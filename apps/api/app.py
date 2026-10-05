"""Enhanced API with adaptive mission intelligence and richer responses."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.config.base import Config
from core.models import Goal
from core.orchestrator.adaptive_orchestrator import AdaptiveOrchestrator
from core.persistence import PersistentLearning, StateManager

app = FastAPI(
    title="🤖 TITAN AI - Autonomous Mission Executor",
    version="0.2.0",
    description="Live autonomous AI system with adaptive learning and mission intelligence",
)

app.state.config = Config.from_env()
app.state.state_manager = StateManager(app.state.config.state_dir)
app.state.persistent_learning = PersistentLearning(app.state.state_manager)
app.state.orchestrator = AdaptiveOrchestrator.create_default(app.state.state_manager)


class MissionRequest(BaseModel):
    """Request body for mission execution."""

    goal: str
    description: str | None = None
    priority: int = 0


class TaskSummary(BaseModel):
    """Summary of an executed task."""

    title: str
    status: str


class MissionResponse(BaseModel):
    """Response for successful mission execution."""

    goal_id: str
    title: str
    description: str
    status: str
    tasks: list[TaskSummary]
    success_rate: float
    execution_time_seconds: float | None = None


class IntelligenceReport(BaseModel):
    """Mission intelligence performance report."""

    total_missions: int
    successful_missions: int
    overall_success_rate: float
    goal_types_analyzed: int
    learning_progress: dict[str, Any]


class AdaptiveStrategy(BaseModel):
    """Adaptive execution strategy for a mission."""

    strategy: str
    goal_type: str | None = None
    success_rate: float | None = None
    recommendations: list[str]
    improvement_potential: str


@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """Welcome to TITAN AI."""
    return {
        "message": "Welcome to TITAN AI",
        "version": "0.2.0",
        "status": "live and learning",
    }


@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "titan-ai"}


@app.post("/missions", response_model=MissionResponse, tags=["Missions"])
async def create_mission(request: MissionRequest) -> MissionResponse:
    """Execute a new mission through TITAN with adaptive learning.

    TITAN will:
    1. Analyze the goal and select an adaptive strategy
    2. Decompose it into executable tasks
    3. Execute tasks with reasoning and optimization
    4. Learn from outcomes for future improvement
    5. Return detailed execution results
    """
    if not request.goal.strip():
        raise HTTPException(status_code=400, detail="goal is required")

    goal = Goal(
        title=request.goal,
        description=request.description or request.goal,
        priority=request.priority,
    )

    try:
        import time

        start_time = time.time()
        report = await app.state.orchestrator.execute(goal)
        execution_time = time.time() - start_time

        result = {
            "goal_id": goal.id,
            "title": goal.title,
            "description": goal.description,
            "status": goal.status.value,
            "tasks": [
                {"title": task.title, "status": task.status.value}
                for task in report.tasks
            ],
            "success_rate": app.state.orchestrator.success_rate(),
            "execution_time_seconds": execution_time,
        }
        return MissionResponse(**result)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/missions", tags=["Missions"])
async def list_missions() -> dict[str, Any]:
    """Return persisted mission history.

    Shows the last 20 missions executed, including their status and results.
    """
    missions = app.state.state_manager.load_missions(limit=20)
    return {"missions": missions, "total_retrieved": len(missions)}


@app.get("/strategy/{goal_text}", response_model=AdaptiveStrategy, tags=["Intelligence"])
async def get_adaptive_strategy(goal_text: str) -> AdaptiveStrategy:
    """Get an adaptive execution strategy for a goal based on learning history.

    Analyzes past mission patterns and recommends an optimized strategy.
    """
    orchestrator = app.state.orchestrator
    strategy = orchestrator._mission_intelligence.get_adaptive_strategy(goal_text)

    return AdaptiveStrategy(
        strategy=strategy.get("strategy", "default"),
        goal_type=strategy.get("goal_type"),
        success_rate=strategy.get("success_rate"),
        recommendations=strategy.get("recommendations", []),
        improvement_potential=strategy.get("improvement_potential", "unknown"),
    )


@app.get("/intelligence", response_model=IntelligenceReport, tags=["Intelligence"])
async def get_intelligence_report() -> IntelligenceReport:
    """Get TITAN's mission intelligence and learning performance report.

    Shows:
    - Overall success rate across all missions
    - Goal type specific performance
    - Learning progress and improvement trends
    - Recommendations for optimization
    """
    orchestrator = app.state.orchestrator
    report = orchestrator.get_intelligence_report()

    return IntelligenceReport(
        total_missions=report.get("total_missions", 0),
        successful_missions=report.get("successful_missions", 0),
        overall_success_rate=report.get("overall_success_rate", 0.0),
        goal_types_analyzed=report.get("goal_types_analyzed", 0),
        learning_progress=report.get("learning_progress", {}),
    )


@app.get("/stats", tags=["Stats"])
async def get_stats() -> dict[str, Any]:
    """Return execution statistics and system state."""
    return app.state.state_manager.get_statistics()


@app.get("/recommendations", tags=["Intelligence"])
async def get_recommendations() -> dict[str, Any]:
    """Get learning-based optimization recommendations."""
    metrics = app.state.persistent_learning.persist_learning_metrics()
    return {
        "recommendations": metrics.get("recommendations", []),
        "total_experiences": metrics.get("total_experiences", 0),
        "timestamp": metrics.get("timestamp"),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
