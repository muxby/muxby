import { useAuthStore } from "../stores/authStore";
import type {
  AuditEvent,
  Hospital,
  HospitalDetail,
  HospitalPayload,
  ModelVersion,
  NewRoundPayload,
  Prediction,
  PredictionInput,
  RegisterPayload,
  RoundDetail,
  StatsOverview,
  TokenResponse,
  TrainingRound,
  User,
} from "./types";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const BASE = "/api";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = useAuthStore.getState().token;
  const headers = new Headers(init.headers);
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (typeof init.body === "string" && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, { ...init, headers });
  } catch {
    throw new ApiError(0, "Network error — is the backend reachable?");
  }

  if (!res.ok) {
    if (res.status === 401 && useAuthStore.getState().token) {
      useAuthStore.getState().logout();
    }
    let message = `Request failed (${res.status})`;
    try {
      const body = (await res.json()) as { detail?: unknown };
      if (typeof body.detail === "string") {
        message = body.detail;
      } else if (Array.isArray(body.detail) && body.detail.length > 0) {
        const first = body.detail[0] as { msg?: string };
        if (typeof first.msg === "string") message = first.msg;
      }
    } catch {
      // non-JSON error body; keep the status message
    }
    throw new ApiError(res.status, message);
  }

  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

function get<T>(path: string): Promise<T> {
  return request<T>(path);
}

function post<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

export const api = {
  // auth
  register(payload: RegisterPayload): Promise<User> {
    return post<User>("/auth/register", payload);
  },
  login(email: string, password: string): Promise<TokenResponse> {
    return request<TokenResponse>("/auth/login", {
      method: "POST",
      body: new URLSearchParams({ username: email, password }),
    });
  },
  me(): Promise<User> {
    return get<User>("/auth/me");
  },

  // hospitals
  listHospitals(): Promise<Hospital[]> {
    return get<Hospital[]>("/hospitals");
  },
  createHospital(payload: HospitalPayload): Promise<Hospital> {
    return post<Hospital>("/hospitals", payload);
  },
  getHospital(id: number): Promise<HospitalDetail> {
    return get<HospitalDetail>(`/hospitals/${id}`);
  },
  updateHospital(
    id: number,
    payload: Partial<HospitalPayload & { status: Hospital["status"] }>,
  ): Promise<Hospital> {
    return request<Hospital>(`/hospitals/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },
  deleteHospital(id: number): Promise<void> {
    return request<void>(`/hospitals/${id}`, { method: "DELETE" });
  },

  // training rounds
  listRounds(): Promise<TrainingRound[]> {
    return get<TrainingRound[]>("/rounds");
  },
  createRound(payload: NewRoundPayload): Promise<TrainingRound> {
    return post<TrainingRound>("/rounds", payload);
  },
  getRound(id: number): Promise<RoundDetail> {
    return get<RoundDetail>(`/rounds/${id}`);
  },
  cancelRound(id: number): Promise<TrainingRound> {
    return post<TrainingRound>(`/rounds/${id}/cancel`);
  },

  // models
  listModels(): Promise<ModelVersion[]> {
    return get<ModelVersion[]>("/models");
  },
  getModel(id: number): Promise<ModelVersion> {
    return get<ModelVersion>(`/models/${id}`);
  },
  activateModel(id: number): Promise<ModelVersion> {
    return post<ModelVersion>(`/models/${id}/activate`);
  },

  // predictions
  createPrediction(payload: PredictionInput): Promise<Prediction> {
    return post<Prediction>("/predictions", payload);
  },
  listPredictions(): Promise<Prediction[]> {
    return get<Prediction[]>("/predictions");
  },

  // audit + stats
  listAudit(limit = 100): Promise<AuditEvent[]> {
    return get<AuditEvent[]>(`/audit?limit=${limit}`);
  },
  statsOverview(): Promise<StatsOverview> {
    return get<StatsOverview>("/stats/overview");
  },
};

export function roundSocketUrl(roundId: number, token: string): string {
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${window.location.host}${BASE}/ws/rounds/${roundId}?token=${encodeURIComponent(token)}`;
}
