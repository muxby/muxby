type Tone = "good" | "info" | "warning" | "critical" | "neutral";

const TONE_BY_STATUS: Record<string, Tone> = {
  online: "good",
  offline: "neutral",
  pending: "warning",
  running: "info",
  completed: "good",
  failed: "critical",
  cancelled: "neutral",
  active: "good",
  inactive: "neutral",
  low: "good",
  moderate: "warning",
  high: "critical",
};

const LABEL_BY_STATUS: Record<string, string> = {
  online: "Online",
  offline: "Offline",
  pending: "Pending",
  running: "Running",
  completed: "Completed",
  failed: "Failed",
  cancelled: "Cancelled",
  active: "Active",
  inactive: "Inactive",
  low: "Low",
  moderate: "Moderate",
  high: "High",
};

export interface StatusBadgeProps {
  status: string;
  label?: string;
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
  const tone = TONE_BY_STATUS[status] ?? "neutral";
  const text = label ?? LABEL_BY_STATUS[status] ?? status;
  return (
    <span className={`badge badge-${tone}`} data-status={status}>
      <span className="badge-dot" aria-hidden="true" />
      {text}
    </span>
  );
}
