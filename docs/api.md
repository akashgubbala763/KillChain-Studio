# API Architecture & Endpoint Specification

## Intelligent Network Security Monitoring & Attack Reconstruction Platform

---

## 1. Overview & General Standards

The platform provides an asynchronous, typed RESTful API built on **FastAPI**.

- **Base URL**: `http://localhost:8000/api/v1`
- **Interactive Documentation**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc).
- **Authentication**: Bearer Token (`Authorization: Bearer <jwt_access_token>`).
- **Data Interchange**: All payloads and responses are encoded in standard UTF-8 JSON.
- **Error Response Standard**:
  ```json
  {
    "error_code": "RESOURCE_NOT_FOUND",
    "message": "Incident INC-2026-0042 not found.",
    "details": null,
    "timestamp": "2026-09-17T14:30:00Z"
  }
  ```

---

## 2. Authentication & User Management (`/api/v1/auth`)

### 2.1 Register User
- **Method & Route**: `POST /auth/register`
- **Access**: Public (Initial Setup) / Admin Only
- **Request Body**:
  ```json
  {
    "email": "analyst@soc.local",
    "password": "SecurePassword123!",
    "full_name": "Jane Doe",
    "role": "ANALYST"
  }
  ```
- **Response (`201 Created`)**:
  ```json
  {
    "id": "c7a84e4e-0a56-42d8-9db8-500e57dfc2a9",
    "email": "analyst@soc.local",
    "full_name": "Jane Doe",
    "role": "ANALYST",
    "is_active": true,
    "created_at": "2026-09-17T14:30:00Z"
  }
  ```

### 2.2 Login & Token Generation
- **Method & Route**: `POST /auth/login`
- **Access**: Public
- **Request Form-Data / Body**:
  ```json
  {
    "username": "analyst@soc.local",
    "password": "SecurePassword123!"
  }
  ```
- **Response (`200 OK`)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 28800,
    "user": {
      "id": "c7a84e4e-0a56-42d8-9db8-500e57dfc2a9",
      "email": "analyst@soc.local",
      "full_name": "Jane Doe",
      "role": "ANALYST"
    }
  }
  ```

### 2.3 Current User Profile
- **Method & Route**: `GET /auth/me`
- **Access**: Authenticated

---

## 3. Network Events & Ingestion (`/api/v1/events`)

### 3.1 Ingest Event(s)
- **Method & Route**: `POST /events/ingest`
- **Access**: Authenticated (Simulator, Agents, Admin)
- **Request Body (Single or Batch Array)**:
  ```json
  [
    {
      "timestamp": "2026-09-17T14:31:02Z",
      "source_ip": "192.168.1.150",
      "destination_ip": "10.0.0.5",
      "source_port": 49152,
      "destination_port": 22,
      "protocol": "SSH",
      "event_type": "auth",
      "bytes_sent": 1200,
      "bytes_received": 450,
      "packets": 8,
      "tcp_flags": "PSH,ACK",
      "user_identifier": "root",
      "device_hostname": "bastion-host",
      "raw_payload": {
        "auth_status": "FAILURE",
        "auth_method": "password"
      }
    }
  ]
  ```
- **Response (`202 Accepted`)**:
  ```json
  {
    "ingested_count": 1,
    "status": "QUEUED_FOR_DETECTION",
    "event_ids": ["f81d4fae-7dec-11d0-a765-00a0c91e6bf6"]
  }
  ```

### 3.2 Query Events (Paginated)
- **Method & Route**: `GET /events`
- **Query Parameters**:
  - `page` (default: 1), `page_size` (default: 50)
  - `source_ip`, `destination_ip`, `destination_port`, `protocol`, `event_type`
  - `start_time`, `end_time`
- **Response (`200 OK`)**: Paginated event items with total count and timestamps.

### 3.3 Get Event Forensic Detail
- **Method & Route**: `GET /events/{id}`
- **Response (`200 OK`)**: Includes raw event record, linked rule matches, ML model classification probabilities, and Isolation Forest anomaly score.

---

## 4. Detections & Rules (`/api/v1/detections`)

### 4.1 List Rules
- **Method & Route**: `GET /detections/rules`
- **Response (`200 OK`)**: Array of all detection rules, active status, threshold parameters, and categories.

### 4.2 Update Detection Rule
- **Method & Route**: `PUT /detections/rules/{id}`
- **Access**: Admin Only
- **Request Body**:
  ```json
  {
    "name": "SSH Brute Force Attack",
    "severity": "CRITICAL",
    "is_enabled": true,
    "parameters": {
      "threshold_failed_attempts": 6,
      "window_seconds": 60
    }
  }
  ```

### 4.3 Query Rule Matches
- **Method & Route**: `GET /detections/matches`
- **Query Parameters**: `severity`, `rule_code`, `start_time`

---

## 5. Behavioral Baselines (`/api/v1/baselines`)

### 5.1 List Entity Baselines
- **Method & Route**: `GET /baselines/entities`
- **Response (`200 OK`)**: List of tracked entities (IPs, Hosts, Users) with hourly averages and standard deviations.

### 5.2 Get Entity Deviation
- **Method & Route**: `GET /baselines/entities/{entity_id}/deviation`
- **Query Parameters**: `window_minutes` (default: 15)
- **Response (`200 OK`)**:
  ```json
  {
    "entity_id": "192.168.1.150",
    "entity_type": "IP",
    "evaluation_window_minutes": 15,
    "metrics": {
      "ssh_connections": {
        "baseline_mean": 0.0,
        "baseline_std": 1.0,
        "current_value": 14.0,
        "z_score": 14.0,
        "status": "HIGHLY_ABNORMAL"
      },
      "bytes_out": {
        "baseline_mean": 50000.0,
        "baseline_std": 12000.0,
        "current_value": 850000.0,
        "z_score": 66.6,
        "status": "CRITICAL_DEVIATION"
      },
      "unique_ports": {
        "baseline_mean": 4.0,
        "baseline_std": 1.5,
        "current_value": 47.0,
        "z_score": 28.6,
        "status": "HIGHLY_ABNORMAL"
      }
    }
  }
  ```

---

## 6. Incidents & Attack Reconstruction (`/api/v1/incidents`)

### 6.1 List Incidents
- **Method & Route**: `GET /incidents`
- **Query Parameters**: `status`, `severity`, `primary_entity`, `page`, `page_size`

### 6.2 Get Incident Summary
- **Method & Route**: `GET /incidents/{id}`
- **Response (`200 OK`)**: Incident overview, risk score (0-100), confidence percentage, signal consensus, and kill-chain phase progression.

### 6.3 Reconstruct Attack Timeline (PRIMARY USP)
- **Method & Route**: `GET /incidents/{id}/timeline`
- **Access**: Analyst, Admin, Viewer
- **Response (`200 OK`)**:
  ```json
  {
    "incident_id": "8a329d2b-10f8-45ee-9e90-25e24b74bb81",
    "incident_code": "INC-2026-0001",
    "title": "Multi-Stage Credential Breach & Exfiltration",
    "total_events": 6,
    "timeline": [
      {
        "step": 1,
        "event_id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
        "timestamp": "2026-09-17T14:31:02Z",
        "kill_chain_phase": "Initial Access",
        "source_ip": "192.168.1.150",
        "destination_ip": "10.0.0.5",
        "destination_port": 22,
        "protocol": "SSH",
        "event_type": "auth",
        "step_risk_score": 25.0,
        "risk_delta": "+25.0",
        "rule_matches": [
          {
            "rule_code": "RULE-BF-01",
            "name": "Multiple Failed Authentications",
            "severity": "HIGH"
          }
        ],
        "ml_classification": {
          "predicted_class": "BruteForce",
          "confidence": 0.94
        },
        "anomaly_detection": {
          "is_anomaly": true,
          "score": 0.88
        }
      },
      {
        "step": 2,
        "event_id": "a1b2c3d4-7dec-11d0-a765-00a0c91e6bf7",
        "timestamp": "2026-09-17T14:31:15Z",
        "kill_chain_phase": "Reconnaissance",
        "source_ip": "192.168.1.150",
        "destination_ip": "10.0.0.8",
        "destination_port": 3306,
        "protocol": "TCP",
        "event_type": "connection",
        "step_risk_score": 52.0,
        "risk_delta": "+27.0",
        "rule_matches": [
          {
            "rule_code": "RULE-PS-01",
            "name": "Horizontal Port Sweep",
            "severity": "HIGH"
          }
        ],
        "ml_classification": {
          "predicted_class": "PortScan",
          "confidence": 0.91
        },
        "anomaly_detection": {
          "is_anomaly": true,
          "score": 0.92
        }
      },
      {
        "step": 3,
        "event_id": "b2c3d4e5-7dec-11d0-a765-00a0c91e6bf8",
        "timestamp": "2026-09-17T14:31:37Z",
        "kill_chain_phase": "Exfiltration",
        "source_ip": "192.168.1.150",
        "destination_ip": "198.51.100.44",
        "destination_port": 4444,
        "protocol": "TCP",
        "event_type": "transfer",
        "step_risk_score": 87.0,
        "risk_delta": "+35.0",
        "rule_matches": [
          {
            "rule_code": "RULE-EX-01",
            "name": "Abnormal Data Exfiltration",
            "severity": "CRITICAL"
          },
          {
            "rule_code": "RULE-SP-01",
            "name": "Traffic on Suspicious Port 4444",
            "severity": "HIGH"
          }
        ],
        "ml_classification": {
          "predicted_class": "DataExfiltration",
          "confidence": 0.96
        },
        "anomaly_detection": {
          "is_anomaly": true,
          "score": 0.97
        }
      }
    ]
  }
  ```

### 6.4 Get Behavioral Comparison for Incident
- **Method & Route**: `GET /incidents/{id}/behavior-comparison`
- **Response (`200 OK`)**: Returns pre-attack baseline metrics versus attack-window metrics for the involved entity.

### 6.5 Update Incident Status
- **Method & Route**: `PATCH /incidents/{id}/status`
- **Access**: Analyst, Admin
- **Request Body**:
  ```json
  {
    "status": "INVESTIGATING",
    "notes": "Analyst investigating compromised SSH session."
  }
  ```

---

## 7. Analytics & Dashboard Metrics (`/api/v1/analytics`)

### 7.1 Overview Metrics
- **Method & Route**: `GET /analytics/overview`
- **Response (`200 OK`)**:
  ```json
  {
    "total_events": 14250,
    "events_per_second": 32.4,
    "suspicious_events": 128,
    "open_incidents": 3,
    "critical_incidents": 1,
    "system_health": "ONLINE"
  }
  ```

### 7.2 Traffic & Protocol Distribution
- **Method & Route**: `GET /analytics/traffic`
- **Response (`200 OK`)**: Breakdown of traffic volume by protocol and top 5 talkers.

---

## 8. Simulator Control (`/api/v1/simulator`)

### 8.1 Trigger Predefined Attack Scenario
- **Method & Route**: `POST /simulator/scenario/{scenario_name}`
- **Access**: Analyst, Admin
- **Valid Path Parameters**:
  - `brute_force`
  - `port_scan`
  - `compromised_account`
  - `data_exfiltration`
  - `full_killchain`
- **Response (`202 Accepted`)**:
  ```json
  {
    "scenario": "full_killchain",
    "status": "STARTED",
    "expected_events": 15,
    "duration_seconds": 30
  }
  ```

### 8.2 Simulator State & Telemetry
- **Method & Route**: `GET /simulator/status`
- **Response (`200 OK`)**: Active scenario name, progress percentage, emitted event count.

---

## 9. Real-Time WebSocket (`/api/v1/ws`)

### 9.1 Live Event & Alert Stream
- **URL**: `ws://localhost:8000/api/v1/ws/stream`
- **Protocol**: Standard WebSocket
- **Payload Format**:
  ```json
  {
    "type": "DETECTION_ALERT",
    "timestamp": "2026-09-17T14:31:02Z",
    "data": {
      "incident_id": "8a329d2b-10f8-45ee-9e90-25e24b74bb81",
      "incident_code": "INC-2026-0001",
      "severity": "HIGH",
      "risk_score": 87,
      "event_id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
      "summary": "Brute force attack detected on 10.0.0.5"
    }
  }
  ```
