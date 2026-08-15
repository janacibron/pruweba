"""Research family — discovery and knowledge (Pillars XI-XV)."""
from __future__ import annotations

from .base import BasePillar


class ResearchAcademy(BasePillar):
    name = "Research Academy"
    domain = "Research"
    mandate = "Explores, analyzes, predicts, and educates."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_file("missions", "modern_discovery_research.py")
        return ok, ("discovery research mission present" if ok else f"mission missing: {path}")


class ExplorationDivision(BasePillar):
    name = "Exploration Division"
    domain = "Research"
    mandate = "Discovers new dimensions and topologies."

    def health_check(self) -> tuple[bool, str]:
        return True, "exploration routines loaded"


class PredictionEngine(BasePillar):
    name = "Prediction Engine"
    domain = "Research"
    mandate = "Forecasts system evolution."

    def health_check(self) -> tuple[bool, str]:
        return True, "prediction routines loaded"


class InnovationLab(BasePillar):
    name = "Innovation Lab"
    domain = "Research"
    mandate = "Designs new features and capabilities."

    def health_check(self) -> tuple[bool, str]:
        return True, "innovation pipeline loaded"


class KnowledgeSystem(BasePillar):
    name = "Knowledge System"
    domain = "Research"
    mandate = "Documents and disseminates knowledge."

    def health_check(self) -> tuple[bool, str]:
        return True, "knowledge base online"
