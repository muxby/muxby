import { beforeEach, describe, expect, it } from "vitest";
import { useAuthStore } from "../stores/authStore";
import type { User } from "../api/types";

const SAMPLE_USER: User = {
  id: 1,
  email: "clinician@example.org",
  full_name: "Test Clinician",
  role: "admin",
  created_at: "2026-01-01T00:00:00Z",
};

describe("authStore", () => {
  beforeEach(() => {
    window.localStorage.clear();
    useAuthStore.setState({ token: null, user: null });
  });

  it("starts without a token or user", () => {
    const state = useAuthStore.getState();
    expect(state.token).toBeNull();
    expect(state.user).toBeNull();
  });

  it("setToken stores the token in state and localStorage", () => {
    useAuthStore.getState().setToken("jwt-abc");
    expect(useAuthStore.getState().token).toBe("jwt-abc");
    expect(window.localStorage.getItem("fedhealth.token")).toBe("jwt-abc");
  });

  it("setUser stores the current user", () => {
    useAuthStore.getState().setUser(SAMPLE_USER);
    expect(useAuthStore.getState().user?.email).toBe("clinician@example.org");
  });

  it("logout clears token, user, and persisted storage", () => {
    useAuthStore.getState().setToken("jwt-abc");
    useAuthStore.getState().setUser(SAMPLE_USER);
    useAuthStore.getState().logout();
    const state = useAuthStore.getState();
    expect(state.token).toBeNull();
    expect(state.user).toBeNull();
    expect(window.localStorage.getItem("fedhealth.token")).toBeNull();
  });
});
