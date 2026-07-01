from langchain_core.tools import tool

from skills.registry import get_registry


def make_load_skill_tool(allowed_skills: list[str]):
    """
    Return a ``load_skill`` LangChain tool scoped to *allowed_skills*.

    The tool lets a worker agent fetch the full content of an add-on skill
    on demand, without that content being pre-loaded into every prompt.
    """
    registry = get_registry()
    allowed_set = frozenset(allowed_skills)

    @tool
    def load_skill(skill_name: str) -> str:
        """Load the full instructions for an add-on skill by name.

        Call this only when you need detailed guidance for a specific skill
        listed under 'Available Add-on Skills'.
        """
        if skill_name not in allowed_set:
            available = ", ".join(sorted(allowed_set)) or "(none)"
            return (
                f"Skill '{skill_name}' is not available for this worker. "
                f"Available add-ons: {available}"
            )
        return registry.get_content(skill_name)

    return load_skill
