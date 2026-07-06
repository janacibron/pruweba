// Pruweba — Claim validation
import type { Claim } from './types.js';

/** Errors that make a claim structurally invalid */
const CLAIM_VALIDATION_ERRORS = {
  MISSING_ID: 'Claim must have an id',
  MISSING_SUBJECT: 'Claim must have a subject',
  MISSING_PREDICATE: 'Claim must have a predicate',
  MISSING_ORIGIN: 'Claim must have an origin',
  INVALID_TIMESTAMP: 'Claim timestamp must be valid ISO 8601',
  EMPTY_STRING_FIELD: (field: string) => `Claim ${field} must not be empty`,
} as const;

/**
 * Validate that a claim is structurally sound.
 * Returns null if valid, or an error message if invalid.
 */
export function validateClaim(claim: unknown): claim is Claim {
  return getClaimError(claim) === null;
}

/**
 * Validate and return the error message, or null if valid.
 */
export function getClaimError(claim: unknown): string | null {
  if (!claim || typeof claim !== 'object') {
    return 'Claim must be an object';
  }

  const c = claim as Record<string, unknown>;

  if (!c.id || typeof c.id !== 'string') {
    return CLAIM_VALIDATION_ERRORS.MISSING_ID;
  }
  if (c.id.trim() === '') {
    return CLAIM_VALIDATION_ERRORS.EMPTY_STRING_FIELD('id');
  }
  if (!c.subject || typeof c.subject !== 'string') {
    return CLAIM_VALIDATION_ERRORS.MISSING_SUBJECT;
  }
  if (c.subject.trim() === '') {
    return CLAIM_VALIDATION_ERRORS.EMPTY_STRING_FIELD('subject');
  }
  if (!c.predicate || typeof c.predicate !== 'string') {
    return CLAIM_VALIDATION_ERRORS.MISSING_PREDICATE;
  }
  if (c.predicate.trim() === '') {
    return CLAIM_VALIDATION_ERRORS.EMPTY_STRING_FIELD('predicate');
  }
  if (!c.origin || typeof c.origin !== 'string') {
    return CLAIM_VALIDATION_ERRORS.MISSING_ORIGIN;
  }
  if (c.origin.trim() === '') {
    return CLAIM_VALIDATION_ERRORS.EMPTY_STRING_FIELD('origin');
  }
  if (!c.timestamp || typeof c.timestamp !== 'string') {
    return CLAIM_VALIDATION_ERRORS.INVALID_TIMESTAMP;
  }
  // Validate ISO 8601 — must parse to a valid date
  const parsed = Date.parse(c.timestamp as string);
  if (isNaN(parsed)) {
    return CLAIM_VALIDATION_ERRORS.INVALID_TIMESTAMP;
  }

  return null;
}

/**
 * Assert that a claim is valid, throwing if not.
 */
export function assertValidClaim(claim: unknown): asserts claim is Claim {
  const error = getClaimError(claim);
  if (error) {
    throw new Error(`Invalid claim: ${error}`);
  }
}
