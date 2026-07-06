// @pruweba/client — TypeScript client for the Pruweba Verification API
// Base URL: https://api.pruweba.com

const DEFAULT_BASE_URL = "https://api.pruweba.com";

// ── Types ────────────────────────────────────────────────

export interface Claim {
  id: string;
  subject: string;
  predicate: string;
  object: unknown;
  evidence?: Record<string, unknown>;
  origin: string;
  timestamp: string;
}

export type Verdict =
  | { status: "VERIFIED"; confidence: number; reason: string }
  | { status: "REJECTED"; reason: string; counterevidence?: string }
  | { status: "UNVERIFIABLE"; reason: string };

export interface Proof {
  claimHash: string;
  previousHash: string;
  proofHash: string;
  timestamp: string;
  algorithm: "sha256";
}

export interface Attestation {
  id: string;
  claim: Claim;
  verdict: Verdict;
  proof: Proof;
  sequence: number;
  recordedAt: string;
}

export interface EvidenceRecord {
  attestation: Attestation;
  previousRecordHash: string;
  recordHash: string;
}

export interface HealthCheck {
  status: string;
  name: string;
  version: string;
  attestations: number;
  chainValid: boolean;
}

export interface InvariantInfo {
  id: string;
  description: string;
  severity: "violation" | "warning";
}

export interface ChainVerification {
  valid: boolean;
  brokenAt?: number;
  reason?: string;
}

// ── Client ────────────────────────────────────────────────

export class PruwebaClient {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl ?? DEFAULT_BASE_URL;
  }

  private async fetch<T>(path: string, init?: RequestInit): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(`Pruweba API error ${res.status}: ${JSON.stringify(body)}`);
    }
    return res.json() as Promise<T>;
  }

  /** POST /verify — Submit a claim for verification */
  async verify(claim: Claim): Promise<Attestation> {
    return this.fetch<Attestation>("/verify", {
      method: "POST",
      body: JSON.stringify(claim),
    });
  }

  /** GET /attestations — List all attestations */
  async getAttestations(): Promise<Attestation[]> {
    return this.fetch<Attestation[]>("/attestations");
  }

  /** GET /attestations/:claimId — Get attestation by claim ID */
  async getAttestation(claimId: string): Promise<Attestation> {
    return this.fetch<Attestation>(`/attestations/${claimId}`);
  }

  /** GET /chain — Get the full evidence chain */
  async getChain(): Promise<EvidenceRecord[]> {
    return this.fetch<EvidenceRecord[]>("/chain");
  }

  /** GET /chain/verify — Verify chain integrity */
  async verifyChain(): Promise<ChainVerification> {
    return this.fetch<ChainVerification>("/chain/verify");
  }

  /** GET /health — Health check */
  async health(): Promise<HealthCheck> {
    return this.fetch<HealthCheck>("/health");
  }

  /** GET /invariants — List registered invariants */
  async getInvariants(): Promise<InvariantInfo[]> {
    return this.fetch<InvariantInfo[]>("/invariants");
  }
}

// ── Default instance ──────────────────────────────────────

export const pruweba = new PruwebaClient();
export default pruweba;
