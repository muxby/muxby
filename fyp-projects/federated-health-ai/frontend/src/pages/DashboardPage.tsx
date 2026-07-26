import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { TrainingRound } from "../api/types";
import { DataTable, type Column } from "../components/DataTable";
import { CHART_COLORS, MetricLineChart } from "../components/MetricLineChart";
import { Spinner } from "../components/Spinner";
import { StatCard } from "../components/StatCard";
import { StatusBadge } from "../components/StatusBadge";
import { EmptyState, ErrorState } from "../components/States";
import { useFetch } from "../hooks/useFetch";
import {
  formatCount,
  formatDateTime,
  formatMetric,
  formatPercent,
} from "../utils/format";

const ROUND_COLUMNS: Column<TrainingRound>[] = [
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

export function DashboardPage() {
  const navigate = useNavigate();
  const stats = useFetch(() => api.statsOverview(), []);
  const rounds = useFetch(() => api.listRounds(), []);
  const lastRoundId = stats.data?.last_round?.id ?? null;
  const lastRound = useFetch(
    () =>
      lastRoundId === null
        ? Promise.resolve(null)
        : api.getRound(lastRoundId),
    [lastRoundId],
  );

  if (stats.loading) return <Spinner center />;
  if (stats.error) {
    return <ErrorState message={stats.error} onRetry={stats.reload} />;
  }

  const s = stats.data;
  const recentRounds = (rounds.data ?? []).slice(0, 6);
  const history = lastRound.data?.history ?? [];

  return (
    <div className="stack">
      <div className="grid-cards">
        <StatCard
          label="Hospitals"
          value={formatCount(s?.hospitals ?? 0)}
          sub={`${formatCount(s?.hospitals_online ?? 0)} online`}
        />
        <StatCard
          label="Rounds completed"
          value={formatCount(s?.rounds_completed ?? 0)}
          sub={
            s?.last_round
              ? `Last round #${s.last_round.id}`
              : "No rounds yet"
          }
        />
        <StatCard
          label="Active model accuracy"
          value={formatPercent(s?.active_model_accuracy)}
          sub={`AUC ${formatMetric(s?.active_model_auc, 3)}`}
        />
        <StatCard
          label="Predictions made"
          value={formatCount(s?.predictions_made ?? 0)}
          sub="via the active model"
        />
      </div>

      <div className="card">
        <div className="card-title">
          <span>
            Accuracy trend
            {s?.last_round ? ` — round #${s.last_round.id}` : ""}
          </span>
          {s?.last_round && (
            <Link to={`/rounds/${s.last_round.id}`}>View round</Link>
          )}
        </div>
        {lastRound.loading && lastRoundId !== null ? (
          <Spinner center />
        ) : lastRound.error ? (
          <ErrorState message={lastRound.error} onRetry={lastRound.reload} />
        ) : history.length === 0 ? (
          <EmptyState
            title="No training history yet"
            message="Launch a training round to see the global accuracy trend here."
          />
        ) : (
          <MetricLineChart
            data={history}
            xKey="round_number"
            xLabel="Round"
            yDomain={[0, 1]}
            yFormatter={(v) => `${Math.round(v * 100)}%`}
            series={[
              {
                key: "accuracy",
                label: "Accuracy",
                color: CHART_COLORS.accuracy,
              },
              { key: "auc", label: "AUC", color: CHART_COLORS.auc },
            ]}
          />
        )}
      </div>

      <div>
        <div className="page-header">
          <h1 style={{ fontSize: 16 }}>Recent training rounds</h1>
          <Link to="/rounds" className="btn btn-sm">
            View all
          </Link>
        </div>
        {rounds.loading ? (
          <Spinner center />
        ) : rounds.error ? (
          <ErrorState message={rounds.error} onRetry={rounds.reload} />
        ) : (
          <DataTable
            columns={ROUND_COLUMNS}
            rows={recentRounds}
            rowKey={(r) => r.id}
            emptyMessage="No training rounds yet — start one from the Training Rounds page."
            onRowClick={(r) => navigate(`/rounds/${r.id}`)}
          />
        )}
      </div>
    </div>
  );
}
