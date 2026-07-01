from workers.specs import WorkerSpec

# google_genai:gemini-2.5-flash
# openai:gpt-4o-mini

WORKER_CATALOG: dict[str, WorkerSpec] = {
    "planning": WorkerSpec(
        name="planning",
        model_ref="openai:gpt-4o-mini",
        base_prompt=(
            "You are the Planning Worker for V-CEO. "
            "Break complex requests into steps, dependencies, and decision points."
        ),
        preloaded_skills=(
            "task_decomposition",
        ),
        addon_skills=(
            "project_status",
            "stakeholder_management",
        ),
    ),
    "analysis": WorkerSpec(
        name="analysis",
        model_ref="openai:gpt-4o-mini",
        base_prompt=(
            "You are the Analysis Worker for V-CEO. "
            "Reason from evidence, identify root causes, risks, and tradeoffs."
        ),
        preloaded_skills=(
            "project_status",
        ),
        addon_skills=(
            "stakeholder_management",
        ),
    ),
    "synthesis": WorkerSpec(
        name="synthesis",
        model_ref="openai:gpt-4o-mini",
        base_prompt=(
            "You are the Synthesis Worker for V-CEO. "
            "Write concise executive-ready outputs."
        ),
        preloaded_skills=(
            "executive_email",
        ),
        addon_skills=(
            "stakeholder_management",
        ),
    ),
    "action": WorkerSpec(
        name="action",
        model_ref="openai:gpt-4o-mini",
        base_prompt=(
            "You are the Action Worker for V-CEO. "
            "Take actions on external systems to satisfy the director's request."
        ),
        preloaded_skills=(
            "communication_style",    
        ),
        addon_skills=(
            "project_status",
            "executive_email",
        ),
    ),
}