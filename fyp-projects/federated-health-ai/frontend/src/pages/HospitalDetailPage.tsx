import { useState, type FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { HospitalStatus } from "../api/types";
import { CHART_COLORS, MetricLineChart } from "../components/MetricLineChart";
import { Modal } from "../components/Modal";
import { Spinner } from "../components/Spinner";
import { StatusBadge } from "../components/StatusBadge";
import { EmptyState, ErrorState } from "../components/States";
import { useFetch } from "../hooks/useFetch";
import { toast } from "../stores/uiStore";
import { formatCount, formatDate } from "../utils/format";

export function HospitalDetailPage() {
  const params = useParams<{ id: string }>();
  const hospitalId = Number(params.id);
  const navigate = useNavigate();
  const hospital = useFetch(() => api.getHospital(hospitalId), [hospitalId]);

  const [showEdit, setShowEdit] = useState(false);
  const [showDelete, setShowDelete] = useState(false);
  const [name, setName] = useState("");
  const [region, setRegion] = useState("");
  const [dataSize, setDataSize] = useState("");
  const [status, setStatus] = useState<HospitalStatus>("online");
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (!Number.isFinite(hospitalId)) {
    return <ErrorState message="Invalid hospital id." />;
  }
  if (hospital.loading) return <Spinner center />;
  if (hospital.error || !hospital.data) {
    return (
      <ErrorState
        message={hospital.error ?? "Hospital not found."}
        onRetry={hospital.reload}
      />
    );
  }

  const h = hospital.data;

  const openEdit = () => {
    setName(h.name);
    setRegion(h.region);
    setDataSize(String(h.data_size));
    setStatus(h.status);
    setFormError(null);
    setShowEdit(true);
  };

  const onSave = async (e: FormEvent) => {
    e.preventDefault();
    const size = Number(dataSize);
    if (!Number.isFinite(size) || size <= 0) {
      setFormError("Patient record count must be a positive number.");
      return;
    }
    setBusy(true);
    try {
      await api.updateHospital(h.id, {
        name: name.trim(),
        region: region.trim(),
        data_size: size,
        status,
      });
      toast("success", "Hospital updated.");
      setShowEdit(false);
      hospital.reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Update failed");
    } finally {
      setBusy(false);
    }
  };

  const onDelete = async () => {
    setBusy(true);
    try {
      await api.deleteHospital(h.id);
      toast("success", `Hospital "${h.name}" removed.`);
      navigate("/hospitals");
    } catch (err) {
      toast("error", err instanceof Error ? err.message : "Delete failed");
      setBusy(false);
      setShowDelete(false);
    }
  };

  return (
    <div className="stack">
      <div className="page-header">
        <div>
          <h1>{h.name}</h1>
          <div className="page-sub">
            <Link to="/hospitals">Hospitals</Link> / #{h.id}
          </div>
        </div>
        <div className="row">
          <button type="button" className="btn" onClick={openEdit}>
            Edit
          </button>
          <button
            type="button"
            className="btn btn-danger"
            onClick={() => setShowDelete(true)}
          >
            Delete
          </button>
        </div>
      </div>

      <div className="grid-two">
        <div className="card">
          <div className="card-title">Institution</div>
          <dl className="kv-list">
            <dt>Status</dt>
            <dd>
              <StatusBadge status={h.status} />
            </dd>
            <dt>Region</dt>
            <dd>{h.region}</dd>
            <dt>Patient records</dt>
            <dd>{formatCount(h.data_size)}</dd>
            <dt>Onboarded</dt>
            <dd>{formatDate(h.created_at)}</dd>
            <dt>Rounds participated</dt>
            <dd>{formatCount(h.metrics.length)}</dd>
          </dl>
        </div>
        <div className="card">
          <div className="card-title">Local performance per round</div>
          {h.metrics.length === 0 ? (
            <EmptyState
              title="No metrics yet"
              message="This hospital has not participated in a completed training round."
            />
          ) : (
            <MetricLineChart
              data={h.metrics}
              xKey="round_id"
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
      </div>

      {h.metrics.length > 0 && (
        <div className="card">
          <div className="card-title">Local loss per round</div>
          <MetricLineChart
            data={h.metrics}
            xKey="round_id"
            xLabel="Round"
            series={[{ key: "loss", label: "Loss", color: CHART_COLORS.loss }]}
          />
        </div>
      )}

      {showEdit && (
        <Modal title="Edit hospital" onClose={() => setShowEdit(false)}>
          {formError && <div className="form-error">{formError}</div>}
          <form onSubmit={onSave}>
            <div className="field">
              <label htmlFor="eh-name">Hospital name</label>
              <input
                id="eh-name"
                className="input"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="eh-region">Region</label>
              <input
                id="eh-region"
                className="input"
                required
                value={region}
                onChange={(e) => setRegion(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="eh-size">Patient records</label>
              <input
                id="eh-size"
                className="input"
                type="number"
                min={1}
                required
                value={dataSize}
                onChange={(e) => setDataSize(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="eh-status">Status</label>
              <select
                id="eh-status"
                className="input"
                value={status}
                onChange={(e) => setStatus(e.target.value as HospitalStatus)}
              >
                <option value="online">Online</option>
                <option value="offline">Offline</option>
              </select>
            </div>
            <div className="modal-actions">
              <button
                type="button"
                className="btn"
                onClick={() => setShowEdit(false)}
              >
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={busy}>
                {busy ? "Saving…" : "Save changes"}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {showDelete && (
        <Modal title="Delete hospital" onClose={() => setShowDelete(false)}>
          <p style={{ marginTop: 0 }}>
            Remove <strong>{h.name}</strong> from the federation? Its local
            metric history will no longer be available.
          </p>
          <div className="modal-actions">
            <button
              type="button"
              className="btn"
              onClick={() => setShowDelete(false)}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-danger"
              disabled={busy}
              onClick={onDelete}
            >
              {busy ? "Deleting…" : "Delete hospital"}
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}
