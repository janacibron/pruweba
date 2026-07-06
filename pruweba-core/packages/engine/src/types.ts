// Copyright (c) 2026 Pruweba. Proprietary and confidential. All rights reserved.
// Unauthorized use, reproduction, or distribution is prohibited.

// Pruweba — Core Types
// The foundational vocabulary of the verification layer.

/** A claim submitted for verification */
export interface Claim {
  /** Unique claim identifier (client-generated) */
  id: string;
  /** What is being claimed about */
  subject: string;
  /** The asserted relationship */
  predicate: string;
  /** The asserted value or target */
  object: unknown;
  /** Supporting evidence or context */
  evidence?: Record<string, unknown>;
  /** Claim origin — agent, module, or system */
  origin: string;
  /** When the claim was made (ISO 8601) */
  timestamp: string;
}

/** The result of verifying a claim */
export type Verdict =
  | { status: 'VERIFIED'; confidence: number; reason: string }
  | { status: 'REJECTED'; reason: string; counterevidence?: string }
  | { status: 'UNVERIFIABLE'; reason: string };

/** A deterministic proof generated from a verified claim */
export interface Proof {
  /** Hash of the claim that was proven */
  claimHash: string;
  /** Hash of the previous proof in the chain */
  previousHash: string;
  /** The proof hash (claimHash + previousHash + timestamp) */
  proofHash: string;
  /** When the proof was generated */
  timestamp: string;
  /** The algorithm used */
  algorithm: 'sha256';
}

/** An immutable attestation — the final artifact */
export interface Attestation {
  /** Unique attestation ID */
  id: string;
  /** The original claim */
  claim: Claim;
  /** The verification verdict */
  verdict: Verdict;
  /** The cryptographic proof */
  proof: Proof;
  /** Sequence number in the evidence store */
  sequence: number;
  /** When this attestation was recorded */
  recordedAt: string;
}

/** An evidence record in the append-only store */
export interface EvidenceRecord {
  /** Attestation data */
  attestation: Attestation;
  /** Hash of the previous record (chain integrity) */
  previousRecordHash: string;
  /** Hash of this record */
  recordHash: string;
}

/** Invariant — a rule that must always hold */
export interface Invariant {
  /** Unique invariant ID */
  id: string;
  /** Human-readable description */
  description: string;
  /** The check function: returns true if the invariant holds */
  check: (claim: Claim) => boolean;
  /** Severity: violation means REJECTED, warning means VERIFIED with note */
  severity: 'violation' | 'warning';
}

/** The public API surface of the verification engine */
export interface VerificationEngine {
  /** Submit a claim for verification */
  verify(claim: Claim): Promise<Attestation>;
  /** Register an invariant rule */
  registerInvariant(invariant: Invariant): void;
  /** Get all attestations */
  getAttestations(): Attestation[];
  /** Get an attestation by claim ID */
  getAttestation(claimId: string): Attestation | undefined;
  /** Get the evidence chain */
  getEvidenceChain(): EvidenceRecord[];
  /** Verify chain integrity */
  verifyChainIntegrity(): { valid: boolean; brokenAt?: number; reason?: string };
}
