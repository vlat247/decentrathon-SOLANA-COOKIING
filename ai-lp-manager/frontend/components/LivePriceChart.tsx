"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function LivePriceChart({ livePrice, liveSignal }: { livePrice?: number | null, liveSignal?: string | null }) {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    // initialize historical base array
    let base = livePrice ?? 185;
    const initialData = [];
    for (let i = 0; i < 30; i++) {
        base += (Math.random() - 0.48) * 2;
        initialData.push({ price: +base.toFixed(2), dotColor: 'transparent', dotRadius: 0 });
    }
    setData(initialData);
  }, []); // Only on mount

  // Watch for new data
  useEffect(() => {
    if (!livePrice) return;
    
    setData(prev => {
        const newData = [...prev.slice(1)];
        let dotColor = 'transparent';
        let dotRadius = 0;
        if (liveSignal === 'INCREASE') { dotColor = '#00f5a0'; dotRadius = 5; }
        else if (liveSignal === 'EXIT') { dotColor = '#f87171'; dotRadius = 5; }
        else if (liveSignal === 'HOLD') { dotColor = '#fbbf24'; dotRadius = 5; }
        
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

  return (
    <div className="bg-[var(--bg2)] border border-lp-border rounded-[10px] p-4">
      <div className="font-mono text-[10px] text-[var(--muted)] tracking-[2px] mb-3">SOL/USDC — Live Price + AI Decisions</div>
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
              domain={['dataMin - 5', 'dataMax + 5']}
              axisLine={false}
              tickLine={false}
              tickFormatter={(val) => `$${val.toFixed(0)}`}
              width={40}
            />
            <Tooltip 
              contentStyle={{ background: '#1a1c24', border: '1px solid #1e2230', borderRadius: '4px' }}
              itemStyle={{ color: '#fff' }}
              labelStyle={{ display: 'none' }}
              formatter={(val: any) => [`$${Number(val).toFixed(2)}`, 'Price']}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
