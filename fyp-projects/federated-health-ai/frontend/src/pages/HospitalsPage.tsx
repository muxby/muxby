import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { Hospital } from "../api/types";
import { DataTable, type Column } from "../components/DataTable";
import { Modal } from "../components/Modal";
import { Spinner } from "../components/Spinner";
import { StatusBadge } from "../components/StatusBadge";
import { ErrorState } from "../components/States";
import { useFetch } from "../hooks/useFetch";
import { toast } from "../stores/uiStore";
import { formatCount, formatDate } from "../utils/format";

const COLUMNS: Column<Hospital>[] = [
  {
    key: "name",
    header: "Hospital",
    strong: true,
    render: (h) => <Link to={`/hospitals/${h.id}`}>{h.name}</Link>,
  },
  { key: "region", header: "Region", render: (h) => h.region },
  {
    key: "data_size",
    header: "Patient records",
    numeric: true,
    render: (h) => formatCount(h.data_size),
  },
  {
    key: "status",
    header: "Status",
    render: (h) => <StatusBadge status={h.status} />,
  },
  {
    key: "created",
    header: "Onboarded",
    render: (h) => formatDate(h.created_at),
  },
];

export function HospitalsPage() {
  const navigate = useNavigate();
  const hospitals = useFetch(() => api.listHospitals(), []);
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [region, setRegion] = useState("");
  const [dataSize, setDataSize] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const closeModal = () => {
    setShowCreate(false);
    setName("");
    setRegion("");
    setDataSize("");
    setFormError(null);
  };

  const onCreate = async (e: FormEvent) => {
    e.preventDefault();
    const size = Number(dataSize);
    if (!Number.isFinite(size) || size <= 0) {
      setFormError("Patient record count must be a positive number.");
      return;
    }
    setFormError(null);
    setSaving(true);
    try {
      const created = await api.createHospital({
        name: name.trim(),
        region: region.trim(),
        data_size: size,
      });
      toast("success", `Hospital "${created.name}" registered.`);
      closeModal();
      hospitals.reload();
    } catch (err) {
      setFormError(
        err instanceof Error ? err.message : "Failed to create hospital",
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Hospitals</h1>
          <div className="page-sub">
            Participating institutions and their local dataset sizes.
          </div>
        </div>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => setShowCreate(true)}
        >
          Register hospital
        </button>
      </div>

      {hospitals.loading ? (
        <Spinner center />
      ) : hospitals.error ? (
        <ErrorState message={hospitals.error} onRetry={hospitals.reload} />
      ) : (
        <DataTable
          columns={COLUMNS}
          rows={hospitals.data ?? []}
          rowKey={(h) => h.id}
          emptyMessage="No hospitals registered yet — add the first participating institution."
          onRowClick={(h) => navigate(`/hospitals/${h.id}`)}
        />
      )}

      {showCreate && (
        <Modal title="Register hospital" onClose={closeModal}>
          {formError && <div className="form-error">{formError}</div>}
          <form onSubmit={onCreate}>
            <div className="field">
              <label htmlFor="h-name">Hospital name</label>
              <input
                id="h-name"
                className="input"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              <span className="hint">
                Full institution name, e.g. a general or teaching hospital.
              </span>
            </div>
            <div className="field">
              <label htmlFor="h-region">Region</label>
              <input
                id="h-region"
                className="input"
                required
                value={region}
                onChange={(e) => setRegion(e.target.value)}
              />
              <span className="hint">
                Geographic region the hospital serves.
              </span>
            </div>
            <div className="field">
              <label htmlFor="h-size">Patient records</label>
              <input
                id="h-size"
                className="input"
                type="number"
                min={1}
                required
                value={dataSize}
                onChange={(e) => setDataSize(e.target.value)}
              />
              <span className="hint">
                Number of local records available for training.
              </span>
            </div>
            <div className="modal-actions">
              <button type="button" className="btn" onClick={closeModal}>
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={saving}
              >
                {saving ? "Registering…" : "Register"}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
