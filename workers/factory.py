"""
Worker factory with agent caching.

Agents are keyed by (spec_name, model_ref, preloaded_skills, addon_skills, prompt_override).
Identical combinations reuse the same compiled graph rather than rebuilding it every call.
"""

from typing import Any

from langchain.agents import create_agent

from middleware.skill_middleware import build_skill_middleware
from tools.mcp import get_mcp_tools
from workers.model_registry import resolve_model
from workers.prompts import build_system_prompt
from workers.specs import WorkerRuntime, WorkerSpec

_agent_cache: dict[tuple, Any] = {}


def build_worker_agent(spec: WorkerSpec, runtime: WorkerRuntime):
    model_ref = runtime.model_ref or spec.model_ref

    # Preloaded skills are worker defaults from catalog.
    preloaded = tuple(spec.preloaded_skills)
    # Add-ons are runtime-selectable (e.g., chosen by orchestrator).
    addon = tuple(
        dict.fromkeys(list(spec.addon_skills) + list(runtime.addon_skills))
    )

    cache_key = (spec.name, model_ref, preloaded, addon, runtime.prompt_override)

    if cache_key not in _agent_cache:
        system_prompt = build_system_prompt(
            spec, runtime, preloaded=list(preloaded)
        )
        model = resolve_model(model_ref)
        # SkillMiddleware registers the load_skill tool and injects add-on
        # skill descriptions into the system prompt on every model call.
        middleware = [build_skill_middleware(list(addon), list(preloaded))] if addon else []
        _agent_cache[cache_key] = create_agent(
            model,
            tools=get_mcp_tools(),
            system_prompt=system_prompt,
            middleware=middleware,
        )

    return _agent_cache[cache_key]