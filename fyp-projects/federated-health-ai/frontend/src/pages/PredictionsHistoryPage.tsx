import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { Prediction } from "../api/types";
import { DataTable, type Column } from "../components/DataTable";
import { Spinner } from "../components/Spinner";
import { StatusBadge } from "../components/StatusBadge";
import { ErrorState } from "../components/States";
import { useFetch } from "../hooks/useFetch";
import {
  diagnosisLabel,
  formatDateTime,
  formatPercent,
  riskLabel,
} from "../utils/format";

const COLUMNS: Column<Prediction>[] = [
  {
    key: "id",
    header: "ID",
    strong: true,
    render: (p) => `#${p.id}`,
  },
  {
    key: "probability",
    header: "Probability",
    numeric: true,
    render: (p) => formatPercent(p.probability),
  },
  {
    key: "risk",
    header: "Risk level",
    render: (p) => (
      <StatusBadge status={p.risk_level} label={riskLabel(p.risk_level)} />
    ),
  },
  {
    key: "diagnosis",
    header: "Diagnosis",
    render: (p) => diagnosisLabel(p.diagnosis),
  },
  {
    key: "patient",
    header: "Patient summary",
    render: (p) =>
      p.features
        ? `${p.features.age}y · ${p.features.sex === 1 ? "M" : "F"} · BMI ${
            p.features.bmi
          } · ${p.features.systolic_bp}/${p.features.diastolic_bp} mmHg`
        : "—",
  },
  {
    key: "model",
    header: "Model",
    render: (p) => p.model_version,
  },
  {
    key: "created",
    header: "Scored at",
    render: (p) => formatDateTime(p.created_at),
  },
];

export function PredictionsHistoryPage() {
  const predictions = useFetch(() => api.listPredictions(), []);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Prediction history</h1>
          <div className="page-sub">
            Every risk score produced by this deployment.
          </div>
        </div>
        <Link to="/predict" className="btn btn-primary">
          New prediction
        </Link>
      </div>

      {predictions.loading ? (
        <Spinner center />
      ) : predictions.error ? (
        <ErrorState message={predictions.error} onRetry={predictions.reload} />
      ) : (
        <DataTable
          columns={COLUMNS}
          rows={predictions.data ?? []}
          rowKey={(p) => p.id}
          emptyMessage="No predictions yet — run one from the Risk Prediction page."
        />
      )}
    </div>
  );
}
