from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class WorkerSpec:
    name: str
    model_ref: str
    base_prompt: str
    preloaded_skills: tuple[str, ...] = field(default_factory=tuple)
    addon_skills: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class WorkerRuntime:
    model_ref: Optional[str] = None
    prompt_override: Optional[str] = None
    preloaded_skills: tuple[str, ...] = field(default_factory=tuple)
    addon_skills: tuple[str, ...] = field(default_factory=tuple)