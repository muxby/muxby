import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { ModelVersion } from "../api/types";
import { DataTable, type Column } from "../components/DataTable";
import { Spinner } from "../components/Spinner";
import { StatusBadge } from "../components/StatusBadge";
import { ErrorState } from "../components/States";
import { useFetch } from "../hooks/useFetch";
import { toast } from "../stores/uiStore";
import {
  formatDateTime,
  formatMetric,
  formatParameters,
  formatPercent,
} from "../utils/format";

export function ModelsPage() {
  const navigate = useNavigate();
  const models = useFetch(() => api.listModels(), []);
  const [activatingId, setActivatingId] = useState<number | null>(null);

  const onActivate = async (model: ModelVersion) => {
    setActivatingId(model.id);
    try {
      await api.activateModel(model.id);
      toast("success", `Model ${model.version} is now active.`);
      models.reload();
    } catch (err) {
      toast("error", err instanceof Error ? err.message : "Activation failed");
    } finally {
      setActivatingId(null);
    }
  };

  const columns: Column<ModelVersion>[] = [
    {
      key: "version",
      header: "Version",
      strong: true,
      render: (m) => <Link to={`/models/${m.id}`}>{m.version}</Link>,
    },
    {
      key: "state",
      header: "State",
      render: (m) => (
        <StatusBadge status={m.is_active ? "active" : "inactive"} />
      ),
    },
    {
      key: "round",
      header: "Source round",
      render: (m) => <Link to={`/rounds/${m.round_id}`}>#{m.round_id}</Link>,
    },
    {
      key: "accuracy",
      header: "Accuracy",
      numeric: true,
      render: (m) => formatPercent(m.accuracy),
    },
    {
      key: "auc",
      header: "AUC",
      numeric: true,
      render: (m) => formatMetric(m.auc, 3),
    },
    {
      key: "loss",
      header: "Loss",
      numeric: true,
      render: (m) => formatMetric(m.loss),
    },
    {
      key: "params",
      header: "Parameters",
      numeric: true,
      render: (m) => formatParameters(m.num_parameters),
    },
    {
      key: "created",
      header: "Created",
      render: (m) => formatDateTime(m.created_at),
    },
    {
      key: "actions",
      header: "",
      render: (m) =>
        m.is_active ? null : (
          <button
            type="button"
            className="btn btn-sm"
            disabled={activatingId === m.id}
            onClick={(e) => {
              e.stopPropagation();
              onActivate(m);
            }}
          >
            {activatingId === m.id ? "Activating…" : "Activate"}
          </button>
        ),
    },
  ];

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Model registry</h1>
          <div className="page-sub">
            Global model versions produced by federated training. The active
            version serves predictions.
          </div>
        </div>
      </div>

      {models.loading ? (
        <Spinner center />
      ) : models.error ? (
        <ErrorState message={models.error} onRetry={models.reload} />
      ) : (
        <DataTable
          columns={columns}
          rows={models.data ?? []}
          rowKey={(m) => m.id}
          emptyMessage="No model versions yet — complete a training round to publish one."
          onRowClick={(m) => navigate(`/models/${m.id}`)}
        />
      )}
    </div>
  );
}
