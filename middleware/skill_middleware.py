from collections.abc import Callable, Coroutine
from typing import Any, Sequence

from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool

from skills.registry import get_registry


def build_skill_middleware(
    addon_skill_names: Sequence[str],
    preloaded_skill_names: Sequence[str] = (),
) -> AgentMiddleware:
    """
    Create a SkillMiddleware instance scoped to *addon_skill_names*.

    The middleware does two things on every model call:
    1. Injects a bullet-list of available add-on skill descriptions into the
       system prompt (so the model knows what skills exist without loading them).
    2. Provides a ``load_skill`` tool that fetches the full content of any
       add-on skill on demand.
    """
    registry = get_registry()
    allowed = frozenset(addon_skill_names)
    preloaded = frozenset(preloaded_skill_names)

    @tool
    def load_skill(skill_name: str) -> str:
        """Load the full instructions for an add-on skill by name.

        Use only when you need detailed guidance for a specific skill listed
        under 'Available Add-on Skills'.
        """
        if skill_name in preloaded:
            return (
                f"Skill '{skill_name}' is already preloaded in system prompt. "
                "Use it directly; no load_skill call is needed."
            )

        if skill_name not in allowed:
            available = ", ".join(sorted(allowed)) or "(none)"
            return (
                f"Skill '{skill_name}' is not available for this worker. "
                f"Available add-ons: {available}"
            )
        return registry.get_content(skill_name)

    class SkillMiddleware(AgentMiddleware):
        # The tool is registered here so create_agent picks it up automatically.
        tools = [load_skill]

        def __init__(self) -> None:
            self.skills_prompt = registry.render_skill_list(list(allowed))

        def wrap_model_call(
            self,
            request: ModelRequest,
            handler: Callable[[ModelRequest], ModelResponse],
        ) -> ModelResponse:
            """Append add-on skill descriptions to the system prompt each call."""
            modified_request = self._inject_skills(request)
            return handler(modified_request)

        async def awrap_model_call(
            self,
            request: ModelRequest,
            handler: Callable[[ModelRequest], Coroutine[Any, Any, ModelResponse]],
        ) -> ModelResponse:
            """Async variant — same injection, async handler."""
            modified_request = self._inject_skills(request)
            return await handler(modified_request)

        def _inject_skills(self, request: ModelRequest) -> ModelRequest:
            """Return a copy of *request* with the skills addendum appended."""
            skills_addendum = (
                "\n\n## Available Add-on Skills\n\n"
                f"{self.skills_prompt}\n\n"
                "Call load_skill when you need the full instructions for a skill."
            )
            new_content = list(request.system_message.content_blocks) + [
                {"type": "text", "text": skills_addendum}
            ]
            new_system_message = SystemMessage(content=new_content)
            return request.override(system_message=new_system_message)

    return SkillMiddleware()