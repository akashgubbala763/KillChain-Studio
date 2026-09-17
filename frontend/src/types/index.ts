export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  timestamp: string;
  environment: string;
}

export interface DbHealthStatus {
  status: string;
  database_type: string;
  timestamp: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'ADMIN' | 'ANALYST' | 'VIEWER';
}

export interface NetworkEvent {
  id: string;
  timestamp: string;
  source_ip: string;
  destination_ip: string;
  source_port: number;
  destination_port: number;
  protocol: string;
  event_type: string;
  bytes_sent: number;
  bytes_received: number;
  packets?: number;
  tcp_flags?: string;
  user_identifier?: string;
  device_hostname?: string;
  raw_payload?: Record<string, any>;
  ingested_at: string;
}

export interface RuleMatch {
  rule_code: string;
  name: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  evidence_details?: Record<string, any>;
}

export interface MLPrediction {
  predicted_class: 'Normal' | 'PortScan' | 'BruteForce' | 'DataExfiltration';
  confidence_score: number;
  class_probabilities: Record<string, number>;
}

export interface AnomalyResult {
  anomaly_score: number;
  is_anomaly: boolean;
}

export interface Incident {
  id: string;
  incident_code: string;
  title: string;
  primary_entity: string;
  attack_category: string;
  status: 'OPEN' | 'INVESTIGATING' | 'RESOLVED' | 'FALSE_POSITIVE';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  current_risk_score: number;
  confidence_rating: number;
  signal_consensus: 'STRONG_AGREEMENT' | 'MODERATE' | 'CONFLICTING';
  start_time: string;
  end_time: string;
  created_at: string;
  updated_at: string;
}

export interface ReconstructedTimelineStep {
  step: number;
  event_id: string;
  timestamp: string;
  kill_chain_phase: string;
  source_ip: string;
  destination_ip: string;
  destination_port: number;
  protocol: string;
  event_type: string;
  step_risk_score: number;
  risk_delta: string;
  rule_matches: RuleMatch[];
  ml_classification?: {
    predicted_class: string;
    confidence: number;
  };
  anomaly_detection?: {
    is_anomaly: boolean;
    score: number;
  };
}

export interface ReconstructedTimelineResponse {
  incident_id: string;
  incident_code: string;
  title: string;
  total_events: number;
  timeline: ReconstructedTimelineStep[];
}
