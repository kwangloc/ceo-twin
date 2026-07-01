"""
Skill registry — descriptions stay in code; content lives in .md files.

To add a new skill:
  1. Add an entry to ``_SKILL_METADATA`` (name + one-line description).
  2. Create ``skills/content/<name>.md`` with the full instructions.
  No other code changes are needed.
"""

from pathlib import Path
from typing import Optional, TypedDict

_SKILLS_DIR = Path(__file__).parent / "content"


class SkillMeta(TypedDict):
    name: str
    description: str


# Only metadata is kept in code — descriptions are small and always-safe to include.
# Full content is loaded lazily from .md files to avoid bloating every prompt.
_SKILL_METADATA: list[SkillMeta] = [
    {
        "name": "project_status",
        "description": "Analyze blockers, risks, dependencies, and ownership.",
    },
    {
        "name": "communication_style",
        "description": "Adjust tone, style, and format of messages for different audiences.",
    },
    {
        "name": "executive_email",
        "description": "Draft concise, professional executive emails.",
    },
    {
        "name": "stakeholder_management",
        "description": "Map stakeholders and plan communication strategy.",
    },
    {
        "name": "task_decomposition",
        "description": "Break a complex task into steps and dependencies.",
    },
]

_META_BY_NAME: dict[str, SkillMeta] = {m["name"]: m for m in _SKILL_METADATA}


class SkillRegistry:
    def get_description(self, name: str) -> Optional[str]:
        meta = _META_BY_NAME.get(name)
        return meta["description"] if meta else None

    def get_content(self, name: str) -> str:
        """Lazily read skill content from its .md file."""
        path = _SKILLS_DIR / f"{name}.md"
        if not path.exists():
            return f"Skill '{name}' content not found (expected at {path})."
        return path.read_text(encoding="utf-8")

    def render_skill_list(self, names: Optional[list[str]] = None) -> str:
        """Return a markdown bullet list of skill names + descriptions."""
        items = (
            _SKILL_METADATA
            if names is None
            else [_META_BY_NAME[n] for n in names if n in _META_BY_NAME]
        )
        return "\n".join(f"- **{m['name']}**: {m['description']}" for m in items)

    def render_skill_content(self, names: list[str]) -> str:
        """Return the full content of each named skill, concatenated."""
        blocks = [f"## {name}\n\n{self.get_content(name)}" for name in names]
        return "\n\n".join(blocks) if blocks else "(none)"

    def available_names(self) -> list[str]:
        return [m["name"] for m in _SKILL_METADATA]


_registry = SkillRegistry()


def get_registry() -> SkillRegistry:
    return _registry
