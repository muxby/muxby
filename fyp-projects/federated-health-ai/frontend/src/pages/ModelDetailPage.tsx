import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { Spinner } from "../components/Spinner";
import { StatCard } from "../components/StatCard";
import { StatusBadge } from "../components/StatusBadge";
import { ErrorState } from "../components/States";
import { useFetch } from "../hooks/useFetch";
import { toast } from "../stores/uiStore";
import {
  formatCount,
  formatDateTime,
  formatMetric,
  formatParameters,
  formatPercent,
} from "../utils/format";

export function ModelDetailPage() {
  const params = useParams<{ id: string }>();
  const modelId = Number(params.id);
  const model = useFetch(() => api.getModel(modelId), [modelId]);
  const [activating, setActivating] = useState(false);

  if (!Number.isFinite(modelId)) {
    return <ErrorState message="Invalid model id." />;
  }
  if (model.loading) return <Spinner center />;
  if (model.error || !model.data) {
    return (
      <ErrorState
        message={model.error ?? "Model not found."}
        onRetry={model.reload}
      />
    );
  }

  const m = model.data;

  const onActivate = async () => {
    setActivating(true);
    try {
      const updated = await api.activateModel(m.id);
      model.setData(() => updated);
      toast("success", `Model ${updated.version} is now active.`);
    } catch (err) {
      toast("error", err instanceof Error ? err.message : "Activation failed");
    } finally {
      setActivating(false);
    }
  };

  return (
    <div className="stack">
      <div className="page-header">
        <div>
          <h1 className="row" style={{ gap: 10 }}>
            Model {m.version}{" "}
            <StatusBadge status={m.is_active ? "active" : "inactive"} />
          </h1>
          <div className="page-sub">
            <Link to="/models">Model registry</Link> / version #{m.id}
          </div>
        </div>
        {!m.is_active && (
          <button
            type="button"
            className="btn btn-primary"
            disabled={activating}
            onClick={onActivate}
          >
            {activating ? "Activating…" : "Activate this version"}
          </button>
        )}
      </div>

      <div className="grid-cards">
        <StatCard label="Accuracy" value={formatPercent(m.accuracy)} />
        <StatCard label="AUC" value={formatMetric(m.auc, 3)} />
        <StatCard label="Loss" value={formatMetric(m.loss)} />
        <StatCard
          label="Parameters"
          value={formatParameters(m.num_parameters)}
          sub={`${formatCount(m.num_parameters)} weights`}
        />
      </div>

      <div className="card" style={{ maxWidth: 520 }}>
        <div className="card-title">Provenance</div>
        <dl className="kv-list">
          <dt>Source training round</dt>
          <dd>
            <Link to={`/rounds/${m.round_id}`}>Round #{m.round_id}</Link>
          </dd>
          <dt>Created</dt>
          <dd>{formatDateTime(m.created_at)}</dd>
          <dt>Serving state</dt>
          <dd>{m.is_active ? "Serving predictions" : "Archived"}</dd>
        </dl>
      </div>
    </div>
  );
}
