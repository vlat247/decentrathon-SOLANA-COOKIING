"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import { runSimulation } from "../../api/simulate";

export default function Simulate() {
  const [running, setRunning] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [amount, setAmount] = useState<number>(10000);
  const [days, setDays] = useState<number>(30);
  const [poolUI, setPoolUI] = useState<string>("SOL / USDC");
  const [strategy, setStrategy] = useState<string>("Balanced");
  const [simData, setSimData] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const runSim = async () => {
    setRunning(true);
    setShowResults(false);
    setError(null);
    try {
      const poolId = poolUI.replace(" / ", "-");
      const data = await runSimulation({ amount, days, pool: poolId, strategy });
      
      const chartData = data.timeline.map((t: any) => ({
        name: `D${t.day}`,
        base: t.baseline_value,
        ai: t.ai_value
      }));
      setSimData(chartData);
      setSummary(data.summary);
      setShowResults(true);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setRunning(false);
    }
  };

  return (
    <>
      <div className="bg-[var(--bg2)] border border-lp-border rounded-[10px] p-4">
        <div className="font-mono text-[10px] text-[var(--muted)] tracking-[2px] mb-3">Simulation Parameters</div>
        <div className="flex flex-col gap-2.5">
          <div className="flex items-center gap-2.5">
            <div className="text-[12px] text-[var(--muted)] w-[110px] shrink-0">Initial USDC</div>
            <input 
              className="flex-1 bg-[var(--bg3)] border border-lp-border rounded-md px-2.5 py-[7px] text-[13px] text-[var(--text)] font-sans outline-none focus:border-[var(--purple)]" 
              type="number" 
              value={amount} 
              onChange={(e) => setAmount(Number(e.target.value))} 
              min="100" 
            />
          </div>
          <div className="flex items-center gap-2.5">
            <div className="text-[12px] text-[var(--muted)] w-[110px] shrink-0">Period (days)</div>
            <input 
              type="range" 
              min="7" max="90" 
              value={days} 
              onChange={(e) => setDays(Number(e.target.value))} 
              className="flex-1 accent-[var(--purple)]" 
            />
            <span className="font-mono text-[12px] text-[var(--text)] min-w-[32px]">{days}d</span>
          </div>
          <div className="flex items-center gap-2.5">
            <div className="text-[12px] text-[var(--muted)] w-[110px] shrink-0">Pool</div>
            <select 
              value={poolUI} onChange={(e) => setPoolUI(e.target.value)}
              className="flex-1 bg-[var(--bg3)] border border-lp-border rounded-md px-2.5 py-[7px] text-[13px] text-[var(--text)] font-sans outline-none focus:border-[var(--purple)] [&>option]:bg-[var(--bg3)]">
              <option>SOL / USDC</option>
              <option>SOL / USDT</option>
              <option>RAY / SOL</option>
              <option>BONK / SOL</option>
            </select>
          </div>
          <div className="flex items-center gap-2.5">
            <div className="text-[12px] text-[var(--muted)] w-[110px] shrink-0">Strategy</div>
            <select 
              value={strategy} onChange={(e) => setStrategy(e.target.value)}
              className="flex-1 bg-[var(--bg3)] border border-lp-border rounded-md px-2.5 py-[7px] text-[13px] text-[var(--text)] font-sans outline-none focus:border-[var(--purple)] [&>option]:bg-[var(--bg3)]">
              <option>Aggressive (wide range)</option>
              <option>Balanced</option>
              <option>Conservative (narrow)</option>
            </select>
          </div>
          <button 
            className="font-mono text-[11px] px-5 py-[9px] bg-[var(--green)] text-black border-none rounded-md cursor-pointer tracking-[1px] font-bold transition-opacity self-start hover:opacity-85 disabled:opacity-50 disabled:cursor-not-allowed mt-2" 
            onClick={runSim} 
            disabled={running}
          >
            {running ? 'Running...' : 'Run Simulation →'}
          </button>
        </div>
      </div>

      {error && <div className="text-[var(--red)] text-[13px] mt-2 font-mono">Error: {error}</div>}

      {showResults && summary && (
        <div className="bg-[var(--bg2)] border border-lp-border rounded-[10px] p-4 mt-4">
          <div className="font-mono text-[10px] text-[var(--muted)] tracking-[2px] mb-3">
            Results — <span>{days} Days · {poolUI} · ${amount.toLocaleString()}</span>
          </div>
          
          <div className="grid grid-cols-2 gap-2.5">
            <div className="rounded-lg p-3 bg-[rgba(100,116,139,0.1)] border border-[rgba(100,116,139,0.2)]">
              <div className="text-[10px] tracking-[1px] mb-2 font-mono text-[var(--muted)]">Without AI</div>
              <div className="flex justify-between py-1 text-[12px] border-b border-[rgba(255,255,255,0.04)]"><span className="text-[var(--muted)]">Gross Return</span><span>{summary.baseline_return_pct > 0 ? '+' : ''}{summary.baseline_return_pct.toFixed(2)}%</span></div>
              <div className="flex justify-between py-1 text-[12px] border-b border-[rgba(255,255,255,0.04)]"><span className="text-[var(--muted)]">Net Profit</span><span>{summary.baseline_final - amount > 0 ? '+' : ''}${(summary.baseline_final - amount).toFixed(0)}</span></div>
              <div className="flex justify-between py-1 text-[12px] border-none"><span className="text-[var(--muted)]">Final Value</span><span>${summary.baseline_final.toLocaleString()}</span></div>
            </div>
            
            <div className="rounded-lg p-3 bg-[rgba(0,245,160,0.07)] border border-[rgba(0,245,160,0.2)]">
              <div className="text-[10px] tracking-[1px] mb-2 font-mono text-[var(--green)]">With AI Strategy</div>
              <div className="flex justify-between py-1 text-[12px] border-b border-[rgba(255,255,255,0.04)]"><span className="text-[var(--muted)]">Gross Return</span><span className={summary.ai_return_pct > 0 ? "text-[var(--green)]" : "text-[var(--red)]"}>{summary.ai_return_pct > 0 ? '+' : ''}{summary.ai_return_pct.toFixed(2)}%</span></div>
              <div className="flex justify-between py-1 text-[12px] border-b border-[rgba(255,255,255,0.04)]"><span className="text-[var(--muted)]">IL Avoided</span><span className="text-[var(--green)]">${summary.total_il_avoided.toFixed(2)}</span></div>
              <div className="flex justify-between py-1 text-[12px] border-b border-[rgba(255,255,255,0.04)]"><span className="text-[var(--muted)]">Net Profit</span><span className={summary.ai_final - amount > 0 ? "text-[var(--green)]" : "text-[var(--red)]"}>{summary.ai_final - amount > 0 ? '+' : ''}${(summary.ai_final - amount).toFixed(0)}</span></div>
              <div className="flex justify-between py-1 text-[12px] border-none"><span className="text-[var(--muted)]">Final Value</span><span className="text-[var(--green)]">${summary.ai_final.toLocaleString()}</span></div>
            </div>
          </div>
          
          <div className="text-center p-2.5 bg-[rgba(0,245,160,0.08)] border border-[rgba(0,245,160,0.2)] rounded-lg font-mono text-[11px] text-[var(--green)] tracking-[1px] mt-3 uppercase">
            {summary.ai_wins 
              ? `✦ AI STRATEGY OUTPERFORMS BY +$${((summary.ai_final - summary.baseline_final)).toFixed(0)} · +${summary.difference_pct.toFixed(1)}%`
              : `✦ AI STRATEGY UNDERPERFORMS BY -$${((summary.baseline_final - summary.ai_final)).toFixed(0)}`}
          </div>

          <div className="font-mono text-[10px] text-[var(--muted)] tracking-[2px] mt-4 mb-3">Performance Over Time</div>
          
          <div className="relative h-[160px] w-full min-h-[160px] min-w-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={simData}>
                <defs>
                  <linearGradient id="colorAi" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="rgba(0,245,160,0.12)" />
                    <stop offset="100%" stopColor="rgba(0,245,160,0)" />
                  </linearGradient>
                </defs>
                <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.03)" />
                <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 9 }} minTickGap={30} tickLine={false} axisLine={false} />
                <YAxis 
                  tick={{ fill: '#64748b', fontSize: 10 }} 
                  tickFormatter={(val) => `$${(val/1000).toFixed(1)}k`} 
                  axisLine={false} 
                  tickLine={false} 
                  domain={['dataMin - 500', 'dataMax + 500']}
                  width={40}
                />
                <Tooltip 
                  contentStyle={{ background: '#1a1c24', border: '1px solid #1e2230', borderRadius: '4px' }}
                  itemStyle={{ color: '#fff' }}
                  labelStyle={{ color: '#64748b', fontSize: '11px' }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '11px', color: '#64748b' }} />
                <Line type="monotone" dataKey="base" name="Without AI" stroke="#64748b" strokeWidth={1.5} dot={false} />
                <Line type="monotone" dataKey="ai" name="With AI" stroke="#00f5a0" strokeWidth={2} dot={false} fillOpacity={1} fill="url(#colorAi)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </>
  );
}
