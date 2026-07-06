// Copyright (c) 2026 Pruweba. Proprietary and confidential. All rights reserved.
// Unauthorized use, reproduction, or distribution is prohibited.

// Pruweba — Attestation
// Produces the final immutable record: Claim + Verdict + Proof = Attestation.

import { createHash } from 'node:crypto';
import type { Claim, Verdict, Proof, Attestation } from './types.js';
import { generateProof } from './prove.js';
import type { Proof as ProofType } from './types.js';

let attestationSequence = 0;

/**
 * Create an attestation from a claim, verdict, and proof chain.
 * Each attestation gets a monotonically increasing sequence number.
 */
export function createAttestation(
  claim: Claim,
  verdict: Verdict,
  previousProof: ProofType | null,
): Attestation {
  const proof = generateProof(claim, previousProof);
  attestationSequence++;

  return {
    id: `att-${attestationSequence.toString().padStart(6, '0')}`,
    claim,
    verdict,
    proof,
    sequence: attestationSequence,
    recordedAt: new Date().toISOString(),
  };
}

/**
 * Hash an attestation for chain linking.
 */
export function hashAttestation(attestation: Attestation): string {
  const input = JSON.stringify({
    id: attestation.id,
    claimHash: attestation.proof.claimHash,
    verdictStatus: attestation.verdict.status,
    proofHash: attestation.proof.proofHash,
    sequence: attestation.sequence,
    recordedAt: attestation.recordedAt,
  });
  return createHash('sha256').update(input).digest('hex');
}
