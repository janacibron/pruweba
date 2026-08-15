"""Federation family — constitutional core (Pillars I-V)."""
from __future__ import annotations

from .base import BasePillar, load_ground_truth


class FederationEngine(BasePillar):
    name = "Federation Engine"
    domain = "Federation"
    mandate = "Sovereign core; federates all pillar services."

    def health_check(self) -> tuple[bool, str]:
        return True, "federation core online"


class SeedCouncil(BasePillar):
    name = "Seed Council"
    domain = "Federation"
    mandate = "Custodian of Genesis; signs expansions."

    def health_check(self) -> tuple[bool, str]:
        try:
            gt = load_ground_truth()
            return bool(gt.GENESIS), f"genesis {gt.GENESIS!r} available"
        except Exception as exc:  # noqa: BLE001
            return False, f"genesis unavailable: {exc}"


class ExpansionAssembly(BasePillar):
    name = "Expansion Assembly"
    domain = "Federation"
    mandate = "Legislates the depth 0→5 expansion."

    def health_check(self) -> tuple[bool, str]:
        try:
            gt = load_ground_truth()
            return gt.MAX_DEPTH == 5, f"expansion depth contract {gt.MAX_DEPTH}"
        except Exception as exc:  # noqa: BLE001
            return False, f"expansion unavailable: {exc}"


class ContinuityWardens(BasePillar):
    name = "Continuity Wardens"
    domain = "Federation"
    mandate = "Monitors Merkle chain continuity."

    def health_check(self) -> tuple[bool, str]:
        try:
            gt = load_ground_truth()
            report = gt.verify_ground_truth(depth=gt.MAX_DEPTH)
            return report["chain_unbroken"], "merkle chain unbroken"
        except Exception as exc:  # noqa: BLE001
            return False, f"chain monitoring unavailable: {exc}"


class RecoveryEngine(BasePillar):
    name = "Recovery Engine"
    domain = "Federation"
    mandate = "Restores missing state; heals broken chains."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_file("docs", "governance", "failure_resolutions.jsonl")
        return ok, ("recovery ledger present" if ok else f"recovery ledger missing: {path}")
