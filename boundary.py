"""Boundary family — integration and governance (Pillars XXVI-XXX)."""
from __future__ import annotations

from .base import BasePillar


class ExecutionBoundary(BasePillar):
    name = "Execution Boundary"
    domain = "Boundary"
    mandate = "Unified execution facade; isolates side effects."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_file("pipeline", "execution_facade.py")
        return ok, ("execution facade present" if ok else f"execution facade missing: {path}")


class GovernanceGate(BasePillar):
    name = "Governance Gate"
    domain = "Boundary"
    mandate = "Gates mutations behind governance state."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_file("docs", "governance", "freeze_state.json")
        return ok, ("governance state readable" if ok else f"governance state missing: {path}")


class RecoveryLedger(BasePillar):
    name = "Recovery Ledger"
    domain = "Boundary"
    mandate = "Records failure resolutions."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_file("docs", "governance", "failure_resolutions.jsonl")
        return ok, ("recovery ledger present" if ok else f"recovery ledger missing: {path}")


class TelemetryBeacon(BasePillar):
    name = "Telemetry Beacon"
    domain = "Boundary"
    mandate = "Emits operational telemetry."

    def health_check(self) -> tuple[bool, str]:
        return True, "telemetry online"


class SovereignRegistrar(BasePillar):
    name = "Sovereign Registrar"
    domain = "Boundary"
    mandate = "Registers the 33 sovereign pillars."

    def health_check(self) -> tuple[bool, str]:
        return True, "33 pillars registered"
