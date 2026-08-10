"""Core onboarding / sealing logic for the Client Portal.

Self-contained port of the local onboarding.py concepts:
  - MerkleSeal : SHA-256 chained proof over completed milestones
  - Oracle     : deterministic status + advisory over milestone state
  - ClientOnboarding : client project aggregate (view / progress / sign-off)

No LLM, no network. Deterministic given the same inputs.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

STATUS_DONE = "done"
STATUS_ACTIVE = "active"
STATUS_PENDING = "pending"

_ICON = {STATUS_DONE: "\u2705", STATUS_ACTIVE: "\U0001F7E1", STATUS_PENDING: "\u23F3"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class MerkleSeal:
    """Append-only SHA-256 hash chain. Each proof commits to the previous one."""

    GENESIS = "0" * 64

    def __init__(self, proofs: Optional[List[Dict[str, Any]]] = None) -> None:
        self.proofs: List[Dict[str, Any]] = list(proofs or [])

    @property
    def head(self) -> str:
        return self.proofs[-1]["hash"] if self.proofs else self.GENESIS

    @staticmethod
    def leaf_hash(payload: Dict[str, Any]) -> str:
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def seal(self, client: str, milestone: str, sealed_at: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "client": client,
            "milestone": milestone,
            "prev": self.head,
            "sealed_at": sealed_at or _utc_now(),
        }
        proof = dict(payload)
        proof["hash"] = self.leaf_hash(payload)
        self.proofs.append(proof)
        return proof

    def verify(self) -> bool:
        prev = self.GENESIS
        for p in self.proofs:
            payload = {
                "client": p["client"],
                "milestone": p["milestone"],
                "prev": prev,
                "sealed_at": p["sealed_at"],
            }
            if self.leaf_hash(payload) != p["hash"] or p["prev"] != prev:
                return False
            prev = p["hash"]
        return True

    def root(self) -> str:
        return self.head

    def to_json(self) -> List[Dict[str, Any]]:
        return list(self.proofs)


class Oracle:
    """Deterministic advisory layer over milestone state."""

    @staticmethod
    def assess(milestones: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(milestones)
        done = sum(1 for m in milestones if m.get("status") == STATUS_DONE)
        active = [m["name"] for m in milestones if m.get("status") == STATUS_ACTIVE]
        pending = [m["name"] for m in milestones if m.get("status") == STATUS_PENDING]

        if total == 0:
            verdict, advice = "UNSCOPED", "No milestones defined. Scope the engagement first."
        elif done == total:
            verdict, advice = "COMPLETE", "All milestones sealed. Ready for final handover."
        elif active:
            verdict, advice = "ON_TRACK", f"In flight: {active[0]}. Sign off to advance the chain."
        elif pending:
            verdict, advice = "STALLED", f"Nothing active. Next up: {pending[0]}."
        else:
            verdict, advice = "UNKNOWN", "Milestone states are inconsistent."

        return {"verdict": verdict, "advice": advice, "done": done, "total": total}


class ClientOnboarding:
    """Client project aggregate."""

    def __init__(
        self,
        client_name: str,
        milestones: Optional[List[Dict[str, Any]]] = None,
        proofs: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self.client_name = client_name
        self.milestones: List[Dict[str, Any]] = [
            {
                "name": m["name"],
                "status": m.get("status", STATUS_PENDING),
                "completed_at": m.get("completed_at"),
            }
            for m in (milestones or [])
        ]
        self.seal = MerkleSeal(proofs)

    # ---- state -----------------------------------------------------------
    def progress(self) -> Dict[str, Any]:
        total = len(self.milestones)
        done = sum(1 for m in self.milestones if m["status"] == STATUS_DONE)
        pct = round((done / total) * 100, 1) if total else 0.0
        oracle = Oracle.assess(self.milestones)
        return {
            "client": self.client_name,
            "completed": done,
            "total": total,
            "percent": pct,
            "verdict": oracle["verdict"],
            "advice": oracle["advice"],
            "seal_root": self.seal.root(),
            "chain_valid": self.seal.verify(),
            "milestones": [
                {**m, "icon": _ICON.get(m["status"], "\u2753")} for m in self.milestones
            ],
            "proofs": self.seal.to_json(),
        }

    def complete_milestone(self, milestone: str) -> Dict[str, Any]:
        target = next((m for m in self.milestones if m["name"] == milestone), None)
        if target is None:
            raise KeyError(f"unknown milestone: {milestone}")
        if target["status"] == STATUS_DONE:
            raise ValueError(f"milestone already sealed: {milestone}")

        target["status"] = STATUS_DONE
        target["completed_at"] = _utc_now()
        proof = self.seal.seal(self.client_name, milestone, target["completed_at"])

        # promote the next pending milestone to active
        for m in self.milestones:
            if m["status"] == STATUS_ACTIVE:
                break
        else:
            nxt = next((m for m in self.milestones if m["status"] == STATUS_PENDING), None)
            if nxt:
                nxt["status"] = STATUS_ACTIVE
        return proof

    # ---- rendering -------------------------------------------------------
    def client_view(self) -> str:
        p = self.progress()
        bar_w = 32
        filled = int(bar_w * p["percent"] / 100)
        bar = "\u2588" * filled + "\u2591" * (bar_w - filled)
        lines = [
            "=" * 58,
            f"  CLIENT PORTAL \u2014 {self.client_name}",
            "=" * 58,
            f"  [{bar}] {p['percent']}%  ({p['completed']}/{p['total']})",
            f"  STATUS : {p['verdict']}",
            f"  ORACLE : {p['advice']}",
            "-" * 58,
        ]
        for i, m in enumerate(p["milestones"], 1):
            stamp = m["completed_at"] or "\u2014"
            lines.append(f"  {i:>2}. {m['icon']}  {m['name']:<32} {stamp}")
        lines.append("-" * 58)
        lines.append(f"  SEAL ROOT   : {p['seal_root']}")
        lines.append(f"  CHAIN VALID : {'YES' if p['chain_valid'] else 'NO'}")
        if p["proofs"]:
            lines.append("  SEALED PROOFS:")
            for pr in p["proofs"]:
                lines.append(f"    \u00b7 {pr['hash'][:16]}\u2026  {pr['milestone']}")
        lines.append("=" * 58)
        return "\n".join(lines)

    # ---- serialization ---------------------------------------------------
    def milestones_json(self) -> List[Dict[str, Any]]:
        return [dict(m) for m in self.milestones]

    def proofs_json(self) -> List[Dict[str, Any]]:
        return self.seal.to_json()
