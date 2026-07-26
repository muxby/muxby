import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "../api/client";
import { LoginPage } from "../pages/LoginPage";
import { useAuthStore } from "../stores/authStore";

vi.mock("../api/client", () => ({
  api: {
    login: vi.fn(),
    me: vi.fn(),
  },
}));

const loginMock = vi.mocked(api.login);
const meMock = vi.mocked(api.me);

function renderLogin() {
  return render(
    <MemoryRouter initialEntries={["/login"]}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<div>dashboard-home</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("LoginPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.localStorage.clear();
    useAuthStore.setState({ token: null, user: null });
  });

  it("submits credentials, stores the session, and redirects to the dashboard", async () => {
    loginMock.mockResolvedValue({ access_token: "jwt-99", token_type: "bearer" });
    meMock.mockResolvedValue({
      id: 1,
      email: "doc@example.org",
      full_name: "Doc Example",
      role: "admin",
      created_at: "2026-01-01T00:00:00Z",
    });

    renderLogin();
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "doc@example.org" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "secret123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByText("dashboard-home")).toBeInTheDocument();
    expect(loginMock).toHaveBeenCalledWith("doc@example.org", "secret123");
    expect(useAuthStore.getState().token).toBe("jwt-99");
    expect(useAuthStore.getState().user?.email).toBe("doc@example.org");
  });

  it("shows the backend error and stays on the login page on failure", async () => {
    loginMock.mockRejectedValue(new Error("Incorrect email or password"));

    renderLogin();
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "doc@example.org" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "wrong" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(
      await screen.findByText("Incorrect email or password"),
    ).toBeInTheDocument();
    expect(screen.queryByText("dashboard-home")).not.toBeInTheDocument();
    expect(useAuthStore.getState().token).toBeNull();
  });
});
