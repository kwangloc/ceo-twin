from skills.registry import get_registry
from workers.specs import WorkerRuntime, WorkerSpec


def build_system_prompt(
    spec: WorkerSpec,
    runtime: WorkerRuntime,
    preloaded: list[str],
) -> str:
    """Build the static system prompt for a worker.

    Preloaded skill content is injected here (always in context).
    Add-on skill descriptions and the load_skill tool are injected
    dynamically by SkillMiddleware on every model call.
    """
    registry = get_registry()
    base = runtime.prompt_override or spec.base_prompt
    preloaded_text = registry.render_skill_content(preloaded) if preloaded else "(none)"

    return f"""{base}

## Preloaded Skills

{preloaded_text}
""".strip()