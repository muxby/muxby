import type { ReactNode } from "react";

export interface StatCardProps {
  label: string;
  value: ReactNode;
  sub?: ReactNode;
}

export function StatCard({ label, value, sub }: StatCardProps) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {sub !== undefined && <div className="stat-sub">{sub}</div>}
    </div>
  );
}
