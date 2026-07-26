import { useNavigate } from "react-router-dom";
import { Spinner } from "../components/Spinner";
import { useAuthStore } from "../stores/authStore";
import { formatDateTime } from "../utils/format";

export function ProfilePage() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  if (!user) {
    return <Spinner center />;
  }

  return (
    <div className="stack" style={{ maxWidth: 520 }}>
      <div className="page-header">
        <div>
          <h1>Profile</h1>
          <div className="page-sub">Your account on this deployment.</div>
        </div>
      </div>

      <div className="card">
        <div className="card-title">Account</div>
        <dl className="kv-list">
          <dt>Full name</dt>
          <dd>{user.full_name}</dd>
          <dt>Email</dt>
          <dd>{user.email}</dd>
          <dt>Role</dt>
          <dd>
            <span className="badge badge-info">{user.role}</span>
          </dd>
          <dt>Member since</dt>
          <dd>{formatDateTime(user.created_at)}</dd>
        </dl>
      </div>

      <div className="card">
        <div className="card-title">Session</div>
        <p className="muted" style={{ marginTop: 0 }}>
          Signing out clears the access token from this browser.
        </p>
        <button
          type="button"
          className="btn btn-danger"
          onClick={() => {
            logout();
            navigate("/login");
          }}
        >
          Log out
        </button>
      </div>
    </div>
  );
}
