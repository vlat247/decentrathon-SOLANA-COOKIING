const BASE = 'http://localhost:8000';

export async function fetchContractInfo() {
  try {
    const res = await fetch(`${BASE}/api/contract/info`);
    if (!res.ok) return null;
    const data = await res.json();
    
    return {
      network: data.network || 'devnet',
      programId: data.program_id || 'CSjDhZXoYAeSa8mtsy7xgSRVqq2Bbeb9jSwf9RP5QVN6'
    };
  } catch (error) {
    console.warn("Backend offline or unable to fetch contract info:", error);
    return null;
  }
}
