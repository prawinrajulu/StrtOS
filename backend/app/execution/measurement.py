from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.execution.models import ActionModel
from app.predictions.repository import PredictionRepository
from app.predictions.accuracy import evaluate_prediction_accuracy
from app.memory.service import MemoryService
from app.memory.schemas import MemoryRecordCreate
from app.memory.models import MemoryType, OutcomeStatus
from app.core.events.publisher import event_publisher
from app.core.logging import logger

class ClosedLoopOptimizationEngine:
    """
    Closed-Loop Optimization Engine evaluating action execution outcomes against
    v1.2 predictions, computing accuracy metrics, and persisting learned lessons to v1.1 Memory.
    """

    @classmethod
    async def process_closed_loop_measurement(
        cls,
        action: ActionModel,
        actual_metric_value: float,
        session: AsyncSession
    ) -> Dict[str, Any]:
        p_repo = PredictionRepository(session)
        mem_service = MemoryService(session)

        pred = None
        if action.prediction_id:
            pred = await p_repo.get_by_id_and_org(action.prediction_id, action.organization_id)

        predicted_val = pred.predicted_value if pred else 3.5
        metric_name = pred.metric_name if pred else "ROAS"

        # 1. Prediction Accuracy Assessment
        acc_res = evaluate_prediction_accuracy(
            predicted_value=predicted_val,
            actual_value=actual_metric_value,
            metric_name=metric_name
        )

        # 2. Map Outcome Status
        pct_err = acc_res["percentage_error"]
        if pct_err <= 10.0:
            outcome_status = OutcomeStatus.SUCCESS
        elif pct_err <= 30.0:
            outcome_status = OutcomeStatus.PARTIAL
        else:
            outcome_status = OutcomeStatus.FAILED

        # 3. Create Memory Record (LESSON & OUTCOME)
        lesson_title = f"Closed-Loop Optimization: {action.name}"
        lesson_content = f"{acc_res['lesson_summary']} Action '{action.name}' completed with actual {metric_name} = {actual_metric_value} (Predicted: {predicted_val})."

        mem_record = await mem_service.create_memory(
            payload=MemoryRecordCreate(
                client_id=action.client_id,
                workflow_id=action.workflow_id,
                approval_id=action.approval_id,
                memory_type=MemoryType.LESSON,
                title=lesson_title,
                content=lesson_content,
                confidence_score=acc_res["accuracy_score"],
                importance_score=85.0,
                outcome_status=outcome_status,
                extra_metadata={
                    "action_id": action.id,
                    "prediction_id": action.prediction_id,
                    "predicted_value": predicted_val,
                    "actual_value": actual_metric_value,
                    "percentage_error": pct_err,
                    "accuracy_score": acc_res["accuracy_score"]
                }
            ),
            org_id=action.organization_id,
            creator_id=action.created_by
        )

        # 4. SSE Telemetry
        await event_publisher.publish(
            event_type="outcome.recorded",
            workflow_id=action.workflow_id,
            organization_id=action.organization_id,
            status=outcome_status.value,
            metadata={"action_id": action.id, "accuracy_score": acc_res["accuracy_score"]}
        )

        await event_publisher.publish(
            event_type="optimization.completed",
            workflow_id=action.workflow_id,
            organization_id=action.organization_id,
            status="COMPLETED",
            metadata={"lesson_memory_id": mem_record.id, "accuracy_status": acc_res["accuracy_status"]}
        )

        return {
            "action_id": action.id,
            "prediction_id": action.prediction_id,
            "metric_name": metric_name,
            "predicted_value": predicted_val,
            "actual_value": actual_metric_value,
            "accuracy_score": acc_res["accuracy_score"],
            "percentage_error": pct_err,
            "outcome_status": outcome_status.value,
            "lesson_memory_id": mem_record.id,
            "lesson_summary": lesson_content
        }
