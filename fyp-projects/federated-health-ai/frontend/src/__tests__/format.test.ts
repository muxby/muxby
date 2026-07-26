import { describe, expect, it } from "vitest";
import {
  diagnosisLabel,
  formatCount,
  formatMetric,
  formatParameters,
  formatPercent,
  riskLabel,
  riskTone,
} from "../utils/format";

describe("format utilities", () => {
  it("formats fractions as percentages", () => {
    expect(formatPercent(0.9132)).toBe("91.3%");
    expect(formatPercent(0)).toBe("0.0%");
    expect(formatPercent(1, 0)).toBe("100%");
    expect(formatPercent(null)).toBe("—");
    expect(formatPercent(undefined)).toBe("—");
  });

  it("formats metrics with fixed decimals", () => {
    expect(formatMetric(0.123456)).toBe("0.1235");
    expect(formatMetric(0.87654, 3)).toBe("0.877");
    expect(formatMetric(null)).toBe("—");
  });

  it("formats counts with thousands separators", () => {
    expect(formatCount(125000)).toBe("125,000");
    expect(formatCount(0)).toBe("0");
    expect(formatCount(null)).toBe("—");
  });

  it("formats parameter counts compactly", () => {
    expect(formatParameters(1_250_000)).toBe("1.25M");
    expect(formatParameters(48_500)).toBe("48.5K");
    expect(formatParameters(950)).toBe("950");
    expect(formatParameters(null)).toBe("—");
  });

  it("labels risk levels for clinicians", () => {
    expect(riskLabel("low")).toBe("Low risk");
    expect(riskLabel("moderate")).toBe("Moderate risk");
    expect(riskLabel("high")).toBe("High risk");
  });

  it("maps risk levels onto status tones", () => {
    expect(riskTone("low")).toBe("good");
    expect(riskTone("moderate")).toBe("warning");
    expect(riskTone("high")).toBe("critical");
  });

  it("labels diagnoses", () => {
    expect(diagnosisLabel("high_risk")).toBe("High risk");
    expect(diagnosisLabel("low_risk")).toBe("Low risk");
  });
});
