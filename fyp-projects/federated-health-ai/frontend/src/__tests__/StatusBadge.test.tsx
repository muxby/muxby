import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusBadge } from "../components/StatusBadge";

describe("StatusBadge", () => {
  it("renders a friendly label for known statuses", () => {
    render(<StatusBadge status="running" />);
    const badge = screen.getByText("Running");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("badge", "badge-info");
  });

  it("maps completed to the good tone", () => {
    render(<StatusBadge status="completed" />);
    expect(screen.getByText("Completed")).toHaveClass("badge-good");
  });

  it("maps failed to the critical tone", () => {
    render(<StatusBadge status="failed" />);
    expect(screen.getByText("Failed")).toHaveClass("badge-critical");
  });

  it("falls back to a neutral tone and raw text for unknown statuses", () => {
    render(<StatusBadge status="archived" />);
    expect(screen.getByText("archived")).toHaveClass("badge-neutral");
  });

  it("prefers an explicit label when provided", () => {
    render(<StatusBadge status="high" label="High risk" />);
    expect(screen.getByText("High risk")).toHaveClass("badge-critical");
  });
});
