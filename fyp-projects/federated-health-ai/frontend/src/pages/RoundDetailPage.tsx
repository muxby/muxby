import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { RoundHistoryPoint, RoundSocketEvent } from "../api/types";
import { DataTable, type Column } from "../components/DataTable";
import { CHART_COLORS, MetricLineChart } from "../components/MetricLineChart";
import { Spinner } from "../components/Spinner";
import { StatCard } from "../components/StatCard";
import { StatusBadge } from "../components/StatusBadge";
import { EmptyState, ErrorState } from "../components/States";
import { useFetch } from "../hooks/useFetch";
import { useRoundSocket } from "../hooks/useRoundSocket";
import { toast } from "../stores/uiStore";
import {
  formatCount,
  formatDateTime,
  formatMetric,
  formatPercent,
} from "../utils/format";

interface UpdateRow {
  key: string;
  hospital_name: string;
  round_number: number;
  num_samples: number | null;
  local_accuracy: number;
  local_loss: number;
  update_norm: number | null;
  created_at: string | null;
}

const UPDATE_COLUMNS: Column<UpdateRow>[] = [
  {
    key: "hospital",
    header: "Hospital",
    strong: true,
    render: (u) => u.hospital_name,
  },
  {
    key: "round",
    header: "Round",
    numeric: true,
    render: (u) => u.round_number,
  },
  {
    key: "samples",
    header: "Samples",
    numeric: true,
    render: (u) => formatCount(u.num_samples),
  },
  {
    key: "acc",
    header: "Local accuracy",
    numeric: true,
    render: (u) => formatPercent(u.local_accuracy),
  },
  {
    key: "loss",
    header: "Local loss",
    numeric: true,
    render: (u) => formatMetric(u.local_loss),
  },
  {
    key: "norm",
    header: "Update norm",
    numeric: true,
    render: (u) => formatMetric(u.update_norm, 3),
  },
  {
    key: "at",
    header: "Received",
    render: (u) => formatDateTime(u.created_at),
  },
];

function upsertHistory(
  history: RoundHistoryPoint[],
  point: RoundHistoryPoint,
): RoundHistoryPoint[] {
  const without = history.filter(
    (p) => p.round_number !== point.round_number,
  );
  return [...without, point].sort((a, b) => a.round_number - b.round_number);
}

interface LiveUpdate {
  hospital_name: string;
  round_number: number;
  local_accuracy: number;
  local_loss: number;
}

export function RoundDetailPage() {
  const params = useParams<{ id: string }>();
  const roundId = Number(params.id);
  const round = useFetch(() => api.getRound(roundId), [roundId]);
  const [liveUpdates, setLiveUpdates] = useState<LiveUpdate[]>([]);
  const [cancelling, setCancelling] = useState(false);
  const setData = round.setData;

  const silentRefresh = useCallback(() => {
    api
      .getRound(roundId)
      .then((fresh) => setData(() => fresh))
      .catch(() => {
        // keep showing the last known state; the next poll retries
      });
  }, [roundId, setData]);

  const onSocketEvent = useCallback(
    (event: RoundSocketEvent) => {
      if (event.type === "round_progress") {
        setData((prev) =>
          prev
            ? {
                ...prev,
                current_round: event.round_number,
                num_rounds: event.total_rounds,
                global_accuracy: event.accuracy,
                global_auc: event.auc,
                global_loss: event.loss,
                history: upsertHistory(prev.history, {
                  round_number: event.round_number,
                  accuracy: event.accuracy,
                  auc: event.auc,
                  loss: event.loss,
                }),
              }
            : prev,
        );
      } else if (event.type === "client_update") {
        setLiveUpdates((prev) => [
          ...prev,
          {
            hospital_name: event.hospital_name,
            round_number: event.round_number,
            local_accuracy: event.local_accuracy,
            local_loss: event.local_loss,
          },
        ]);
      } else if (event.type === "status") {
        setData((prev) => (prev ? { ...prev, status: event.status } : prev));
        if (event.status !== "running" && event.status !== "pending") {
          silentRefresh();
        }
      }
    },
    [setData, silentRefresh],
  );

  const status = round.data?.status;
  const isLive = status === "running" || status === "pending";
  const { connected } = useRoundSocket(
    Number.isFinite(roundId) ? roundId : null,
    isLive,
    onSocketEvent,
  );

  useEffect(() => {
    if (!isLive || connected) return;
    const timer = window.setInterval(silentRefresh, 4000);
    return () => window.clearInterval(timer);
  }, [isLive, connected, silentRefresh]);

  if (!Number.isFinite(roundId)) {
    return <ErrorState message="Invalid round id." />;
  }
  if (round.loading) return <Spinner center />;
  if (round.error || !round.data) {
    return (
      <ErrorState
        message={round.error ?? "Round not found."}
        onRetry={round.reload}
      />
    );
  }

  const r = round.data;
  const progress =
    r.num_rounds > 0 ? Math.min(1, r.current_round / r.num_rounds) : 0;

  const fetchedRows: UpdateRow[] = r.updates.map((u) => ({
    key: `f-${u.id}`,
    hospital_name: u.hospital_name,
    round_number: u.round_number,
    num_samples: u.num_samples,
    local_accuracy: u.local_accuracy,
    local_loss: u.local_loss,
    update_norm: u.update_norm,
    created_at: u.created_at,
  }));
  const seen = new Set(
    fetchedRows.map((u) => `${u.hospital_name}|${u.round_number}`),
  );
  const liveRows: UpdateRow[] = liveUpdates
    .filter((u) => !seen.has(`${u.hospital_name}|${u.round_number}`))
    .map((u, i) => ({
      key: `l-${i}`,
      hospital_name: u.hospital_name,
      round_number: u.round_number,
      num_samples: null,
      local_accuracy: u.local_accuracy,
      local_loss: u.local_loss,
      update_norm: null,
      created_at: null,
    }));
  const updateRows = [...fetchedRows, ...liveRows].sort(
    (a, b) => b.round_number - a.round_number,
  );

  const onCancel = async () => {
    setCancelling(true);
    try {
      const cancelled = await api.cancelRound(r.id);
      setData((prev) => (prev ? { ...prev, ...cancelled } : prev));
      toast("info", `Round #${r.id} cancelled.`);
    } catch (err) {
      toast("error", err instanceof Error ? err.message : "Cancel failed");
    } finally {
      setCancelling(false);
    }
  };

  return (
    <div className="stack">
      <div className="page-header">
        <div>
          <h1 className="row" style={{ gap: 10 }}>
            Training round #{r.id} <StatusBadge status={r.status} />
          </h1>
          <div className="page-sub">
            <Link to="/rounds">Training rounds</Link> / started{" "}
            {formatDateTime(r.created_at)}
            {r.completed_at
              ? ` · finished ${formatDateTime(r.completed_at)}`
              : ""}
          </div>
        </div>
        <div className="row">
          {isLive && (
            <span className={`live-dot${connected ? "" : " polling"}`}>
              {connected ? "live" : "polling"}
            </span>
          )}
          {isLive && (
            <button
              type="button"
              className="btn btn-danger"
              disabled={cancelling}
              onClick={onCancel}
            >
              {cancelling ? "Cancelling…" : "Cancel round"}
            </button>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-title">
          <span>
            Progress — round {r.current_round} of {r.num_rounds}
          </span>
          <span className="muted">{Math.round(progress * 100)}%</span>
        </div>
        <div className="progress-track">
          <div
            className={`progress-fill${isLive ? " progress-live" : ""}`}
            style={{ width: `${progress * 100}%` }}
          />
        </div>
      </div>

      <div className="grid-cards">
        <StatCard
          label="Global accuracy"
          value={formatPercent(r.global_accuracy)}
        />
        <StatCard label="Global AUC" value={formatMetric(r.global_auc, 3)} />
        <StatCard label="Global loss" value={formatMetric(r.global_loss)} />
        <StatCard
          label="Configuration"
          value={`${r.num_rounds} × ${r.local_epochs} epochs`}
          sub={`${r.dp_enabled ? `DP ε=${r.dp_epsilon ?? "?"}` : "No DP"} · ${
            r.secure_aggregation ? "SecAgg on" : "SecAgg off"
          }`}
        />
      </div>

      <div className="grid-two">
        <div className="card">
          <div className="card-title">Global accuracy & AUC</div>
          {r.history.length === 0 ? (
            <EmptyState
              title="Waiting for the first aggregation"
              message="Metrics appear as soon as the first federated round completes."
            />
          ) : (
            <MetricLineChart
              data={r.history}
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
        <div className="card">
          <div className="card-title">Global loss</div>
          {r.history.length === 0 ? (
            <EmptyState
              title="Waiting for the first aggregation"
              message="Loss appears once the first federated round completes."
            />
          ) : (
            <MetricLineChart
              data={r.history}
              xKey="round_number"
              xLabel="Round"
              series={[
                { key: "loss", label: "Loss", color: CHART_COLORS.loss },
              ]}
            />
          )}
        </div>
      </div>

      <div>
        <div className="card-title" style={{ marginBottom: 10 }}>
          Client updates
        </div>
        <DataTable
          columns={UPDATE_COLUMNS}
          rows={updateRows}
          rowKey={(u) => u.key}
          emptyMessage="No client updates received yet."
        />
      </div>
    </div>
  );
}
