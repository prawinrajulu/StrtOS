from typing import List, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.memory.models import MemoryRecordModel, MemoryType, OutcomeStatus
from app.clients.repository import ClientRepository

class MemoryRetrievalEngine:
    """
    Deterministic Memory Retrieval Engine indexing, scoring, and ranking historical client context,
    decisions, strategies, outcomes, and lessons without external vector databases.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.client_repo = ClientRepository(session)

    async def retrieve_relevant_memories(
        self,
        organization_id: str,
        client_id: Optional[str] = None,
        query: Optional[str] = None,
        industry: Optional[str] = None,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10
    ) -> List[Tuple[MemoryRecordModel, float]]:
        # 1. Base query scoped strictly to organization_id
        stmt = select(MemoryRecordModel).where(MemoryRecordModel.organization_id == organization_id)

        if memory_types and len(memory_types) > 0:
            stmt = stmt.where(MemoryRecordModel.memory_type.in_(memory_types))

        # Fetch candidate records for deterministic scoring
        results = await self.session.execute(stmt.limit(100))
        candidates = list(results.scalars().all())

        if not candidates:
            return []

        # Resolve client industry if not explicitly passed
        target_industry = industry
        if client_id and not target_industry:
            client = await self.client_repo.get_by_id_and_org(client_id, organization_id)
            if client and client.industry:
                target_industry = client.industry

        # Parse query keywords
        query_words = set()
        if query:
            query_words = {w.lower() for w in query.replace(",", " ").split() if len(w) > 3}

        now = datetime.now(timezone.utc)
        scored_memories: List[Tuple[MemoryRecordModel, float]] = []

        for mem in candidates:
            score = 0.0

            # Rule A: Client Match
            if client_id and mem.client_id == client_id:
                score += 40.0

            # Rule B: Industry Match
            mem_industry = (mem.extra_metadata or {}).get("industry")
            if target_industry and mem_industry and target_industry.lower() == str(mem_industry).lower():
                score += 20.0

            # Rule C: Keyword Overlap
            if query_words:
                text_content = f"{mem.title} {mem.content or ''}".lower()
                overlap = sum(1 for word in query_words if word in text_content)
                score += min(15.0, overlap * 3.0)

            # Rule D: Recency Factor
            created_at = mem.created_at or now
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            days_old = (now - created_at).days
            if days_old <= 30:
                score += 10.0
            elif days_old <= 90:
                score += 5.0

            # Rule E: Confidence & Importance Score Factor
            score += ((mem.importance_score or 50.0) * 0.1) + ((mem.confidence_score or 90.0) * 0.05)

            # Rule F: Outcome Status Value
            if mem.outcome_status == OutcomeStatus.SUCCESS:
                score += 5.0
            elif mem.outcome_status == OutcomeStatus.FAILED:
                score += 3.0  # High warning/learning relevance
            elif mem.outcome_status == OutcomeStatus.PARTIAL:
                score += 2.0

            final_score = round(score, 1)
            scored_memories.append((mem, final_score))

        # Sort by relevance score descending
        scored_memories.sort(key=lambda x: x[1], reverse=True)

        return scored_memories[:limit]
