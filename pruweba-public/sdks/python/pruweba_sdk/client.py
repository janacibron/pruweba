# Copyright (c) 2026 Pruweba. Source available under PolyForm Noncommercial 1.0.0.
# Commercial use requires a paid license: https://pruweba.com/pricing

"""
Pruweba Python SDK

Example:
    from pruweba_sdk import PruwebaClient

    client = PruwebaClient(api_key="pw_live_...")

    attestation = client.verify(
        id="claim-001",
        subject="agent-alpha",
        predicate="produced_output",
        object={"hash": "abc123"},
        origin="my-app",
    )

    print(attestation["verdict"]["status"])  # "VERIFIED"
"""

from typing import Any, Dict, List, Optional
import requests


class PruwebaClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.pruweba.com/v1",
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})

    def verify(self, **claim: Any) -> Dict[str, Any]:
        """Submit a claim for verification."""
        response = self.session.post(
            f"{self.base_url}/verify",
            json={
                "id": claim.get("id"),
                "subject": claim.get("subject"),
                "predicate": claim.get("predicate"),
                "object": claim.get("object"),
                "origin": claim.get("origin"),
                "timestamp": claim.get("timestamp"),
                "evidence": claim.get("evidence"),
            },
        )
        response.raise_for_status()
        return response.json()

    def list_attestations(self) -> List[Dict[str, Any]]:
        """List all attestations."""
        response = self.session.get(f"{self.base_url}/attestations")
        response.raise_for_status()
        return response.json()

    def get_attestation(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """Get an attestation by claim ID."""
        response = self.session.get(f"{self.base_url}/attestations/{claim_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def health(self) -> Dict[str, Any]:
        """Check API health."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
