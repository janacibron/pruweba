// Copyright (c) 2026 Pruweba. Proprietary and confidential. All rights reserved.
// Unauthorized use, reproduction, or distribution is prohibited.

// Pruweba — Public API Surface
// The verification engine. Claim → Verify → Prove → Attest.

import type { Claim, Attestation, EvidenceRecord, Invariant, VerificationEngine } from './types.js';
import { assertValidClaim } from './claim.js';
import { verifyClaim } from './verify.js';
import { createAttestation } from './attest.js';
import { EvidenceStore } from './evidence-store.js';
import type { Proof } from './types.js';

/**
 * Create a new Pruweba verification engine.
 * The engine enforces invariants, proves claims, and maintains
 * an immutable evidence chain.
 */
export function createEngine(): VerificationEngine {
  const store = new EvidenceStore();
  const invariants: Invariant[] = [];
  let lastProof: Proof | null = null;

  const engine: VerificationEngine = {
    async verify(claim: Claim): Promise<Attestation> {
      // Gate 1: Validate structure
      assertValidClaim(claim);

      // Gate 2: Check invariants
      const verdict = verifyClaim(claim, invariants);

      // Gate 3: Create attestation (always — even REJECTED claims get attested)
      const attestation = createAttestation(claim, verdict, lastProof);
      lastProof = attestation.proof;

      // Gate 4: Append to evidence store
      store.append(attestation);

      return attestation;
    },

    registerInvariant(invariant: Invariant): void {
      invariants.push(invariant);
    },

    getAttestations(): Attestation[] {
      return store.getAll().map((r) => r.attestation);
    },

    getAttestation(claimId: string): Attestation | undefined {
      return store
        .getAll()
        .map((r) => r.attestation)
        .find((a) => a.claim.id === claimId);
    },

    getEvidenceChain(): EvidenceRecord[] {
      return store.getAll();
    },

    verifyChainIntegrity(): {
      valid: boolean;
      brokenAt?: number;
      reason?: string;
    } {
      return store.verifyIntegrity();
    },
  };

  return engine;
}

// Re-export types for consumers
export type {
  Claim,
  Verdict,
  Proof,
  Attestation,
  EvidenceRecord,
  Invariant,
  VerificationEngine,
} from './types.js';

export { validateClaim, getClaimError } from './claim.js';
export { verifyClaim } from './verify.js';
export { hashClaim, generateProof, verifyProof } from './prove.js';
export { EvidenceStore } from './evidence-store.js';
