from typing import Any, TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from app.agents import ComplianceAgent, DecisionAgent, IntakeAgent, PolicyAgent, RiskAgent
from app.schemas.review import AgentResult, ReviewReport, ReviewRequest, ReviewResponse


class WorkflowState(TypedDict, total=False):
    request: ReviewRequest
    workflow_id: str
    agent_results: list[AgentResult]
    intake_check: dict[str, Any]
    intake_warnings: list[str]
    required_materials: list[str]
    risk_assessment: dict[str, Any]
    risk_score: int
    risk_level: str
    suggested_amount: float
    policy_references: list[dict[str, Any]]
    compliance_warnings: list[str]
    final_decision: str
    summary: str
    decision_reasons: list[str]
    decision_report_generation: dict[str, Any]
    tool_calls: list[dict[str, Any]]


class ReviewWorkflow:
    def __init__(self) -> None:
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(WorkflowState)

        graph.add_node("intake", IntakeAgent().run)
        graph.add_node("risk", RiskAgent().run)
        graph.add_node("policy", PolicyAgent().run)
        graph.add_node("compliance", ComplianceAgent().run)
        graph.add_node("decision", DecisionAgent().run)

        graph.add_edge(START, "intake")
        graph.add_conditional_edges(
            "intake",
            self._route_after_intake,
            {
                "missing_materials": "policy",
                "ready_for_risk": "risk",
            },
        )
        graph.add_edge("risk", "policy")
        graph.add_edge("policy", "compliance")
        graph.add_edge("compliance", "decision")
        graph.add_edge("decision", END)
        return graph.compile()

    def _route_after_intake(self, state: WorkflowState) -> str:
        # Future extension point: add high-risk or compliance-specific branches after risk scoring.
        if state.get("required_materials"):
            return "missing_materials"
        return "ready_for_risk"

    def run(self, request: ReviewRequest) -> ReviewResponse:
        initial_state: WorkflowState = {
            "request": request,
            "workflow_id": str(uuid4()),
            "agent_results": [],
        }
        state = self.graph.invoke(initial_state)
        report = ReviewReport(
            intake_check=state.get("intake_check", {}),
            risk_assessment=state.get("risk_assessment", {}),
            policy_references=state.get("policy_references", []),
            compliance_warnings=state.get("compliance_warnings", []),
            decision_reasons=state.get("decision_reasons", []),
            required_materials=state.get("required_materials", []),
        )
        return ReviewResponse(
            workflow_id=state["workflow_id"],
            final_decision=state["final_decision"],
            risk_level=state["risk_level"],
            risk_score=state["risk_score"],
            suggested_amount=state["suggested_amount"],
            summary=state["summary"],
            agent_results=state["agent_results"],
            report=report,
        )
