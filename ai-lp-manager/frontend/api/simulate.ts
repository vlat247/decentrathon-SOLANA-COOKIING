const BASE = 'http://localhost:8000';

export async function runSimulation({ amount, days, pool, strategy = 'balanced' }: { amount: string | number, days: string | number, pool: string, strategy?: string }) {
  try {
    const res = await fetch(`${BASE}/api/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ initial_amount: Number(amount), time_period: Number(days), pool, strategy })
    });
    if (!res.ok) throw new Error('Simulation failed');
    return await res.json();
  } catch (error) {
    console.warn("Backend offline or unable to run simulation:", error);
    throw error;
  }
}
