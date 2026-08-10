from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.memory.models import MemoryRecordModel, MemoryType, OutcomeStatus
from app.memory.schemas import (
    MemoryRecordCreate, MemoryRecordUpdate, MemoryRecordResponse,
    MemoryListResponse, OutcomeSubmissionRequest, OutcomeResponse
)
from app.memory.repository import MemoryRepository
from app.memory.retrieval import MemoryRetrievalEngine
from app.memory.outcome_engine import evaluate_outcome_variance, extract_deterministic_lesson
from app.core.events.publisher import event_publisher
from app.core.logging import logger

class MemoryService:
    """Core Memory Management Service maintaining tenant isolation, memory scoring, and outcome recording."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = MemoryRepository(session)
        self.retrieval_engine = MemoryRetrievalEngine(session)

    async def create_memory(
        self,
        payload: MemoryRecordCreate,
        org_id: str,
        creator_id: Optional[str] = None
    ) -> MemoryRecordResponse:
        memory = MemoryRecordModel(
            organization_id=org_id,
            client_id=payload.client_id,
            workflow_id=payload.workflow_id,
            report_id=payload.report_id,
            approval_id=payload.approval_id,
            memory_type=payload.memory_type,
            title=payload.title.strip(),
            content=payload.content,
            structured_data=payload.structured_data or {},
            source=payload.source or "system",
            source_type=payload.source_type or "internal",
            confidence_score=payload.confidence_score,
            importance_score=payload.importance_score,
            outcome_status=payload.outcome_status,
            created_by=creator_id,
            occurred_at=payload.occurred_at or datetime.now(timezone.utc),
            expires_at=payload.expires_at,
            extra_metadata=payload.extra_metadata or {}
        )

        created = await self.repo.create(memory)
        await self.session.commit()
        await self.session.refresh(created)

        # Real-time Event
        await event_publisher.publish(
            event_type="memory.created",
            workflow_id=created.workflow_id,
            organization_id=org_id,
            status=created.outcome_status.value,
            metadata={"memory_id": created.id, "memory_type": created.memory_type.value}
        )

        return MemoryRecordResponse.model_validate(created)

    async def get_memory(self, memory_id: str, org_id: str) -> MemoryRecordResponse:
        memory = await self.repo.get_by_id_and_org(memory_id, org_id)
        if not memory:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory record not found.")
        return MemoryRecordResponse.model_validate(memory)

    async def list_memories(
        self,
        org_id: str,
        page: int = 1,
        page_size: int = 20,
        client_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        outcome_status: Optional[OutcomeStatus] = None,
        search: Optional[str] = None
    ) -> MemoryListResponse:
        skip = (page - 1) * page_size
        memories, total = await self.repo.list_by_org(
            org_id=org_id,
            client_id=client_id,
            workflow_id=workflow_id,
            memory_type=memory_type,
            outcome_status=outcome_status,
            search=search,
            skip=skip,
            limit=page_size
        )
        dtos = [MemoryRecordResponse.model_validate(m) for m in memories]
        return MemoryListResponse(memories=dtos, total=total, page=page, page_size=page_size)

    async def retrieve_memories_for_context(
        self,
        org_id: str,
        client_id: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 5
    ) -> List[MemoryRecordResponse]:
        results = await self.retrieval_engine.retrieve_relevant_memories(
            organization_id=org_id,
            client_id=client_id,
            query=query,
            limit=limit
        )
        dtos = []
        for mem, score in results:
            dto = MemoryRecordResponse.model_validate(mem)
            dto.relevance_score = score
            dtos.append(dto)
        return dtos

    async def submit_outcome(
        self,
        payload: OutcomeSubmissionRequest,
        org_id: str,
        creator_id: Optional[str] = None
    ) -> OutcomeResponse:
        # Evaluate variance
        eval_res = evaluate_outcome_variance(
            predicted_value=payload.predicted_value,
            actual_value=payload.actual_value,
            metric_name=payload.metric_name,
            unit=payload.unit
        )

        # 1. Create OUTCOME memory
        outcome_mem = MemoryRecordModel(
            organization_id=org_id,
            client_id=payload.client_id,
            workflow_id=payload.workflow_id,
            memory_type=MemoryType.OUTCOME,
            title=f"Measured Outcome: {payload.metric_name}",
            content=f"Predicted {payload.predicted_value}{payload.unit} vs Actual {payload.actual_value}{payload.unit}. Notes: {payload.notes or 'None'}",
            structured_data={
                "metric_name": payload.metric_name,
                "predicted_value": payload.predicted_value,
                "actual_value": payload.actual_value,
                "unit": payload.unit,
                "absolute_variance": eval_res["absolute_variance"],
                "percentage_variance": eval_res["percentage_variance"],
                "measurement_period": payload.measurement_period
            },
            source="outcome_submission",
            confidence_score=95.0,
            importance_score=80.0,
            outcome_status=eval_res["outcome_status"],
            created_by=creator_id
        )
        created_outcome = await self.repo.create(outcome_mem)

        # 2. Extract and create LESSON memory if meaningful
        lesson_str = extract_deterministic_lesson(
            metric_name=payload.metric_name,
            predicted_value=payload.predicted_value,
            actual_value=payload.actual_value,
            unit=payload.unit,
            outcome_status=eval_res["outcome_status"],
            pct_var=eval_res["percentage_variance"]
        )

        lesson_mem = MemoryRecordModel(
            organization_id=org_id,
            client_id=payload.client_id,
            workflow_id=payload.workflow_id,
            memory_type=MemoryType.LESSON,
            title=f"Learned Signal: {payload.metric_name} Calibration",
            content=lesson_str,
            structured_data={
                "source_outcome_id": created_outcome.id,
                "percentage_variance": eval_res["percentage_variance"]
            },
            source="lesson_engine",
            confidence_score=90.0,
            importance_score=85.0,
            outcome_status=eval_res["outcome_status"],
            created_by=creator_id
        )
        created_lesson = await self.repo.create(lesson_mem)

        await self.session.commit()

        # Real-time Events
        await event_publisher.publish(
            event_type="outcome.recorded",
            workflow_id=payload.workflow_id,
            organization_id=org_id,
            status=eval_res["outcome_status"].value,
            metadata={"metric_name": payload.metric_name, "percentage_variance": eval_res["percentage_variance"]}
        )
        await event_publisher.publish(
            event_type="lesson.created",
            workflow_id=payload.workflow_id,
            organization_id=org_id,
            status=eval_res["outcome_status"].value,
            metadata={"lesson_id": created_lesson.id, "summary": lesson_str}
        )

        return OutcomeResponse(
            outcome_memory_id=created_outcome.id,
            lesson_memory_id=created_lesson.id,
            metric_name=payload.metric_name,
            predicted_value=payload.predicted_value,
            actual_value=payload.actual_value,
            unit=payload.unit,
            absolute_variance=eval_res["absolute_variance"],
            percentage_variance=eval_res["percentage_variance"],
            outcome_status=eval_res["outcome_status"],
            lesson_summary=lesson_str
        )
