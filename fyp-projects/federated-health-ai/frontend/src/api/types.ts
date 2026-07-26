export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
}

export type HospitalStatus = "online" | "offline";

export interface Hospital {
  id: number;
  name: string;
  region: string;
  data_size: number;
  status: HospitalStatus;
  created_at: string;
}

export interface HospitalMetric {
  round_id: number;
  accuracy: number;
  auc: number;
  loss: number;
}

export interface HospitalDetail extends Hospital {
  metrics: HospitalMetric[];
}

export interface HospitalPayload {
  name: string;
  region: string;
  data_size: number;
}

export type RoundStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "cancelled";

export interface TrainingRound {
  id: number;
  status: RoundStatus;
  num_rounds: number;
  local_epochs: number;
  dp_enabled: boolean;
  dp_epsilon: number | null;
  secure_aggregation: boolean;
  current_round: number;
  created_at: string;
  completed_at: string | null;
  global_accuracy: number | null;
  global_auc: number | null;
  global_loss: number | null;
}

export interface RoundHistoryPoint {
  round_number: number;
  accuracy: number;
  auc: number;
  loss: number;
}

export interface ClientUpdate {
  id: number;
  hospital_id: number;
  hospital_name: string;
  round_number: number;
  num_samples: number;
  local_loss: number;
  local_accuracy: number;
  update_norm: number;
  created_at: string;
}

export interface RoundDetail extends TrainingRound {
  history: RoundHistoryPoint[];
  updates: ClientUpdate[];
}

export interface NewRoundPayload {
  num_rounds: number;
  local_epochs: number;
  dp_enabled: boolean;
  dp_epsilon: number | null;
  secure_aggregation: boolean;
  hospital_ids: number[];
}

export interface ModelVersion {
  id: number;
  version: string;
  round_id: number;
  accuracy: number;
  auc: number;
  loss: number;
  is_active: boolean;
  num_parameters: number;
  created_at: string;
}

export interface PredictionInput {
  age: number;
  sex: 0 | 1;
  systolic_bp: number;
  diastolic_bp: number;
  cholesterol: number;
  hdl: number;
  bmi: number;
  glucose: number;
  smoker: 0 | 1;
  family_history: 0 | 1;
}

export type Diagnosis = "high_risk" | "low_risk";
export type RiskLevel = "low" | "moderate" | "high";

export interface Prediction {
  id: number;
  probability: number;
  diagnosis: Diagnosis;
  risk_level: RiskLevel;
  model_version: string;
  created_at: string;
  features?: PredictionInput;
}

export interface AuditEvent {
  id: number;
  actor_email: string;
  action: string;
  resource: string;
  detail: string;
  created_at: string;
}

export interface StatsOverview {
  hospitals: number;
  hospitals_online: number;
  rounds_completed: number;
  active_model_accuracy: number | null;
  active_model_auc: number | null;
  predictions_made: number;
  last_round: TrainingRound | null;
}

export type RoundSocketEvent =
  | {
      type: "round_progress";
      round_number: number;
      total_rounds: number;
      accuracy: number;
      auc: number;
      loss: number;
    }
  | {
      type: "client_update";
      hospital_name: string;
      round_number: number;
      local_accuracy: number;
      local_loss: number;
    }
  | {
      type: "status";
      status: RoundStatus;
    };
