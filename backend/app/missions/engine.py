from typing import List, Dict, Any, Tuple
from app.missions.models import (
    MissionModel, MissionStatus, MissionEvaluationStatus, MissionCheckpointDecision
)
from app.missions.schemas import MissionEvaluationResponse

class MissionAutonomyEngine:
    """Evaluates step governance and autonomy requirements."""

    def evaluate_step_autonomy(self, risk_level: str) -> str:
        if risk_level in ["HIGH", "CRITICAL"]:
            return "APPROVAL_REQUIRED"
        elif risk_level == "MEDIUM":
            return "ASSISTED"
        return "AUTONOMOUS"

class MissionCheckpointEngine:
    """Evaluates checkpoint decisions following execution steps."""

    def evaluate_checkpoint(self, progress: float, risk_score: float) -> Tuple[MissionCheckpointDecision, str]:
        if progress >= 100.0:
            return MissionCheckpointDecision.COMPLETE, "Mission target achieved."
        elif risk_score >= 80.0:
            return MissionCheckpointDecision.ESCALATE, "Risk score crossed threshold, escalation required."
        elif progress < 20.0 and risk_score >= 50.0:
            return MissionCheckpointDecision.REPLAN, "Progress lagging forecast, adaptive replanning triggered."
        return MissionCheckpointDecision.CONTINUE, "Mission progressing cleanly on track."

class MissionAdaptationEngine:
    """Handles bounded adaptive replanning (MAX 10% delta)."""

    def apply_bounded_adaptation(self, current_version: str, delta_pct: float) -> Tuple[str, float]:
        bounded_delta = min(10.0, max(0.0, delta_pct))
        parts = current_version.replace("v", "").split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        new_version = f"v{major}.{minor + 1}.0"
        return new_version, bounded_delta

class MissionEvaluationEngine:
    """Calculates progress and evaluates mission status."""

    def evaluate_mission(self, mission: MissionModel) -> MissionEvaluationResponse:
        completed_steps = sum(1 for s in mission.steps if s.status.value == "COMPLETED")
        total_steps = len(mission.steps) or 1
        progress = round((completed_steps / total_steps) * 100.0, 1)

        if progress >= 100.0:
            status = MissionEvaluationStatus.COMPLETED
        elif mission.risk_score >= 70.0:
            status = MissionEvaluationStatus.AT_RISK
        elif progress >= 50.0:
            status = MissionEvaluationStatus.ON_TRACK
        else:
            status = MissionEvaluationStatus.ON_TRACK

        return MissionEvaluationResponse(
            mission_id=mission.id,
            status=status,
            progress_percentage=progress,
            risk_score=mission.risk_score,
            confidence_score=mission.confidence_score,
            summary=f"Mission evaluated as {status.value}. Progress: {progress}%."
        )
