import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { RoundStatus, TrainingRound } from "../api/types";
import { DataTable, type Column } from "../components/DataTable";
import { Spinner } from "../components/Spinner";
import { StatusBadge } from "../components/StatusBadge";
import { ErrorState } from "../components/States";
import { useFetch } from "../hooks/useFetch";
import {
  formatDateTime,
  formatMetric,
  formatPercent,
} from "../utils/format";

const FILTERS: Array<{ value: RoundStatus | "all"; label: string }> = [
  { value: "all", label: "All" },
  { value: "running", label: "Running" },
  { value: "pending", label: "Pending" },
  { value: "completed", label: "Completed" },
  { value: "failed", label: "Failed" },
  { value: "cancelled", label: "Cancelled" },
];

const COLUMNS: Column<TrainingRound>[] = [
  {
    key: "id",
    header: "Round",
    strong: true,
    render: (r) => <Link to={`/rounds/${r.id}`}>#{r.id}</Link>,
  },
  {
    key: "status",
    header: "Status",
    render: (r) => <StatusBadge status={r.status} />,
  },
  {
    key: "progress",
    header: "Progress",
    numeric: true,
    render: (r) => `${r.current_round}/${r.num_rounds}`,
  },
  {
    key: "epochs",
    header: "Local epochs",
    numeric: true,
    render: (r) => r.local_epochs,
  },
  {
    key: "privacy",
    header: "Privacy",
    render: (r) => (
      <span className="row" style={{ gap: 6 }}>
        {r.dp_enabled ? (
          <span className="badge badge-info">DP ε={r.dp_epsilon ?? "?"}</span>
        ) : (
          <span className="badge badge-neutral">No DP</span>
        )}
        {r.secure_aggregation && (
          <span className="badge badge-info">SecAgg</span>
        )}
      </span>
    ),
  },
  {
    key: "accuracy",
    header: "Accuracy",
    numeric: true,
    render: (r) => formatPercent(r.global_accuracy),
  },
  {
    key: "auc",
    header: "AUC",
    numeric: true,
    render: (r) => formatMetric(r.global_auc, 3),
  },
  {
    key: "created",
    header: "Started",
    render: (r) => formatDateTime(r.created_at),
  },
];

export function RoundsPage() {
  const navigate = useNavigate();
  const rounds = useFetch(() => api.listRounds(), []);
  const [filter, setFilter] = useState<RoundStatus | "all">("all");

  const filtered = (rounds.data ?? []).filter(
    (r) => filter === "all" || r.status === filter,
  );

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Training rounds</h1>
          <div className="page-sub">
            Federated averaging jobs across the hospital network.
          </div>
        </div>
        <Link to="/rounds/new" className="btn btn-primary">
          New training round
        </Link>
      </div>

      <div className="chip-row" role="tablist" aria-label="Filter by status">
        {FILTERS.map((f) => (
          <button
            key={f.value}
            type="button"
            className={`chip${filter === f.value ? " active" : ""}`}
            onClick={() => setFilter(f.value)}
          >
            {f.label}
          </button>
        ))}
      </div>

      {rounds.loading ? (
        <Spinner center />
      ) : rounds.error ? (
        <ErrorState message={rounds.error} onRetry={rounds.reload} />
      ) : (
        <DataTable
          columns={COLUMNS}
          rows={filtered}
          rowKey={(r) => r.id}
          emptyMessage={
            filter === "all"
              ? "No training rounds yet — launch the first one."
              : `No ${filter} rounds.`
          }
          onRowClick={(r) => navigate(`/rounds/${r.id}`)}
        />
      )}
    </div>
  );
}
