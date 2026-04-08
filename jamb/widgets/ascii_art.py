from __future__ import annotations

from textual.widgets import Static

from ..constants import ADULT_FRAMES, JUVENILE_FRAMES, SNAIL_FRAMES


def frames_for(stage: str, specialization: str | None = None) -> list[str]:
    if stage == "adult" and specialization and specialization in ADULT_FRAMES:
        return ADULT_FRAMES[specialization]
    if stage == "juvenile":
        return JUVENILE_FRAMES
    return SNAIL_FRAMES


class SnailArt(Static):
    """Animated snail ASCII art that alternates between frames."""

    def __init__(self, stage: str = "hatchling", specialization: str | None = None, **kwargs) -> None:
        self._frame_idx = 0
        self._frames = frames_for(stage, specialization)
        super().__init__(self._frames[0], **kwargs)

    def set_stage(self, stage: str, specialization: str | None = None) -> None:
        self._frames = frames_for(stage, specialization)
        self._frame_idx = 0
        self.update(self._frames[0])

    def next_frame(self) -> None:
        self._frame_idx = (self._frame_idx + 1) % len(self._frames)
        self.update(self._frames[self._frame_idx])
