import type { Diagnosis, RiskLevel } from "../api/types";

/** Format a 0–1 fraction as a percentage, e.g. 0.9132 -> "91.3%". */
export function formatPercent(
  value: number | null | undefined,
  digits = 1,
): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "—";
  }
  return `${(value * 100).toFixed(digits)}%`;
}

/** Format a metric such as loss or AUC with fixed decimals. */
export function formatMetric(
  value: number | null | undefined,
  digits = 4,
): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "—";
  }
  return value.toFixed(digits);
}

/** Thousands-separated integer, e.g. 125000 -> "125,000". */
export function formatCount(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "—";
  }
  return value.toLocaleString("en-US");
}

/** Compact parameter count, e.g. 1_250_000 -> "1.25M". */
export function formatParameters(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "—";
  }
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return String(value);
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function riskLabel(level: RiskLevel): string {
  switch (level) {
    case "low":
      return "Low risk";
    case "moderate":
      return "Moderate risk";
    case "high":
      return "High risk";
  }
}

export type RiskTone = "good" | "warning" | "critical";

export function riskTone(level: RiskLevel): RiskTone {
  switch (level) {
    case "low":
      return "good";
    case "moderate":
      return "warning";
    case "high":
      return "critical";
  }
}

export function diagnosisLabel(diagnosis: Diagnosis): string {
  return diagnosis === "high_risk" ? "High risk" : "Low risk";
}
