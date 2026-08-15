"""Base class and helpers for the 30 Ground Truth Sovereign Pillars."""
from __future__ import annotations

import sys
from pathlib import Path

PIPELINE_ROOT = Path(r"C:\Users\Jan\Documents\Idea-to-Execution-v2")


def load_ground_truth():
    """Import the pipeline's ground_truth core (lazy, path-bridged)."""
    if str(PIPELINE_ROOT) not in sys.path:
        sys.path.insert(0, str(PIPELINE_ROOT))
    import ground_truth  # noqa: PLC0415

    return ground_truth


class BasePillar:
    """Shared contract: name, domain, mandate, and health_check()."""

    name = "Unnamed Pillar"
    domain = "Sovereign"
    mandate = ""

    def health_check(self) -> tuple[bool, str]:
        """Return (ok: bool, detail: str). Override in subclasses."""
        return True, f"{self.name} initialized"

    @staticmethod
    def pipeline_file(*parts: str) -> tuple[bool, str]:
        path = PIPELINE_ROOT.joinpath(*parts)
        return path.is_file(), str(path)

    @staticmethod
    def pipeline_dir(*parts: str) -> tuple[bool, str]:
        path = PIPELINE_ROOT.joinpath(*parts)
        return path.is_dir(), str(path)

    def __repr__(self) -> str:
        return f"<SovereignPillar {self.name} ({self.domain})>"
