import { useEffect } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuthStore } from "../stores/authStore";
import { ToastStack } from "./Toast";

interface NavItem {
  to: string;
  label: string;
  end?: boolean;
}

const NAV_SECTIONS: Array<{ title: string; items: NavItem[] }> = [
  {
    title: "Overview",
    items: [{ to: "/", label: "Dashboard", end: true }],
  },
  {
    title: "Federation",
    items: [
      { to: "/hospitals", label: "Hospitals" },
      { to: "/rounds", label: "Training Rounds" },
      { to: "/models", label: "Model Registry" },
    ],
  },
  {
    title: "Inference",
    items: [
      { to: "/predict", label: "Risk Prediction" },
      { to: "/predictions", label: "Prediction History" },
    ],
  },
  {
    title: "System",
    items: [
      { to: "/audit", label: "Audit Log" },
      { to: "/profile", label: "Profile" },
    ],
  },
];

const TITLES: Array<[RegExp, string]> = [
  [/^\/$/, "Dashboard"],
  [/^\/hospitals\/\d+/, "Hospital Detail"],
  [/^\/hospitals/, "Hospitals"],
  [/^\/rounds\/new/, "New Training Round"],
  [/^\/rounds\/\d+/, "Training Round"],
  [/^\/rounds/, "Training Rounds"],
  [/^\/models\/\d+/, "Model Version"],
  [/^\/models/, "Model Registry"],
  [/^\/predictions/, "Prediction History"],
  [/^\/predict/, "Risk Prediction"],
  [/^\/audit/, "Audit Log"],
  [/^\/profile/, "Profile"],
];

export function AppLayout() {
  const user = useAuthStore((s) => s.user);
  const token = useAuthStore((s) => s.token);
  const setUser = useAuthStore((s) => s.setUser);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (token && !user) {
      api
        .me()
        .then(setUser)
        .catch(() => {
          // A 401 already cleared the session via the client interceptor;
          // any other failure leaves the user header blank until reload.
        });
    }
  }, [token, user, setUser]);

  const title =
    TITLES.find(([pattern]) => pattern.test(location.pathname))?.[1] ??
    "FedHealth AI";

  const initials = user
    ? user.full_name
        .split(/\s+/)
        .map((p) => p[0])
        .slice(0, 2)
        .join("")
        .toUpperCase()
    : "·";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark">FH</div>
          <div>
            <span className="brand-name">FedHealth AI</span>
            <span className="brand-sub">Federated Learning</span>
          </div>
        </div>
        <nav className="sidebar-nav">
          {NAV_SECTIONS.map((section) => (
            <div key={section.title}>
              <div className="nav-section">{section.title}</div>
              {section.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) =>
                    `nav-link${isActive ? " active" : ""}`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
      </aside>
      <div className="main-column">
        <header className="topbar">
          <div className="topbar-title">{title}</div>
          <div className="topbar-user">
            <div className="topbar-avatar">{initials}</div>
            <span>{user?.email ?? ""}</span>
            <button
              type="button"
              className="btn btn-sm"
              onClick={() => {
                logout();
                navigate("/login");
              }}
            >
              Log out
            </button>
          </div>
        </header>
        <main className="page">
          <Outlet />
        </main>
      </div>
      <ToastStack />
    </div>
  );
}
