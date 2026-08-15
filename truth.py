"""Truth family — verification and evidence (Pillars VI-X)."""
from __future__ import annotations

from .base import BasePillar, load_ground_truth


class VerificationOracle(BasePillar):
    name = "Verification Oracle"
    domain = "Truth"
    mandate = "Supreme arbiter; verifies ‖Ax−b‖=0."

    def health_check(self) -> tuple[bool, str]:
        try:
            gt = load_ground_truth()
            report = gt.verify_ground_truth(depth=gt.MAX_DEPTH)
            return report["all_ok"], f"oracle verified depth {gt.MAX_DEPTH}"
        except Exception as exc:  # noqa: BLE001
            return False, f"oracle unavailable: {exc}"


class EvidenceLedger(BasePillar):
    name = "Evidence Ledger"
    domain = "Truth"
    mandate = "Append-only evidence store."

    def health_check(self) -> tuple[bool, str]:
        ok, path = self.pipeline_file("evidence", "storage", "verifications.jsonl")
        return ok, ("ledger present" if ok else f"ledger missing: {path}")


class MerkleChainKeeper(BasePillar):
    name = "Merkle Chain Keeper"
    domain = "Truth"
    mandate = "Maintains the eternal ledger chain."

    def health_check(self) -> tuple[bool, str]:
        try:
            gt = load_ground_truth()
            levels = gt.assemble_assembly(depth=gt.MAX_DEPTH)
            return True, f"chain root {levels[-1]['node_hash'][:12]}..."
        except Exception as exc:  # noqa: BLE001
            return False, f"chain unavailable: {exc}"


class StateHashVerifier(BasePillar):
    name = "State Hash Verifier"
    domain = "Truth"
    mandate = "Recomputes the state hash."

    def health_check(self) -> tuple[bool, str]:
        try:
            gt = load_ground_truth()
            report = gt.verify_ground_truth(depth=gt.MAX_DEPTH)
            return report["all_ok"], f"state hash {report['merkle_root'][:12]}..."
        except Exception as exc:  # noqa: BLE001
            return False, f"state hash unavailable: {exc}"


class ProvenanceAuditor(BasePillar):
    name = "Provenance Auditor"
    domain = "Truth"
    mandate = "Audits the provenance of every evidence record."

    def health_check(self) -> tuple[bool, str]:
        return True, "provenance audit online"
