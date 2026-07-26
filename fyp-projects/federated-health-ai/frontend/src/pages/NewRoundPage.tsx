import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { Spinner } from "../components/Spinner";
import { StatusBadge } from "../components/StatusBadge";
import { EmptyState, ErrorState } from "../components/States";
import { useFetch } from "../hooks/useFetch";
import { toast } from "../stores/uiStore";
import { formatCount } from "../utils/format";

export function NewRoundPage() {
  const navigate = useNavigate();
  const hospitals = useFetch(() => api.listHospitals(), []);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [numRounds, setNumRounds] = useState(10);
  const [localEpochs, setLocalEpochs] = useState(3);
  const [dpEnabled, setDpEnabled] = useState(false);
  const [dpEpsilon, setDpEpsilon] = useState("8.0");
  const [secureAggregation, setSecureAggregation] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const toggleHospital = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (selected.size === 0) {
      setError("Select at least one participating hospital.");
      return;
    }
    const epsilon = Number(dpEpsilon);
    if (dpEnabled && (!Number.isFinite(epsilon) || epsilon <= 0)) {
      setError("Privacy budget ε must be a positive number.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const round = await api.createRound({
        num_rounds: numRounds,
        local_epochs: localEpochs,
        dp_enabled: dpEnabled,
        dp_epsilon: dpEnabled ? epsilon : null,
        secure_aggregation: secureAggregation,
        hospital_ids: [...selected],
      });
      toast("success", `Training round #${round.id} launched.`);
      navigate(`/rounds/${round.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start round");
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>New training round</h1>
          <div className="page-sub">
            <Link to="/rounds">Training rounds</Link> / configure and launch
          </div>
        </div>
      </div>

      {hospitals.loading ? (
        <Spinner center />
      ) : hospitals.error ? (
        <ErrorState message={hospitals.error} onRetry={hospitals.reload} />
      ) : (hospitals.data ?? []).length === 0 ? (
        <EmptyState
          title="No hospitals available"
          message="Register at least one hospital before launching a training round."
        />
      ) : (
        <form onSubmit={onSubmit} className="grid-two">
          <div className="card">
            <div className="card-title">
              <span>Participating hospitals</span>
              <span className="muted" style={{ fontWeight: 400 }}>
                {selected.size} selected
              </span>
            </div>
            <div className="hospital-picker">
              {(hospitals.data ?? []).map((h) => (
                <label key={h.id} className="checkbox-row">
                  <input
                    type="checkbox"
                    checked={selected.has(h.id)}
                    onChange={() => toggleHospital(h.id)}
                  />
                  <span style={{ flex: 1 }}>
                    {h.name}
                    <span className="muted"> — {h.region}</span>
                  </span>
                  <span className="muted mono">
                    {formatCount(h.data_size)}
                  </span>
                  <StatusBadge status={h.status} />
                </label>
              ))}
            </div>
            <div className="chart-note">
              Offline hospitals may be skipped by the coordinator when the
              round starts.
            </div>
          </div>

          <div className="card">
            <div className="card-title">Training configuration</div>
            <div className="field slider-row">
              <label htmlFor="nr-rounds">
                Federated rounds
              </label>
              <div className="row">
                <input
                  id="nr-rounds"
                  type="range"
                  min={1}
                  max={50}
                  value={numRounds}
                  onChange={(e) => setNumRounds(Number(e.target.value))}
                />
                <span className="slider-value">{numRounds}</span>
              </div>
              <span className="hint">
                Aggregation rounds performed by the coordinator.
              </span>
            </div>
            <div className="field slider-row">
              <label htmlFor="nr-epochs">Local epochs per round</label>
              <div className="row">
                <input
                  id="nr-epochs"
                  type="range"
                  min={1}
                  max={20}
                  value={localEpochs}
                  onChange={(e) => setLocalEpochs(Number(e.target.value))}
                />
                <span className="slider-value">{localEpochs}</span>
              </div>
              <span className="hint">
                Epochs each hospital trains locally before sending an update.
              </span>
            </div>

            <div className="switch-row">
              <div>
                <label htmlFor="nr-dp" style={{ fontWeight: 550 }}>
                  Differential privacy
                </label>
                <div className="hint">
                  Adds calibrated noise to client updates.
                </div>
              </div>
              <input
                id="nr-dp"
                type="checkbox"
                checked={dpEnabled}
                onChange={(e) => setDpEnabled(e.target.checked)}
                style={{ accentColor: "var(--accent)", width: 16, height: 16 }}
              />
            </div>
            {dpEnabled && (
              <div className="field">
                <label htmlFor="nr-eps">Privacy budget ε</label>
                <input
                  id="nr-eps"
                  className="input"
                  type="number"
                  step="0.1"
                  min="0.1"
                  max="50"
                  value={dpEpsilon}
                  onChange={(e) => setDpEpsilon(e.target.value)}
                />
                <span className="hint">
                  Lower ε means stronger privacy and noisier updates (typical
                  range 1–10).
                </span>
              </div>
            )}

            <div className="switch-row">
              <div>
                <label htmlFor="nr-secagg" style={{ fontWeight: 550 }}>
                  Secure aggregation
                </label>
                <div className="hint">
                  Updates are masked so only the aggregate is revealed.
                </div>
              </div>
              <input
                id="nr-secagg"
                type="checkbox"
                checked={secureAggregation}
                onChange={(e) => setSecureAggregation(e.target.checked)}
                style={{ accentColor: "var(--accent)", width: 16, height: 16 }}
              />
            </div>

            {error && (
              <div className="form-error" style={{ marginTop: 14 }}>
                {error}
              </div>
            )}
            <div className="modal-actions" style={{ marginTop: 16 }}>
              <Link to="/rounds" className="btn">
                Cancel
              </Link>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={submitting}
              >
                {submitting ? "Launching…" : "Launch training round"}
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
}
