import json
from typing import Optional, Dict, Any
from app.core.redis import redis_manager
from app.core.logging import logger
from app.core.events.schemas import RealtimeEvent

class EventPublisher:
    """Canonical Event Publisher broadcasting typed real-time events to Redis channels."""

    @staticmethod
    async def publish(
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
    ) -> RealtimeEvent:
        event = RealtimeEvent(
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

        payload_json = event.model_dump_json()

        # Publish to global channel and specific workflow channel
        await redis_manager.publish_event("strtos_events", payload_json)
        if workflow_id:
            await redis_manager.publish_event(f"strtos_events:{workflow_id}", payload_json)
        if organization_id:
            await redis_manager.publish_event(f"strtos_events_org:{organization_id}", payload_json)

        logger.debug(f"Published real-time event '{event_type}' for workflow {workflow_id}")
        return event

event_publisher = EventPublisher()
