export default function StatCard({ 
  label, 
  value, 
  valueColorClass = "", 
}: { 
  label: string, 
  value: React.ReactNode, 
  valueColorClass?: string, 
}) {
  return (
    <div className="bg-[var(--bg3)] rounded-lg p-3">
      <div className="text-[11px] text-[var(--muted)] mb-1 tracking-[0.5px]">{label}</div>
      {typeof value === "string" ? (
        <div className={`font-mono text-[18px] font-bold ${valueColorClass}`}>{value}</div>
      ) : (
        <div className="mt-1.5">{value}</div>
      )}
    </div>
  );
}
