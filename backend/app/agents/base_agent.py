import time
import json
import asyncio
from typing import Dict, Any, List, Optional, Type, Tuple
from abc import ABC, abstractmethod
from pydantic import BaseModel, ValidationError

from app.core.evidence.models import EvidenceItem
from app.core.confidence.engine import calculate_confidence
from app.core.events.publisher import event_publisher
from app.tools.registry import tool_registry
from app.llm.router import llm_router
from app.llm.providers.base_provider import LLMRequest, LLMResponse
from app.core.logging import logger

TOOL_SOURCE_TYPE_MAP = {
    "firecrawl": "website",
    "pagespeed": "api",
    "serper": "search",
    "tavily": "search",
    "google_business": "api",
    "browser": "website",
}

class SpecialistAgentBase(ABC):
    """
    Abstract Base Class for Specialist AI Agents in StrtOS.
    Provides standard lifecycle, evidence collection, confidence computation,
    and event publishing helpers.
    """

    def validate_input(self, validator_obj: Any, payload: Any) -> None:
        """Validates payload using validator object if provided."""
        if hasattr(validator_obj, "validate_input"):
            validator_obj.validate_input(payload)

    async def publish_event(
        self,
        event_type: str,
        workflow_id: Optional[str] = None,
        task_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        organization_id: Optional[str] = None,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        tool_name: Optional[str] = None,
        token_usage: Optional[int] = None,
        latency_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publishes typed real-time event to EventPublisher."""
        await event_publisher.publish(
            event_type=event_type,
            workflow_id=workflow_id,
            task_id=task_id,
            agent_name=agent_name,
            organization_id=organization_id,
            status=status,
            progress=progress,
            message=message,
            provider=provider,
            model=model,
            tool_name=tool_name,
            token_usage=token_usage,
            latency_ms=latency_ms,
            metadata=metadata or {}
        )

    async def run_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        finding_desc: str,
        workflow_id: Optional[str] = None,
        task_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> Tuple[EvidenceItem, Dict[str, Any]]:
        """
        Executes a registered tool via ToolRegistry, logs evidence, and emits real-time events.
        """
        start_t = time.time()
        await self.publish_event(
            event_type="agent.tool.started",
            workflow_id=workflow_id,
            task_id=task_id,
            agent_name=agent_name,
            organization_id=organization_id,
            tool_name=tool_name,
            status="RUNNING"
        )

        try:
            tool_res = await tool_registry.execute_tool(tool_name, params)
            latency_ms = int((time.time() - start_t) * 1000)
            status = tool_res.get("status", "SUCCESS")
            
            if status == "SUCCESS":
                stype = TOOL_SOURCE_TYPE_MAP.get(tool_name, "api")
                url = tool_res.get("url") or params.get("url")
                evidence_item = EvidenceItem.from_tool_result(
                    finding=finding_desc,
                    source=f"Tool:{tool_name}",
                    source_type=stype,
                    url=url,
                    evidence=tool_res,
                    confidence=100.0
                )
            else:
                evidence_item = EvidenceItem(
                    finding=f"Attempted {finding_desc} via {tool_name} (Tool Unavailable)",
                    source=f"Tool:{tool_name}",
                    source_type="unavailable",
                    url=params.get("url"),
                    evidence=tool_res,
                    confidence=0.0
                )

            await self.publish_event(
                event_type="agent.tool.completed",
                workflow_id=workflow_id,
                task_id=task_id,
                agent_name=agent_name,
                organization_id=organization_id,
                tool_name=tool_name,
                status=status,
                latency_ms=latency_ms
            )

            await self.publish_event(
                event_type="agent.evidence.collected",
                workflow_id=workflow_id,
                task_id=task_id,
                agent_name=agent_name,
                organization_id=organization_id,
                metadata={"finding": evidence_item.finding, "source_type": evidence_item.source_type}
            )

            return evidence_item, tool_res

        except Exception as e:
            latency_ms = int((time.time() - start_t) * 1000)
            logger.error(f"Error executing tool {tool_name}: {e}")
            evidence_item = EvidenceItem(
                finding=f"Tool execution failed for {tool_name}: {str(e)}",
                source=f"Tool:{tool_name}",
                source_type="unavailable",
                url=params.get("url"),
                evidence={"error": str(e)},
                confidence=0.0
            )
            await self.publish_event(
                event_type="agent.tool.completed",
                workflow_id=workflow_id,
                task_id=task_id,
                agent_name=agent_name,
                organization_id=organization_id,
                tool_name=tool_name,
                status="UNAVAILABLE",
                latency_ms=latency_ms,
                metadata={"error": str(e)}
            )
            return evidence_item, {"status": "UNAVAILABLE", "error": str(e)}

    async def run_llm(
        self,
        agent_name: str,
        prompt: str,
        system_prompt: str,
        workflow_id: Optional[str] = None,
        task_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> Tuple[LLMResponse, Dict[str, Any]]:
        """
        Executes LLM Router generation and returns (llm_response, parsed_json_or_dict).
        """
        start_t = time.time()
        await self.publish_event(
            event_type="agent.llm.started",
            workflow_id=workflow_id,
            task_id=task_id,
            agent_name=agent_name,
            organization_id=organization_id,
            status="RUNNING"
        )

        req = LLMRequest(prompt=prompt, system_prompt=system_prompt)
        llm_resp = await llm_router.route_and_generate(agent_name, req)
        latency_ms = int((time.time() - start_t) * 1000)

        # Parse JSON output from LLM content if present
        parsed_data = {}
        if llm_resp.content:
            try:
                # Remove possible markdown block backticks ```json ... ```
                raw_text = llm_resp.content.strip()
                if raw_text.startswith("```"):
                    lines = raw_text.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    raw_text = "\n".join(lines).strip()
                parsed_data = json.loads(raw_text)
            except Exception as e:
                logger.warning(f"Failed to parse LLM response JSON for {agent_name}: {e}")
                parsed_data = {"raw_content": llm_resp.content, "parse_error": str(e)}

        await self.publish_event(
            event_type="agent.llm.completed",
            workflow_id=workflow_id,
            task_id=task_id,
            agent_name=agent_name,
            organization_id=organization_id,
            status=llm_resp.status,
            provider=llm_resp.provider,
            model=llm_resp.model,
            token_usage=llm_resp.total_tokens,
            latency_ms=latency_ms
        )

        return llm_resp, parsed_data

    def compute_confidence(
        self,
        evidence_items: List[EvidenceItem],
        llm_status: str = "SUCCESS",
        has_unavailable_tools: bool = False
    ) -> float:
        """Helper to calculate deterministic confidence score."""
        return calculate_confidence(
            evidence_items=evidence_items,
            llm_status=llm_status,
            has_unavailable_tools=has_unavailable_tools
        )

    async def handle_failure(
        self,
        exc: Exception,
        agent_name: str,
        workflow_id: Optional[str] = None,
        task_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> None:
        """Publishes agent.failed event."""
        logger.error(f"Agent {agent_name} failed: {exc}")
        await self.publish_event(
            event_type="agent.failed",
            workflow_id=workflow_id,
            task_id=task_id,
            agent_name=agent_name,
            organization_id=organization_id,
            status="FAILED",
            metadata={"error": str(exc)}
        )
