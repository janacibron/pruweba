// Copyright (c) 2026 Pruweba. Proprietary and confidential. All rights reserved.
// Unauthorized use, reproduction, or distribution is prohibited.

// Pruweba — Deterministic Proof Generation
// Produces a cryptographic proof chain using SHA-256.

import { createHash } from 'node:crypto';
import type { Claim, Proof } from './types.js';

/**
 * Serialize a claim to a deterministic string for hashing.
 * Keys are sorted alphabetically for reproducibility.
 */
export function serializeClaim(claim: Claim): string {
  const sorted = {
    evidence: claim.evidence ?? {},
    id: claim.id,
    object: claim.object,
    origin: claim.origin,
    predicate: claim.predicate,
    subject: claim.subject,
    timestamp: claim.timestamp,
  };
  return JSON.stringify(sorted);
}

/**
 * Compute the SHA-256 hash of a claim.
 */
export function hashClaim(claim: Claim): string {
  const serialized = serializeClaim(claim);
  return createHash('sha256').update(serialized).digest('hex');
}

/**
 * Generate a proof for a verified claim.
 * Links to the previous proof via its hash, forming an immutable chain.
 */
export function generateProof(claim: Claim, previousProof: Proof | null): Proof {
  const claimHash = hashClaim(claim);
  const previousHash = previousProof?.proofHash ?? '0000000000000000000000000000000000000000000000000000000000000000';
  const timestamp = new Date().toISOString();

  // Proof = hash(claimHash + previousHash + timestamp)
  const proofInput = `${claimHash}:${previousHash}:${timestamp}`;
  const proofHash = createHash('sha256').update(proofInput).digest('hex');

  return {
    claimHash,
    previousHash,
    proofHash,
    timestamp,
    algorithm: 'sha256',
  };
}

/**
 * Verify that a proof is valid for a given claim.
 */
export function verifyProof(claim: Claim, proof: Proof): boolean {
  const claimHash = hashClaim(claim);
  if (claimHash !== proof.claimHash) return false;

  const proofInput = `${proof.claimHash}:${proof.previousHash}:${proof.timestamp}`;
  const expectedHash = createHash('sha256').update(proofInput).digest('hex');

  return expectedHash === proof.proofHash;
}
