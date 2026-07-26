import { useState, type FormEvent } from "react";
import { api } from "../api/client";
import type { Prediction, PredictionInput } from "../api/types";
import { ProbabilityGauge } from "../components/ProbabilityGauge";
import { StatusBadge } from "../components/StatusBadge";
import { EmptyState } from "../components/States";
import { diagnosisLabel, formatDateTime, riskLabel } from "../utils/format";

interface NumericField {
  key: keyof PredictionInput;
  label: string;
  unit: string;
  min: number;
  max: number;
  step: number;
  initial: string;
}

const NUMERIC_FIELDS: NumericField[] = [
  { key: "age", label: "Age", unit: "years", min: 18, max: 100, step: 1, initial: "55" },
  { key: "systolic_bp", label: "Systolic BP", unit: "mmHg", min: 80, max: 250, step: 1, initial: "130" },
  { key: "diastolic_bp", label: "Diastolic BP", unit: "mmHg", min: 40, max: 150, step: 1, initial: "85" },
  { key: "cholesterol", label: "Total cholesterol", unit: "mg/dL", min: 100, max: 400, step: 1, initial: "210" },
  { key: "hdl", label: "HDL cholesterol", unit: "mg/dL", min: 20, max: 120, step: 1, initial: "50" },
  { key: "bmi", label: "BMI", unit: "kg/m²", min: 12, max: 60, step: 0.1, initial: "27.5" },
  { key: "glucose", label: "Fasting glucose", unit: "mg/dL", min: 50, max: 300, step: 1, initial: "98" },
];

type NumericValues = Record<string, string>;

export function PredictPage() {
  const [values, setValues] = useState<NumericValues>(() =>
    Object.fromEntries(NUMERIC_FIELDS.map((f) => [f.key, f.initial])),
  );
  const [sex, setSex] = useState<0 | 1>(0);
  const [smoker, setSmoker] = useState(false);
  const [familyHistory, setFamilyHistory] = useState(false);
  const [result, setResult] = useState<Prediction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    for (const f of NUMERIC_FIELDS) {
      const v = Number(values[f.key]);
      if (!Number.isFinite(v) || v < f.min || v > f.max) {
        setError(`${f.label} must be between ${f.min} and ${f.max} ${f.unit}.`);
        return;
      }
    }
    setSubmitting(true);
    try {
      const payload: PredictionInput = {
        age: Number(values.age),
        sex,
        systolic_bp: Number(values.systolic_bp),
        diastolic_bp: Number(values.diastolic_bp),
        cholesterol: Number(values.cholesterol),
        hdl: Number(values.hdl),
        bmi: Number(values.bmi),
        glucose: Number(values.glucose),
        smoker: smoker ? 1 : 0,
        family_history: familyHistory ? 1 : 0,
      };
      const prediction = await api.createPrediction(payload);
      setResult(prediction);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Cardiovascular risk prediction</h1>
          <div className="page-sub">
            Runs the active global model on a single patient record. Data never
            leaves this deployment.
          </div>
        </div>
      </div>

      <div className="grid-two">
        <form className="card" onSubmit={onSubmit}>
          <div className="card-title">Patient features</div>
          {error && <div className="form-error">{error}</div>}
          <div className="form-grid">
            {NUMERIC_FIELDS.map((f) => (
              <div className="field" key={f.key}>
                <label htmlFor={`pf-${f.key}`}>
                  {f.label} <span className="muted">({f.unit})</span>
                </label>
                <input
                  id={`pf-${f.key}`}
                  className="input"
                  type="number"
                  min={f.min}
                  max={f.max}
                  step={f.step}
                  required
                  value={values[f.key]}
                  onChange={(e) =>
                    setValues((prev) => ({ ...prev, [f.key]: e.target.value }))
                  }
                />
                <span className="hint">
                  {f.min}–{f.max} {f.unit}
                </span>
              </div>
            ))}
            <div className="field">
              <label htmlFor="pf-sex">Sex</label>
              <select
                id="pf-sex"
                className="input"
                value={sex}
                onChange={(e) => setSex(Number(e.target.value) === 1 ? 1 : 0)}
              >
                <option value={0}>Female</option>
                <option value={1}>Male</option>
              </select>
            </div>
          </div>
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={smoker}
              onChange={(e) => setSmoker(e.target.checked)}
            />
            Current smoker
          </label>
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={familyHistory}
              onChange={(e) => setFamilyHistory(e.target.checked)}
            />
            Family history of cardiovascular disease
          </label>
          <div className="modal-actions" style={{ marginTop: 14 }}>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting}
            >
              {submitting ? "Scoring…" : "Run prediction"}
            </button>
          </div>
        </form>

        <div className="card">
          <div className="card-title">Result</div>
          {result === null ? (
            <EmptyState
              title="No prediction yet"
              message="Fill in the patient features and run a prediction to see the risk assessment."
            />
          ) : (
            <div className="stack" style={{ alignItems: "center" }}>
              <ProbabilityGauge
                probability={result.probability}
                riskLevel={result.risk_level}
              />
              <StatusBadge
                status={result.risk_level}
                label={riskLabel(result.risk_level)}
              />
              <dl className="kv-list" style={{ width: "100%" }}>
                <dt>Diagnosis</dt>
                <dd>{diagnosisLabel(result.diagnosis)}</dd>
                <dt>Model version</dt>
                <dd>{result.model_version}</dd>
                <dt>Scored at</dt>
                <dd>{formatDateTime(result.created_at)}</dd>
              </dl>
              <div className="chart-note">
                This score supports, and never replaces, clinical judgement.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
