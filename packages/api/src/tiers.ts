// tiers.ts — Usage tiers (all free during beta)
// Tracks per-key usage with configurable limits

interface Tier {
  name: string;
  limit: number;          // verifications per window
  windowMs: number;       // window in milliseconds (30 days)
}

export const TIERS: Record<string, Tier> = {
  free: {
    name: "Free",
    limit: 1_000,
    windowMs: 30 * 24 * 60 * 60 * 1000, // 30 days
  },
  pro: {
    name: "Pro",
    limit: 10_000,
    windowMs: 30 * 24 * 60 * 60 * 1000,
  },
  team: {
    name: "Team",
    limit: 100_000,
    windowMs: 30 * 24 * 60 * 60 * 1000,
  },
};

// Which tier a key gets (default: free)
export function getTier(apiKey?: string): Tier {
  if (!apiKey) return TIERS.free;
  // Future: look up key → tier mapping from DB
  return TIERS.free;
}

// Simple in-memory usage tracker (resets on cold start — acceptable for beta)
const usage = new Map<string, number>();

export function incrementUsage(key: string): number {
  const current = usage.get(key) ?? 0;
  usage.set(key, current + 1);
  return current + 1;
}

export function getUsage(key: string): number {
  return usage.get(key) ?? 0;
}

// Periodic cleanup every hour
setInterval(() => usage.clear(), 60 * 60 * 1000);
