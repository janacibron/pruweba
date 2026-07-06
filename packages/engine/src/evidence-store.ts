// Pruweba — Append-Only Evidence Store
// Immutable, hash-chained evidence records. Write once, verify forever.

import { createHash } from 'node:crypto';
import type { Attestation, EvidenceRecord } from './types.js';
import { hashAttestation } from './attest.js';

/**
 * An append-only evidence store with chain integrity.
 * Records are hash-linked — tampering with any record breaks the chain.
 */
export class EvidenceStore {
  private records: EvidenceRecord[] = [];

  /**
   * Append an attestation to the evidence store.
   * Returns the newly created evidence record with its chain hash.
   */
  append(attestation: Attestation): EvidenceRecord {
    const previousRecordHash =
      this.records.length > 0
        ? this.records[this.records.length - 1].recordHash
        : '0000000000000000000000000000000000000000000000000000000000000000';

    const recordHash = this.computeRecordHash(attestation, previousRecordHash);

    const record: EvidenceRecord = {
      attestation,
      previousRecordHash,
      recordHash,
    };

    this.records.push(record);
    return record;
  }

  /**
   * Get all evidence records.
   */
  getAll(): EvidenceRecord[] {
    return [...this.records];
  }

  /**
   * Get the total number of records.
   */
  get count(): number {
    return this.records.length;
  }

  /**
   * Get the latest record (the tip of the chain).
   */
  getLatest(): EvidenceRecord | undefined {
    return this.records[this.records.length - 1];
  }

  /**
   * Verify the integrity of the entire evidence chain.
   * Returns which record broke the chain, or null if intact.
   */
  verifyIntegrity(): { valid: boolean; brokenAt?: number; reason?: string } {
    for (let i = 0; i < this.records.length; i++) {
      const record = this.records[i];

      // Check the previous hash link
      if (i === 0) {
        if (record.previousRecordHash !==
          '0000000000000000000000000000000000000000000000000000000000000000') {
          return {
            valid: false,
            brokenAt: i,
            reason: 'First record has non-genesis previousRecordHash',
          };
        }
      } else {
        const expectedPrevious = this.records[i - 1].recordHash;
        if (record.previousRecordHash !== expectedPrevious) {
          return {
            valid: false,
            brokenAt: i,
            reason: `Record ${i} previousRecordHash does not match record ${i - 1}`,
          };
        }
      }

      // Check the record's own hash
      const expectedHash = this.computeRecordHash(
        record.attestation,
        record.previousRecordHash,
      );
      if (record.recordHash !== expectedHash) {
        return {
          valid: false,
          brokenAt: i,
          reason: `Record ${i} hash mismatch`,
        };
      }
    }

    return { valid: true };
  }

  /**
   * Compute the hash for a record.
   */
  private computeRecordHash(
    attestation: Attestation,
    previousRecordHash: string,
  ): string {
    const attHash = hashAttestation(attestation);
    const input = `${attHash}:${previousRecordHash}:${attestation.sequence}`;
    return createHash('sha256').update(input).digest('hex');
  }

  /**
   * Clear all records. Use only for testing.
   */
  clear(): void {
    this.records = [];
  }
}
