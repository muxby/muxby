import { api } from "../api/client";
import type { AuditEvent } from "../api/types";
import { DataTable, type Column } from "../components/DataTable";
import { Spinner } from "../components/Spinner";
import { ErrorState } from "../components/States";
import { useFetch } from "../hooks/useFetch";
import { formatDateTime } from "../utils/format";

const COLUMNS: Column<AuditEvent>[] = [
  {
    key: "time",
    header: "Time",
    render: (e) => formatDateTime(e.created_at),
  },
  {
    key: "actor",
    header: "Actor",
    strong: true,
    render: (e) => e.actor_email,
  },
  {
    key: "action",
    header: "Action",
    render: (e) => <span className="badge badge-neutral">{e.action}</span>,
  },
  { key: "resource", header: "Resource", render: (e) => e.resource },
  { key: "detail", header: "Detail", render: (e) => e.detail },
];

export function AuditPage() {
  const audit = useFetch(() => api.listAudit(100), []);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Audit log</h1>
          <div className="page-sub">
            Latest 100 security-relevant events across the platform.
          </div>
        </div>
        <button type="button" className="btn" onClick={audit.reload}>
          Refresh
        </button>
      </div>

      {audit.loading ? (
        <Spinner center />
      ) : audit.error ? (
        <ErrorState message={audit.error} onRetry={audit.reload} />
      ) : (
        <DataTable
          columns={COLUMNS}
          rows={audit.data ?? []}
          rowKey={(e) => e.id}
          emptyMessage="No audit events recorded yet."
        />
      )}
    </div>
  );
}
