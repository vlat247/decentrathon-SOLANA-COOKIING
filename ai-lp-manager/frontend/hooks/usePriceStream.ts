import { useEffect, useState } from 'react';

export function usePriceStream() {
  const [data, setData] = useState<{
    price: number | null;
    apy: number | null;
    signal: string | null;
    score: number | null;
    confidence: number | null;
    timestamp: string | null;
  } | null>(null);

  useEffect(() => {
    let ws: WebSocket;
    let retryTimeout: NodeJS.Timeout;

    function connect() {
      ws = new WebSocket('ws://localhost:8000/ws/prices');

      ws.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        setData({
          price:      msg.price,
          apy:        msg.apy,
          signal:     msg.action ?? msg.ai_signal,   // "INCREASE" | "HOLD" | "EXIT"
          score:      msg.score,
          confidence: msg.confidence,
          timestamp:  msg.timestamp,
        });
      };

      ws.onclose = () => {
        // backend streams every 10s — auto-reconnect on drop
        retryTimeout = setTimeout(connect, 3000);
      };
    }

    connect();
    return () => { ws?.close(); clearTimeout(retryTimeout); };
  }, []);

  return data;
}
