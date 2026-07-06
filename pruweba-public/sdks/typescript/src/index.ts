// Copyright (c) 2026 Pruweba. Source available under PolyForm Noncommercial 1.0.0.
// Commercial use requires a paid license: https://pruweba.com/pricing

/**
 * Pruweba TypeScript SDK
 *
 * @example
 * ```ts
 * import { PruwebaClient } from '@pruweba/sdk';
 *
 * const client = new PruwebaClient({ apiKey: 'pw_live_...' });
 *
 * const attestation = await client.verify({
 *   id: 'claim-001',
 *   subject: 'agent-alpha',
 *   predicate: 'produced_output',
 *   object: { hash: 'abc123' },
 *   origin: 'my-app',
 *   timestamp: new Date().toISOString(),
 * });
 * ```
 */

export interface PruwebaConfig {
  apiKey: string;
  baseUrl?: string;
}

export interface Claim {
  id: string;
  subject: string;
  predicate: string;
  object: unknown;
  origin: string;
  timestamp: string;
  evidence?: Record<string, unknown>;
}

export interface Verdict {
  status: 'VERIFIED' | 'REJECTED' | 'UNVERIFIABLE';
  confidence?: number;
  reason: string;
  counterevidence?: string;
}

export interface Proof {
  claimHash: string;
  previousHash: string;
  proofHash: string;
  timestamp: string;
  algorithm: 'sha256';
}

export interface Attestation {
  id: string;
  claim: Claim;
  verdict: Verdict;
  proof: Proof;
  sequence: number;
  recordedAt: string;
}

export class PruwebaClient {
  private apiKey: string;
  private baseUrl: string;

  constructor(config: PruwebaConfig) {
    this.apiKey = config.apiKey;
    this.baseUrl = config.baseUrl ?? 'https://api.pruweba.com/v1';
  }

  /** Submit a claim for verification */
  async verify(claim: Claim): Promise<Attestation> {
    const response = await fetch(`${this.baseUrl}/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey,
      },
      body: JSON.stringify(claim),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Verification failed');
    }

    return response.json();
  }

  /** List all attestations */
  async listAttestations(): Promise<Attestation[]> {
    const response = await fetch(`${this.baseUrl}/attestations`, {
      headers: { 'X-API-Key': this.apiKey },
    });
    return response.json();
  }

  /** Get an attestation by claim ID */
  async getAttestation(claimId: string): Promise<Attestation | null> {
    const response = await fetch(`${this.baseUrl}/attestations/${claimId}`, {
      headers: { 'X-API-Key': this.apiKey },
    });
    if (response.status === 404) return null;
    return response.json();
  }

  /** Check health */
  async health(): Promise<{ status: string; version: string }> {
    const response = await fetch(`${this.baseUrl}/health`, {
      headers: { 'X-API-Key': this.apiKey },
    });
    return response.json();
  }
}

export default PruwebaClient;
