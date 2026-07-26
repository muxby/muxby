import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";
import { ProtectedRoute } from "../components/ProtectedRoute";
import { useAuthStore } from "../stores/authStore";

function renderGuarded() {
  return render(
    <MemoryRouter initialEntries={["/secure"]}>
      <Routes>
        <Route path="/login" element={<div>login-screen</div>} />
        <Route
          path="/secure"
          element={
            <ProtectedRoute>
              <div>secure-content</div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ProtectedRoute", () => {
  beforeEach(() => {
    window.localStorage.clear();
    useAuthStore.setState({ token: null, user: null });
  });

  it("redirects to /login when no token is present", () => {
    renderGuarded();
    expect(screen.getByText("login-screen")).toBeInTheDocument();
    expect(screen.queryByText("secure-content")).not.toBeInTheDocument();
  });

  it("renders the protected content when a token exists", () => {
    useAuthStore.setState({ token: "jwt-ok" });
    renderGuarded();
    expect(screen.getByText("secure-content")).toBeInTheDocument();
    expect(screen.queryByText("login-screen")).not.toBeInTheDocument();
  });
});
