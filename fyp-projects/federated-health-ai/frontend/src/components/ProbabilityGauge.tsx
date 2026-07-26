import { formatPercent } from "../utils/format";
import type { RiskLevel } from "../api/types";

const RISK_COLOR: Record<RiskLevel, string> = {
  low: "#0ca30c",
  moderate: "#fab219",
  high: "#d03b3b",
};

export interface ProbabilityGaugeProps {
  probability: number;
  riskLevel: RiskLevel;
}

/** Semi-circular gauge showing predicted disease probability. */
export function ProbabilityGauge({
  probability,
  riskLevel,
}: ProbabilityGaugeProps) {
  const clamped = Math.max(0, Math.min(1, probability));
  const radius = 80;
  const circumference = Math.PI * radius;
  const filled = circumference * clamped;
  const color = RISK_COLOR[riskLevel];

  return (
    <div className="gauge-wrap">
      <svg width="200" height="112" viewBox="0 0 200 112" role="img" aria-label={`Predicted probability ${formatPercent(clamped)}`}>
        <path
          d={`M 20 100 A ${radius} ${radius} 0 0 1 180 100`}
          fill="none"
          stroke="#2a2a28"
          strokeWidth="14"
          strokeLinecap="round"
        />
        <path
          d={`M 20 100 A ${radius} ${radius} 0 0 1 180 100`}
          fill="none"
          stroke={color}
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray={`${filled} ${circumference}`}
        />
      </svg>
      <div className="gauge-value" style={{ marginTop: -46 }}>
        {formatPercent(clamped)}
      </div>
      <div className="muted" style={{ fontSize: 12 }}>
        predicted probability
      </div>
    </div>
  );
}
