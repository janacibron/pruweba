"""Intelligence family — data and adaptation (Pillars XXI-XXV)."""
from __future__ import annotations

from .base import BasePillar


class DataSourceRegistry(BasePillar):
    name = "Data Source Registry"
    domain = "Intelligence"
    mandate = "Registers and manages pipeline data sources."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_dir("pipeline", "data_sources")
        return ok, ("data sources present" if ok else f"data sources missing: {path}")


class ConfidenceScorer(BasePillar):
    name = "Confidence Scorer"
    domain = "Intelligence"
    mandate = "Scores evidence confidence deterministically."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_file("pipeline", "confidence.py")
        return ok, ("confidence scorer present" if ok else f"confidence scorer missing: {path}")


class CouplingAnalyzer(BasePillar):
    name = "Coupling Analyzer"
    domain = "Intelligence"
    mandate = "Measures coupling between components."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_file("pipeline", "coupling.py")
        return ok, ("coupling analyzer present" if ok else f"coupling analyzer missing: {path}")


class PlanningEngine(BasePillar):
    name = "Planning Engine"
    domain = "Intelligence"
    mandate = "Builds execution plans."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_file("pipeline", "planning_engine.py")
        return ok, ("planning engine present" if ok else f"planning engine missing: {path}")


class WorkerCoordinator(BasePillar):
    name = "Worker Coordinator"
    domain = "Intelligence"
    mandate = "Coordinates parallel workers."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_file("pipeline", "worker_coordinator.py")
        return ok, ("worker coordinator present" if ok else f"worker coordinator missing: {path}")
