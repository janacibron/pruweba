"""Offline unit tests for portal domain + auth logic. No network, no Supabase."""

import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "api"))

import portal  # noqa: E402
from _onboarding import ClientOnboarding, MerkleSeal  # noqa: E402
from portal import AuthError, ForbiddenError, bearer_token, handle_get, handle_sign  # noqa: E402

PHASES = [
    "Discovery & scoping",
    "Contract sealed",
    "Core module built",
    "Integration tests green",
    "Production handover",
]


def fresh():
    ms = [{"name": n, "status": "pending", "completed_at": None} for n in PHASES]
    ms[0]["status"] = "active"
    return ClientOnboarding("Paydora_Payments", ms, [])


class Headers(dict):
    def get(self, k, d=None):
        return dict.get(self, k, d)


# ---- domain ---------------------------------------------------------------
def test_progress_and_chain():
    c = fresh()
    p1 = c.complete_milestone("Discovery & scoping")
    p2 = c.complete_milestone("Contract sealed")
    p = c.progress()
    assert (p["completed"], p["percent"]) == (2, 40.0), p
    assert p1["prev"] == MerkleSeal.GENESIS
    assert p2["prev"] == p1["hash"]
    assert c.seal.verify()


def test_tamper_detected():
    c = fresh()
    c.complete_milestone("Discovery & scoping")
    c.seal.proofs[0]["milestone"] = "forged"
    assert not c.seal.verify()


def test_completion_verdict():
    c = fresh()
    for n in PHASES:
        c.complete_milestone(n)
    p = c.progress()
    assert (p["percent"], p["verdict"]) == (100.0, "COMPLETE"), p


def test_milestone_errors():
    c = fresh()
    try:
        c.complete_milestone("nope")
        raise AssertionError("expected KeyError")
    except KeyError:
        pass
    c.complete_milestone("Contract sealed")
    try:
        c.complete_milestone("Contract sealed")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


# ---- auth -----------------------------------------------------------------
def test_bearer_parsing():
    assert bearer_token(Headers({"Authorization": "Bearer abc.def"})) == "abc.def"
    assert bearer_token(Headers({"authorization": "bearer xyz"})) == "xyz"
    for bad in [{}, {"Authorization": ""}, {"Authorization": "Basic abc"},
                {"Authorization": "Bearer"}, {"Authorization": "Bearer   "}]:
        try:
            bearer_token(Headers(bad))
            raise AssertionError(f"expected AuthError for {bad}")
        except AuthError:
            pass


def test_unauthenticated_is_401():
    """No token must be rejected before any DB work happens."""
    called = []
    orig = portal._supabase
    portal._supabase = lambda: called.append(1)
    try:
        assert handle_get("Paydora_Payments", None)[0] == 401
        assert handle_get("", "")[0] == 401
        assert handle_sign({"milestone": "x"}, None)[0] == 401
    finally:
        portal._supabase = orig
    assert not called, "must not touch Supabase when unauthenticated"


def test_wrong_owner_is_403():
    """A verified user may not read a project assigned to someone else."""
    rows = [{"id": "p1", "client_name": "Paydora_Payments",
             "assigned_user_email": "owner@paydora.com"}]

    class FakeTable:
        def select(self, *a, **k): return self
        def limit(self, *a, **k): return self
        def eq(self, col, val):
            self._m = [r for r in rows if r.get(col) == val]
            return self
        def ilike(self, col, val):
            v = val.rstrip("%").lower()
            self._m = [r for r in rows
                       if (r.get(col) or "").lower().startswith(v)
                       if col != "assigned_user_email" or (r.get(col) or "").lower() == v]
            return self
        def execute(self): return type("R", (), {"data": self._m})()

    sb = type("SB", (), {"table": lambda self, n: FakeTable()})()
    try:
        portal._find_project(sb, "Paydora_Payments", "intruder@evil.com")
        raise AssertionError("expected ForbiddenError")
    except ForbiddenError:
        pass
    got = portal._find_project(sb, "Paydora_Payments", "owner@paydora.com")
    assert got["id"] == "p1"


def test_prefix_must_not_leak_across_tenants():
    """Regression: requesting 'X' must never resolve to the caller's own 'X_Other'.

    Caught live -- the intruder asked for ZZ_Auth_Sandbox and got 200 with
    ZZ_Auth_Sandbox_Other because matching happened inside the caller's rows.
    """
    rows = [
        {"id": "p1", "client_name": "Acme", "assigned_user_email": "owner@acme.com"},
        {"id": "p2", "client_name": "Acme_Other", "assigned_user_email": "intruder@evil.com"},
    ]

    class FakeTable:
        def select(self, *a, **k): return self
        def limit(self, *a, **k): return self
        def eq(self, col, val):
            self._m = [r for r in rows if r.get(col) == val]
            return self
        def ilike(self, col, val):
            v = val.rstrip("%").lower()
            if col == "assigned_user_email":
                self._m = [r for r in rows if (r.get(col) or "").lower() == v]
            else:
                self._m = [r for r in rows if (r.get(col) or "").lower().startswith(v)]
            return self
        def execute(self): return type("R", (), {"data": self._m})()

    sb = type("SB", (), {"table": lambda self, n: FakeTable()})()
    try:
        got = portal._find_project(sb, "Acme", "intruder@evil.com")
        raise AssertionError(f"leaked {got['client_name']} to intruder")
    except ForbiddenError:
        pass
    # each owner still reaches their own project
    assert portal._find_project(sb, "Acme", "owner@acme.com")["id"] == "p1"
    assert portal._find_project(sb, "Acme_Other", "intruder@evil.com")["id"] == "p2"


def test_sign_requires_milestone():
    orig = portal.verify_user
    portal.verify_user = lambda t: "owner@paydora.com"
    try:
        assert handle_sign({"client": "Paydora"}, "tok")[0] == 400
    finally:
        portal.verify_user = orig


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"SELFTEST_OK ({len(tests)} tests)")
