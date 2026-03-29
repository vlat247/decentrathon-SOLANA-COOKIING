const BASE = 'http://localhost:8000';

export async function fetchWallet(publicKey: string) {
  try {
    const res = await fetch(`${BASE}/api/wallet/${publicKey}`);
    if (!res.ok) return null;
    const data = await res.json();
  
    // normalize field names in case backend differs
    return {
      publicKey:   data.pubkey      ?? data.publicKey   ?? data.public_key,
      solBalance:  data.sol_balance ?? data.solBalance,
      splTokens:   data.tokens      ?? data.spl_tokens  ?? data.splTokens  ?? [],
      txCount:     data.tx_count    ?? data.transaction_count ?? 0,
    };
  } catch (error) {
    console.warn("Backend offline or unable to fetch wallet:", error);
    return null;
  }
}
