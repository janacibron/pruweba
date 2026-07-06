// Copyright (c) 2026 Pruweba. Proprietary and confidential. All rights reserved.
// Unauthorized use, reproduction, or distribution is prohibited.

// Pruweba — Verification
// Checks claims against registered invariants and produces verdicts.

import type { Claim, Invariant, Verdict } from './types.js';
import { assertValidClaim } from './claim.js';

/**
 * Verify a claim against a set of invariants.
 * A claim is VERIFIED only if ALL violation-severity invariants pass.
 * Warnings do not cause rejection — they annotate the verdict.
 */
export function verifyClaim(claim: Claim, invariants: Invariant[]): Verdict {
  assertValidClaim(claim);

  const warnings: string[] = [];

  for (const invariant of invariants) {
    try {
      const holds = invariant.check(claim);
      if (!holds) {
        if (invariant.severity === 'violation') {
          return {
            status: 'REJECTED',
            reason: `Invariant violated: ${invariant.description}`,
            counterevidence: invariant.id,
          };
        }
        // severity === 'warning'
        warnings.push(invariant.description);
      }
    } catch (err) {
      // If an invariant check throws, treat as violation
      return {
        status: 'REJECTED',
        reason: `Invariant '${invariant.id}' threw: ${err instanceof Error ? err.message : String(err)}`,
        counterevidence: invariant.id,
      };
    }
  }

  // All violation invariants passed
  const confidence = calculateConfidence(invariants.length, warnings.length);

  if (warnings.length > 0) {
    return {
      status: 'VERIFIED',
      confidence,
      reason: `All invariants pass. ${warnings.length} warning(s): ${warnings.join('; ')}`,
    };
  }

  return {
    status: 'VERIFIED',
    confidence,
    reason: 'All invariants pass.',
  };
}

/**
 * Calculate a simple confidence score.
 * More invariants checked → higher confidence.
 * Warnings reduce confidence slightly.
 */
function calculateConfidence(totalInvariants: number, warningCount: number): number {
  if (totalInvariants === 0) return 0.5; // No invariants = low confidence
  const base = Math.min(0.95, 0.5 + (totalInvariants * 0.05));
  const penalty = warningCount * 0.03;
  return Math.max(0.1, base - penalty);
}
