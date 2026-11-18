from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Stage:
    name: str
    planned_sec: int


DEFAULT_STAGES: tuple[Stage, ...] = (
    Stage("pitch", 300),
    Stage("qa", 180),
    Stage("feedback", 60),
)


def stage_names(stages: tuple[Stage, ...] = DEFAULT_STAGES) -> list[str]:
    return [s.name for s in stages]


def planned_seconds(name: str, stages: tuple[Stage, ...] = DEFAULT_STAGES) -> int:
    for stage in stages:
        if stage.name == name:
            return stage.planned_sec
    raise KeyError(name)


def next_stage(name: str | None, stages: tuple[Stage, ...] = DEFAULT_STAGES) -> str | None:
    names = stage_names(stages)
    if name is None:
        return names[0]
    index = names.index(name)
    return names[index + 1] if index + 1 < len(names) else None


def remaining_seconds(planned_sec: int, started_at: datetime, now: datetime) -> int:
    elapsed = (now - started_at).total_seconds()
    return max(0, int(planned_sec - elapsed))


def is_expired(planned_sec: int, started_at: datetime, now: datetime) -> bool:
    return remaining_seconds(planned_sec, started_at, now) == 0
