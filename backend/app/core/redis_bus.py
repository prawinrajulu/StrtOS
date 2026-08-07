import asyncio
import json
from typing import AsyncGenerator, Dict, Any, List

class RedisEventBus:
    """
    Redis Ready Pub/Sub Event Bus.
    Fallback to in-memory async queues for non-blocking local operation.
    """
    def __init__(self):
        self.subscribers: List[asyncio.Queue] = []
        self.history: List[Dict[str, Any]] = []

    async def publish(self, event_type: str, data: Dict[str, Any]):
        message = {"type": event_type, "data": data}
        self.history.append(message)
        for queue in list(self.subscribers):
            try:
                await queue.put(message)
            except Exception:
                pass

    async def subscribe(self) -> AsyncGenerator[Dict[str, Any], None]:
        queue = asyncio.Queue()
        self.subscribers.append(queue)
        try:
            # Replay current history state first
            for item in self.history[-10:]:
                yield item
            while True:
                msg = await queue.get()
                yield msg
        finally:
            if queue in self.subscribers:
                self.subscribers.remove(queue)

event_bus = RedisEventBus()
