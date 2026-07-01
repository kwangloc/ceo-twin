"""
LLM-based iterative orchestrator using structured output.

The orchestrator is called repeatedly. On each turn, it decides whether to:
1) run another worker (with optional retrieval first), or
2) end the workflow.
"""

from typing import Literal

from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

from config import ORCHESTRATOR_MODEL
from skills.registry import get_registry
from state import State
from workers.catalog import WORKER_CATALOG
import os
from dotenv import load_dotenv

load_dotenv()

_AVAILABLE_SOURCES = ["graph", "vector", "memory"]
_DEFAULT_ROLE = "director_twin"


class OrchestratorDecision(BaseModel):
    reasoning: str = Field(description="Brief reasoning for the routing decision")
    worker_type: Literal["planning", "analysis", "synthesis", "action", "none"] = Field(
        description="Which worker to run next. Use 'none' when should_end is true."
    )
    should_end: bool = Field(
        description="Whether the workflow should end now"
    )
    worker_task: str = Field(
        default="",
        description=(
            "Execution brief for the selected worker in THIS turn only. "
            "Be specific, scoped, and avoid redoing completed work."
        ),
    )
    need_retrieval: bool = Field(
        description="Whether to run retrieval before the selected worker"
    )
    retrieval_sources: list[str] = Field(
        default_factory=list,
        description=(
            f"Which sources to query. Options: {', '.join(_AVAILABLE_SOURCES)}. "
            "Leave empty if need_retrieval is false."
        ),
    )
    addon_skills: list[str] = Field(
        default_factory=list,
        description="Skills the worker can optionally load via the load_skill tool",
    )
    final_response: str = Field(
        default="",
        description=(
            "User-facing response for this turn when should_end is true. "
            "Leave empty when should_end is false."
        ),
    )


_ROLE_INSTRUCTIONS = {
    "director_twin": """You are the V-CEO Orchestrator acting as the Director's digital twin.
Treat incoming messages as communications from employees, stakeholders, or collaborators directed to the Director via Slack. Your role is to determine how the Director would respond, delegate, decide, or act based on the available context, policies, and knowledge.
Understand the sender's intent, the current workflow state, and the level of authority required. Decide the next best action while staying within delegated permissions.
When responding, act on behalf of the Director rather than as an assistant supporting the Director. Use the Director's communication style, priorities, and decision-making principles.
Do only what is requested or reasonably implied by the request. Do not expand scope, make unapproved decisions, or take actions beyond your authority. Escalate to the Director when confidence is low, context is insufficient, or the request exceeds delegated authority.

Communication style:
- Respond as a real Vietnamese director in a workplace conversation: natural, concise, professional, and respectful.
- Use appropriate first-person pronouns (e.g. "em", "anh") when speaking on the Director's behalf. Do not sound like an AI assistant, customer support agent, or automated system.
- Prefer direct Slack-style communication: answer first, add only necessary context, and avoid generic assistance phrases or overly formal language.
Example:
Employee: "Project V-CEO khi nào tới hạn triển khai Neo4j staging vậy anh?"
Good answer: "Neo4j staging due là 1/7 em nhé. Anh sẽ nhắc team chuẩn bị trước 1 tuần."

""",
    "assistant": """You are the V-CEO Orchestrator acting as the Director's executive assistant.
Treat incoming messages as requests from the Director seeking support, information, analysis, planning, drafting, or execution assistance. Your role is to help the Director achieve their objectives by coordinating the appropriate reasoning, knowledge, and actions.
Understand the Director's intent, the current workflow state, and the desired outcome. Determine the next best step and provide the support needed to move the work forward.
When responding, assist the Director rather than acting on the Director's behalf. Unless explicitly requested, do not impersonate the Director, make commitments in the Director's name, or communicate as though you are the Director.
Do only what is requested or reasonably implied by the request. Do not expand scope unnecessarily or take autonomous actions beyond the Director's intent.

Communication style:
- Respond as a professional executive assistant supporting the Director. Be concise, clear, proactive, and business-oriented.
- Address the user directly as the Director. Do not speak on the Director's behalf unless explicitly asked to draft a message or role-play.
- Prefer executive-style communication: provide the answer first, then relevant context, recommendations, risks, or next actions. Avoid unnecessary pleasantries and filler text.
Example:
Director: "Project V-CEO khi nào tới hạn triển khai Neo4j staging vậy?"
Good answer:
"Neo4j staging có hạn triển khai vào ngày 1/7."
""",
}


_SYSTEM_PROMPT_TEMPLATE = """\
{role_instructions}

Worker types:
- planning: Breaks complex goals into steps, timelines, and dependencies
- analysis: Reasons from evidence; identifies root causes, risks, and tradeoffs
- synthesis: Writes executive-ready documents, emails, and summaries
- action: Interacts with external systems (Jira, Slack, etc.)

Retrieval sources:
- graph: Knowledge graph (entity relationships, project dependencies, owners)
- vector: Semantic search over documents, notes, and meeting transcripts
- memory: Director's prior context, preferences, and conversation history
Note: vector and graph must be used together for best results

Available skills:
{skill_list}
- Missing skills do not imply missing capability; workers may achieve goals through reasoning and tool chaining.

Worker preloaded skills (fixed by catalog, informational):
{worker_preloaded_skills}

Completed worker runs so far:
{completed_runs}

Guidelines:
- Skip retrieval for general reasoning or writing tasks that need no external data.
- Select retrieval sources likely to contain relevant information.
- Do NOT decide preloaded skills. Preloaded skills are fixed by the worker catalog.
- Decide only add-on skills that may be optionally loaded via load_skill.
- Multi-worker is allowed. Typical patterns: analysis -> synthesis, planning -> action, analysis -> action.
- Use completed worker outputs to avoid repeating already-finished steps.
- worker_task must be scoped to one step (not the full end-to-end request).
- When should_end=false, provide a precise worker_task for this turn.
- should_end indicates whether orchestration is complete.
- If a worker must execute, set should_end=false.
- If worker_type != 'none', should_end MUST be false.
- Set should_end=true only when no further worker execution is required.
- When should_end=true, set worker_type='none' and worker_task=''.
- When should_end=true, also provide final_response as the exact message to send back to the director this turn.
- When should_end=false, set final_response=''.
"""


def _render_worker_preloaded_skills() -> str:
    lines: list[str] = []
    for name, spec in WORKER_CATALOG.items():
        preloaded = ", ".join(spec.preloaded_skills) if spec.preloaded_skills else "(none)"
        lines.append(f"- {name}: {preloaded}")
    return "\n".join(lines)


def _render_completed_runs(state: State) -> str:
    def _content_to_text(value) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            parts: list[str] = []
            for item in value:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                else:
                    parts.append(str(item))
            return "\n".join(p for p in parts if p)
        return str(value)

    runs = state.get("worker_runs", [])
    if not runs:
        return "(none)"
    lines: list[str] = []
    for idx, run in enumerate(runs[-4:], start=max(1, len(runs) - 3)):
        worker = run.get("worker", "?")
        out = _content_to_text(run.get("output", ""))
        # Keep substantial context so the orchestrator can detect completed work.
        preview = out.strip()[:2000]
        lines.append(f"{idx}. {worker}:\n{preview}")
    return "\n".join(lines)


def _make_llm():
    llm = init_chat_model(ORCHESTRATOR_MODEL)
    return llm.with_structured_output(OrchestratorDecision)


_llm = _make_llm()


def _resolve_final_response(state: State, decision: OrchestratorDecision) -> str:
    """Resolve a user-facing response for the current turn."""
    final_response = (decision.final_response or "").strip()
    if final_response:
        return final_response

    worker_output = str(state.get("worker_output", "")).strip()
    if worker_output:
        return worker_output

    reasoning = str(decision.reasoning or "").strip()
    if reasoning:
        return reasoning

    return "No additional action required for this turn."


def orchestrator_node(state: State) -> dict:
    turn_count = int(state.get("turn_count", 0)) + 1
    # Safety stop against accidental infinite loops.
    if turn_count > int(os.getenv("ORCHESTRATOR_MAX_TURNS", 10)):
        return {
            "turn_count": turn_count,
            "next_step": "end",
            "orchestrator_decision": {
                "reasoning": "Reached orchestration turn limit.",
                "worker_type": "none",
                "should_end": True,
                "worker_task": "",
                "need_retrieval": False,
                "retrieval_sources": [],
                "addon_skills": [],
                "final_response": "Reached orchestration turn limit.",
            },
        }

    registry = get_registry()
    skill_list = registry.render_skill_list()
    worker_preloaded_skills = _render_worker_preloaded_skills()
    completed_runs = _render_completed_runs(state)
    role = str(state.get("conversation_role", _DEFAULT_ROLE)).strip() or _DEFAULT_ROLE
    role_instructions = _ROLE_INSTRUCTIONS.get(role, _ROLE_INSTRUCTIONS[_DEFAULT_ROLE])

    system = _SYSTEM_PROMPT_TEMPLATE.format(
        role_instructions=role_instructions,
        skill_list=skill_list,
        worker_preloaded_skills=worker_preloaded_skills,
        completed_runs=completed_runs,
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": state["user_request"]},
    ]

    decision: OrchestratorDecision = _llm.invoke(messages)
    should_end = bool(decision.should_end) or decision.worker_type == "none"
    if should_end:
        decision_payload = decision.model_dump()
        decision_payload["final_response"] = _resolve_final_response(state, decision)
        return {
            "turn_count": turn_count,
            "orchestrator_decision": decision_payload,
            "next_step": "end",
        }

    next_step = "retrieve" if decision.need_retrieval else "worker"

    return {
        "turn_count": turn_count,
        "orchestrator_decision": decision.model_dump(),
        "current_worker_type": decision.worker_type,
        "current_worker_task": decision.worker_task,
        "current_addon_skills": decision.addon_skills,
        "next_step": next_step,
    }