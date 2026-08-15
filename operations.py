"""Operations family — execution and delivery (Pillars XVI-XX)."""
from __future__ import annotations

from .base import BasePillar


class MissionScheduler(BasePillar):
    name = "Mission Scheduler"
    domain = "Operations"
    mandate = "Schedules and queues mission execution."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_file("pipeline", "status.py")
        return ok, ("scheduler present" if ok else f"scheduler missing: {path}")


class TaskOrchestrator(BasePillar):
    name = "Task Orchestrator"
    domain = "Operations"
    mandate = "Orchestrates multi-step task flows."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_file("pipeline", "orchestrator.py")
        return ok, ("orchestrator present" if ok else f"orchestrator missing: {path}")


class DeliveryIntegrator(BasePillar):
    name = "Delivery Integrator"
    domain = "Operations"
    mandate = "Delivers generated artifacts to targets."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_file("pipeline", "delivery_integration.py")
        return ok, ("delivery present" if ok else f"delivery missing: {path}")


class MutationPolicyGate(BasePillar):
    name = "Mutation Policy Gate"
    domain = "Operations"
    mandate = "Enforces MUTATING vs read-only execution."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_file("pipeline", "mutation_policy.py")
        return ok, ("mutation policy present" if ok else f"mutation policy missing: {path}")


class FreezeController(BasePillar):
    name = "Freeze Controller"
    domain = "Operations"
    mandate = "Controls governance freeze state."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_file("docs", "governance", "freeze_state.json")
        return ok, ("freeze state present" if ok else f"freeze state missing: {path}")
