const BASE = 'http://localhost:8000';

// pool_id format the backend expects: "SOL-USDC"
export async function getAIDecision(poolId: string) {
  try {
    const res = await fetch(`${BASE}/api/decide/${poolId}`);
    if (!res.ok) throw new Error('AI decision fetch failed');
    const data = await res.json();

    return {
      action:     data.action     ?? data.signal,       // "INCREASE"|"HOLD"|"EXIT"
      score:      data.score      ?? data.composite_score,
      confidence: data.confidence ?? data.confidence_score,
      reason:     data.reason     ?? data.reasoning,
      pool:       data.pool       ?? poolId,
    };
  } catch (error) {
    console.warn("Backend offline or unable to fetch AI decision:", error);
    return null;
  }
}
