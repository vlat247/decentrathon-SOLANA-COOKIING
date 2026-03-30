"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function LivePriceChart({ livePrice, liveSignal }: { livePrice?: number | null, liveSignal?: string | null }) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // STEP 2 & 6: Backend as Single Source of Truth
  useEffect(() => {
    async function fetchHistory() {
      try {
        const res = await fetch("http://localhost:8000/api/price-history/SOL?days=1");
        if (!res.ok) throw new Error("Failed to fetch from backend");
        const json = await res.json();
        
        // STEP 5: Add data flow clarity
        console.log("PRICE HISTORY FROM BACKEND:", json);

        if (!Array.isArray(json) || json.length === 0) {
            setError(true);
            setLoading(false);
            return;
        }

        const formatted = json.map((pt: any) => ({
            price: Number(pt.price).toFixed(2),
            timestamp: pt.timestamp,
            dotColor: 'transparent',
            dotRadius: 0
        }));
        
        setData(formatted);
        setLoading(false);
      } catch (err) {
        console.error("Market data fetch error:", err);
        setError(true);
        setLoading(false);
      }
    }
    
    fetchHistory();
  }, []);

  // Watch for new websocket data to append to the historical chart
  useEffect(() => {
    if (!livePrice || data.length === 0 || livePrice === 0.0) return;
    
    // STEP 5: Add data flow clarity
    console.log("PRICE FROM BACKEND:", livePrice);
    
    setData(prev => {
        // limit arrays to 60 items so chart continues scrolling linearly
        const newData = prev.length >= 60 ? [...prev.slice(1)] : [...prev];
        
        let dotColor = 'transparent';
        let dotRadius = 0;
        if (liveSignal === 'INCREASE') { dotColor = '#00f5a0'; dotRadius = 5; }
        else if (liveSignal === 'EXIT') { dotColor = '#f87171'; dotRadius = 5; }
        else if (liveSignal === 'REDUCE') { dotColor = '#fbbf24'; dotRadius = 5; } // yellow for reduce
        else if (liveSignal === 'HOLD') { dotColor = '#a78bfa'; dotRadius = 3; } // smaller dot for hold
        
        newData.push({
          price: +(livePrice).toFixed(2),
          dotColor,
          dotRadius
        });
        return newData;
    });
  }, [livePrice, liveSignal]);

  const renderDot = (props: any) => {
    const { cx, cy, payload } = props;
    if (payload.dotRadius === 0) return null;
    return (
      <circle cx={cx} cy={cy} r={payload.dotRadius} fill={payload.dotColor} key={`dot-${cx}-${cy}`} />
    );
  };

  // STEP 7: UI BEHAVIOR RULES
  if (loading) {
      return (
        <div className="bg-[var(--bg2)] border border-lp-border rounded-[10px] p-4 flex items-center justify-center h-[230px]">
            <span className="font-mono text-xs text-[var(--muted)] animate-pulse">Loading real market data from backend...</span>
        </div>
      );
  }

  if (error || data.length === 0) {
      return (
        <div className="bg-[var(--bg2)] border border-lp-border rounded-[10px] p-4 flex items-center justify-center h-[230px]">
            <span className="font-mono text-xs text-[#f87171]">Market data temporarily unavailable</span>
        </div>
      );
  }

  return (
    <div className="bg-[var(--bg2)] border border-lp-border rounded-[10px] p-4">
      <div className="flex justify-between items-center mb-3">
        <div className="font-mono text-[10px] text-[var(--muted)] tracking-[2px]">SOL/USDC — Live Price & Decisions</div>
        {/* STEP 8: Price Source Label */}
        <div className="text-[10px] text-[var(--green)] opacity-80 border border-[var(--green)] px-2 py-0.5 rounded">
            Price Source: Live Market (CoinGecko)
        </div>
      </div>
      <div className="relative h-[180px] w-full min-h-[180px] min-w-[200px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="rgba(167,139,250,0.18)" />
                <stop offset="100%" stopColor="rgba(167,139,250,0)" />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.04)" />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke="#a78bfa" 
              strokeWidth={2} 
              dot={renderDot as any}
              fillOpacity={1}
              fill="url(#colorPrice)"
              isAnimationActive={false}
            />
            <YAxis 
              tick={{ fill: '#64748b', fontSize: 10 }} 
              domain={['auto', 'auto']}
              axisLine={false}
              tickLine={false}
              tickFormatter={(val) => `$${val.toFixed(0)}`}
              width={40}
            />
            <Tooltip 
              contentStyle={{ background: '#1a1c24', border: '1px solid #1e2230', borderRadius: '4px' }}
              itemStyle={{ color: '#fff' }}
              labelStyle={{ display: 'none' }}
              formatter={(val: any) => [`$${Number(val).toFixed(2)}`, 'Market Price']}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
