// Pruweba — Integration test
// Verifies the full pipeline: Claim → Verify → Prove → Attest

import { createEngine } from './index.js';
import type { Claim, Invariant } from './types.js';

const engine = createEngine();

// Register invariants
const TIMESTAMP_INVARIANT: Invariant = {
  id: 'INV-TIMESTAMP',
  description: 'Claim timestamp must not be in the future',
  severity: 'violation',
  check: (claim: Claim) => new Date(claim.timestamp) <= new Date(),
};

const PREDICATE_INVARIANT: Invariant = {
  id: 'INV-PREDICATE',
  description: 'Predicate must be a known action',
  severity: 'violation',
  check: (claim: Claim) =>
    ['produced_output', 'status', 'state_transition', 'invariant_check'].includes(claim.predicate),
};

engine.registerInvariant(TIMESTAMP_INVARIANT);
engine.registerInvariant(PREDICATE_INVARIANT);

let passed = 0;
let failed = 0;

function assert(condition: boolean, label: string) {
  if (condition) {
    console.log(`  ✓ ${label}`);
    passed++;
  } else {
    console.log(`  ✗ ${label}`);
    failed++;
  }
}

// Test 1: Valid claim → VERIFIED
async function test1() {
  console.log('\nTest 1: Valid claim should VERIFY');
  const claim: Claim = {
    id: 'test-001',
    subject: 'agent-alpha',
    predicate: 'produced_output',
    object: { hash: 'abc123', size: 100 },
    origin: 'metal-loop-v0.1',
    timestamp: new Date().toISOString(),
  };

  const attestation = await engine.verify(claim);
  assert(attestation.verdict.status === 'VERIFIED', 'Status is VERIFIED');
  assert(attestation.sequence === 1, 'Sequence is 1');
  assert(attestation.proof.algorithm === 'sha256', 'Algorithm is sha256');
  assert(attestation.proof.previousHash === '0000000000000000000000000000000000000000000000000000000000000000', 'First proof links to genesis');
  assert(typeof attestation.proof.proofHash === 'string', 'Proof hash is generated');
}

// Test 2: Invalid predicate → REJECTED
async function test2() {
  console.log('\nTest 2: Invalid predicate should REJECT');
  const claim: Claim = {
    id: 'test-002',
    subject: 'agent-beta',
    predicate: 'unauthorized_action',
    object: null,
    origin: 'unknown-source',
    timestamp: new Date().toISOString(),
  };

  const attestation = await engine.verify(claim);
  assert(attestation.verdict.status === 'REJECTED', 'Status is REJECTED');
  assert(attestation.sequence === 2, 'Sequence increments even on rejection');
}

// Test 3: Future timestamp → REJECTED
async function test3() {
  console.log('\nTest 3: Future timestamp should REJECT');
  const claim: Claim = {
    id: 'test-003',
    subject: 'agent-gamma',
    predicate: 'status',
    object: 'active',
    origin: 'monitor',
    timestamp: new Date(Date.now() + 86400000).toISOString(), // tomorrow
  };

  const attestation = await engine.verify(claim);
  assert(attestation.verdict.status === 'REJECTED', 'Status is REJECTED');
  assert(attestation.sequence === 3, 'Sequence is 3');
}

// Test 4: Evidence chain integrity
async function test4() {
  console.log('\nTest 4: Evidence chain integrity');
  const chain = engine.getEvidenceChain();
  assert(chain.length === 3, 'Chain has 3 records');
  const integrity = engine.verifyChainIntegrity();
  assert(integrity.valid === true, 'Chain integrity is valid');
}

// Test 5: Retrieve attestation by claim ID
async function test5() {
  console.log('\nTest 5: Retrieve attestation by claim ID');
  const found = engine.getAttestation('test-001');
  assert(found !== undefined, 'Found attestation for test-001');
  assert(found!.verdict.status === 'VERIFIED', 'Retrieved verdict is correct');

  const notFound = engine.getAttestation('nonexistent');
  assert(notFound === undefined, 'Nonexistent claim returns undefined');
}

// Test 6: Claim validation
async function test6() {
  console.log('\nTest 6: Claim structural validation');
  const { getClaimError } = await import('./claim.js');

  assert(getClaimError(null) !== null, 'Null is rejected');
  assert(getClaimError({}) !== null, 'Empty object is rejected');
  assert(getClaimError({ id: '', subject: 'x', predicate: 'y', origin: 'z', timestamp: new Date().toISOString() }) !== null, 'Empty id is rejected');
  assert(getClaimError({ id: 'x', subject: 'x', predicate: 'y', origin: 'z', timestamp: 'not-a-date' }) !== null, 'Invalid timestamp is rejected');
}

async function run() {
  console.log('◈ Pruweba Engine Integration Tests');
  console.log('═══════════════════════════════════');

  await test1();
  await test2();
  await test3();
  await test4();
  await test5();
  await test6();

  console.log(`\n═══════════════════════════════════`);
  console.log(`  ${passed} passed, ${failed} failed`);
  console.log(`═══════════════════════════════════`);
  process.exit(failed > 0 ? 1 : 0);
}

run().catch((err) => {
  console.error('Test runner crashed:', err);
  process.exit(1);
});
