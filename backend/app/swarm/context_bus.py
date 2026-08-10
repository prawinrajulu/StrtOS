from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import asyncio

class SharedContextBus:
    """
    Thread-safe, tenant-isolated shared context bus enabling real-time evidence
    and message distribution between specialist agents during a Swarm Session.
    """
    _messages: Dict[str, List[Dict[str, Any]]] = {}
    _evidence: Dict[str, List[Dict[str, Any]]] = {}
    _lock = asyncio.Lock()

    @classmethod
    async def publish_message(cls, swarm_id: str, org_id: str, message: Dict[str, Any]) -> None:
        async with cls._lock:
            key = f"{org_id}:{swarm_id}"
            if key not in cls._messages:
                cls._messages[key] = []
            message["timestamp"] = datetime.now(timezone.utc).isoformat()
            cls._messages[key].append(message)

    @classmethod
    async def get_messages(cls, swarm_id: str, org_id: str, agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
        async with cls._lock:
            key = f"{org_id}:{swarm_id}"
            msgs = cls._messages.get(key, [])
            if agent_name:
                return [m for m in msgs if m.get("source_agent") == agent_name or m.get("target_agent") == agent_name or m.get("target_agent") is None]
            return msgs

    @classmethod
    async def publish_evidence(cls, swarm_id: str, org_id: str, evidence_item: Dict[str, Any]) -> None:
        async with cls._lock:
            key = f"{org_id}:{swarm_id}"
            if key not in cls._evidence:
                cls._evidence[key] = []
            evidence_item["timestamp"] = datetime.now(timezone.utc).isoformat()
            cls._evidence[key].append(evidence_item)

    @classmethod
    async def get_evidence(cls, swarm_id: str, org_id: str) -> List[Dict[str, Any]]:
        async with cls._lock:
            key = f"{org_id}:{swarm_id}"
            return cls._evidence.get(key, [])

    @classmethod
    async def clear_session(cls, swarm_id: str, org_id: str) -> None:
        async with cls._lock:
            key = f"{org_id}:{swarm_id}"
            cls._messages.pop(key, None)
            cls._evidence.pop(key, None)
