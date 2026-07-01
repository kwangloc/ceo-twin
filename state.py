from typing import Literal, Optional, TypedDict


class OrchestratorDecision(TypedDict):
    """Structured routing decision produced by the LLM orchestrator."""

    reasoning: str
    worker_type: Literal["planning", "analysis", "synthesis", "action", "none"]
    should_end: bool
    worker_task: str
    need_retrieval: bool
    retrieval_sources: list[str]
    addon_skills: list[str]
    final_response: str


class State(TypedDict, total=False):
    # --- Provided by caller ---
    user_request: str
    conversation_role: Literal["assistant", "director_twin"]
    model_override: Optional[str]   # override the worker model at runtime
    prompt_override: Optional[str]  # override the worker base prompt at runtime

    # --- Set by orchestrator ---
    orchestrator_decision: OrchestratorDecision
    current_worker_type: Literal["planning", "analysis", "synthesis", "action"]
    current_worker_task: str
    current_addon_skills: list[str]
    turn_count: int
    worker_runs: list[dict]
    next_step: Literal["retrieve", "worker", "end"]

    # --- Set by retrieval ---
    context: list[str]

    # --- Set by worker ---
    worker_output: str
