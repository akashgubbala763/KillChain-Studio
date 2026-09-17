# Requirements Specification

## Intelligent Network Security Monitoring & Attack Reconstruction Platform

---

## 1. Executive Summary

This document specifies the complete functional and non-functional requirements for the **Intelligent Network Security Monitoring & Attack Reconstruction Platform**. Designed as an advanced, educational, and demonstrable final-year cybersecurity engineering project, the platform demonstrates how modern security operations centers (SOCs) collect, normalize, detect, correlate, score, and interactively reconstruct complex multi-stage network attacks.

---

## 2. Stakeholders & Personas

| Role | Persona Description | Key Objectives & Permissions |
| :--- | :--- | :--- |
| **SOC Admin** | Security Systems Administrator / Lead Architect | Configures detection rules, tunes ML thresholds, manages users and roles, starts/stops network attack simulations, inspects audit trails. |
| **Security Analyst** | Tier-1 & Tier-2 SOC Analyst | Monitors real-time telemetry stream, reviews generated incidents, performs deep-dive forensic attack reconstruction, inspects behavioral deviations, updates incident statuses. |
| **Viewer / Auditor** | Read-Only Stakeholder / Student Evaluator | Observes overview dashboards, reviews resolved incident reports, inspects model metrics without permission to alter state. |

---

## 3. Functional Requirements (FR)

### Module 1: Event Collection & Ingestion
- **FR-1.1**: The system shall provide an authenticated REST endpoint (`POST /api/v1/events/ingest`) accepting both single-event payloads and bulk event arrays in structured JSON format.
- **FR-1.2**: Ingested events must validate against a strict Pydantic schema containing:
  - `timestamp`: ISO-8601 UTC timestamp
  - `source_ip`: IPv4/IPv6 source address
  - `destination_ip`: IPv4/IPv6 destination address
  - `source_port`: Integer (0–65535)
  - `destination_port`: Integer (0–65535)
  - `protocol`: Transport/application protocol (TCP, UDP, ICMP, HTTP, DNS, SSH)
  - `event_type`: Categorical label (e.g. `connection`, `auth`, `dns`, `transfer`, `flow`)
  - `bytes_sent`: Bigint non-negative integer
  - `bytes_received`: Bigint non-negative integer
  - `packets`: Optional packet count
  - `tcp_flags`: Optional TCP flags string (e.g. `SYN`, `ACK`, `RST`, `FIN`, `PSH`)
  - `user_identifier`: Monitored user identity (if applicable)
  - `device_hostname`: Originating or target asset hostname
  - `raw_payload`: Optional JSON dictionary containing protocol-specific parameters.
- **FR-1.3**: The system shall validate, normalize, and persist valid events into PostgreSQL with an ingestion timestamp and unique UUID.
- **FR-1.4**: The system shall push freshly ingested events over a WebSocket channel (`/api/v1/ws/stream`) to active connected clients within 100ms of persistence.

### Module 2: Multi-Signal Detection Engine
- **FR-2.1 (Deterministic Rule Engine)**:
  - The system shall evaluate events against a configurable set of deterministic rules in real-time.
  - The engine must support stateful rules (e.g. tracking event frequency over a sliding window per source IP).
  - Every rule match must record the `rule_id`, `rule_code`, `event_id`, severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), matched timestamp, and explicit JSON evidence explanation.
  - Core initial rules must include:
    1. `RULE-BF-01`: Failed authentications threshold ($\ge 5$ within 60s).
    2. `RULE-PS-01`: Port scanning threshold ($\ge 15$ unique destination ports within 30s).
    3. `RULE-BW-01`: Traffic volume surge ($> 5\times$ entity rolling baseline).
    4. `RULE-SP-01`: Suspicious port traffic (e.g. 4444, 6667, 1337, 31337).
    5. `RULE-RF-01`: Repeated TCP RST / failed handshakes.
    6. `RULE-EX-01`: Large outbound data transfer ($> 50\text{ MB}$ or non-standard egress).
- **FR-2.2 (Supervised Machine Learning Classification)**:
  - The system shall extract a 12-dimensional numerical feature vector from events and pass it to a pre-trained Random Forest classifier.
  - The classifier must predict the category (`Normal`, `PortScan`, `BruteForce`, `DataExfiltration`) along with class probability scores.
  - Predictions and confidence values must be persisted in `ml_predictions` linked by `event_id`.
- **FR-2.3 (Unsupervised Anomaly Detection)**:
  - The system shall evaluate events against an Isolation Forest model to detect multivariate outliers that deviate from learned normal traffic.
  - The model must output a boolean `is_anomaly` flag and a continuous anomaly score normalized to $[0, 1]$.
  - Anomaly results must be stored in `anomaly_results` linked by `event_id`.

### Module 3: Behavioral Baseline & Deviation Analysis
- **FR-3.1**: The system shall compute and maintain rolling behavioral baselines for monitored entities (`source_ip`, `host`, `user`).
- **FR-3.2**: Tracked baseline dimensions must include:
  - Average connections per hour ($\mu, \sigma$)
  - Average outbound volume in bytes ($\mu, \sigma$)
  - Average unique destination ports contacted ($\mu, \sigma$)
  - Average failed login count ($\mu, \sigma$)
- **FR-3.3**: The system shall compute the standard score (Z-Score) for entity metrics during an active observation window:
  $$Z = \frac{x - \mu}{\sigma + \epsilon}$$
- **FR-3.4**: Deviations where $|Z| \ge 2.0$ shall be flagged as anomalous deviations, and $|Z| \ge 3.5$ as severe anomalies.
- **FR-3.5**: The system shall provide an API endpoint returning a structured delta comparison between normal baseline metrics and current incident-window metrics.

### Module 4: Event Correlation & Incident Formation
- **FR-4.1**: The system shall correlate related security events into unified **Incidents** based on shared entity identifiers (Source IP, Target Host, Subnet, User) within an adjustable sliding time window (default: 15 minutes).
- **FR-4.2**: Correlated events must be classified into progressive cyber kill-chain phases:
  - `Reconnaissance`
  - `Initial Access`
  - `Lateral Movement / Internal Activity`
  - `Exfiltration / Impact`
- **FR-4.3**: The correlation engine shall generate an incident when:
  - A single event produces a Critical rule match and high ML probability ($> 0.85$), OR
  - An entity triggers $\ge 3$ correlated suspicious events within the time window, OR
  - An entity demonstrates progression across $\ge 2$ kill-chain phases.
- **FR-4.4**: The incident record shall store `incident_code`, `title`, `primary_entity`, `attack_category`, `severity`, `status`, `start_time`, `end_time`, `current_risk_score`, and `confidence_rating`.

### Module 5: Explainable Risk Scoring & Signal Agreement
- **FR-5.1**: The system shall calculate a transparent risk score from 0 to 100 for each incident using the weighted additive formula:
  $$\text{Risk} = \min\left(100, W_{\text{rule}} + W_{\text{ml}} + W_{\text{anomaly}} + W_{\text{behavior}} + W_{\text{correlation}}\right)$$
- **FR-5.2**: The system must provide the exact numerical and percentage contribution of each factor in the API response.
- **FR-5.3**: The system shall assess **Signal Agreement (Detection Confidence)**:
  - Strong Agreement: Rules, ML Classifier, and Isolation Forest all indicate malicious/abnormal activity ($90 - 100\%$).
  - Moderate Agreement: 2 of 3 signals indicate malicious activity ($60 - 85\%$).
  - Conflicting Signals: Only 1 signal indicates malicious activity ($30 - 55\%$), flagging the incident as "Review Required".

### Module 6: Attack Reconstruction Studio (Primary USP)
- **FR-6.1**: The system shall provide an interactive incident timeline endpoint (`GET /api/v1/incidents/{id}/timeline`) returning all correlated events in chronological sequence with step-specific risk scores, triggered detections, and phase labels.
- **FR-6.2**: The frontend shall implement an interactive timeline scrubber and playback controller (Play, Pause, Step Forward, Step Backward, Speed 1x/2x/5x).
- **FR-6.3**: When the analyst scrubs or steps through the timeline, the interface shall update all surrounding widgets in real-time:
  - Active event snapshot
  - Cumulative risk progression chart
  - Entity behavioral delta table (baseline vs event-time activity)
  - Triggered rule evidence and ML confidence breakdown
- **FR-6.4**: Every evidence item displayed in the reconstruction view must maintain a direct link to the underlying immutable raw event.

### Module 7: Network Event Simulator
- **FR-7.1**: The system shall include an integrated simulator capable of generating synthetic background traffic (HTTP, HTTPS, DNS, normal SSH) at configurable intervals.
- **FR-7.2**: The simulator shall support on-demand triggering of 5 pre-programmed attack scenarios:
  1. *Brute Force*: Rapid authentication failures followed by unauthorized access.
  2. *Port Scan*: Vertical and horizontal port discovery sweeps.
  3. *Compromised Account*: Unusual login origin followed by privilege/internal probing.
  4. *Data Exfiltration*: High-volume outbound transfer to external destination over suspicious port.
  5. *Full Kill-Chain*: Sequential end-to-end execution of Recon $\to$ Access $\to$ Pivot $\to$ Exfil.
- **FR-7.3**: The simulator must be controllable via both REST API (`/api/v1/simulator/*`) and UI buttons in the React dashboard.

### Module 8: Security & Role-Based Access Control
- **FR-8.1**: Passwords must be hashed using `bcrypt`.
- **FR-8.2**: Authentication must use signed JSON Web Tokens (JWT) with standard expiry and refresh capabilities.
- **FR-8.3**: Role-based access control (RBAC) must enforce the following permissions:
  - `Admin`: Full access (Rule updates, user management, simulator control).
  - `Analyst`: Incident investigation, status transition (`INVESTIGATING`, `RESOLVED`, `FALSE_POSITIVE`), evidence review, simulator control.
  - `Viewer`: Read-only access to dashboards and incident timelines.
- **FR-8.4**: System actions (status modifications, rule toggles) must be logged in an audit table.

---

## 4. Non-Functional Requirements (NFR)

| NFR ID | Category | Requirement | Verification Method |
| :--- | :--- | :--- | :--- |
| **NFR-01** | **Ingestion Latency** | Pipeline processing time from HTTP receipt to database persistence and rule evaluation must be $< 150\text{ ms}$ per single event. | Backend integration benchmark under 50 events/sec. |
| **NFR-02** | **Reconstruction Response** | Querying reconstructed incident timeline ($< 1,000$ events) must return in $< 400\text{ ms}$. | API performance testing with sample incident datasets. |
| **NFR-03** | **WebSocket Delivery** | Real-time WebSocket dispatch latency must be $< 50\text{ ms}$ post-database commit. | Client-side WebSocket timestamp delta measurement. |
| **NFR-04** | **Hardware Feasibility** | The complete system must run smoothly inside Docker Compose on student laptops ($\ge 8\text{ GB}$ RAM, 4 CPU cores, x86_64 or Apple Silicon ARM64) without dedicated GPUs. | Docker resource profiling under active simulation. |
| **NFR-05** | **ML Model Footprint** | Serialized ML models must occupy $< 15\text{ MB}$ disk space and $< 200\text{ MB}$ runtime RAM memory. | Process memory profiling upon model initialization. |
| **NFR-06** | **Scientific Integrity** | No hardcoded or faked ML evaluation metrics; all reported precision, recall, and F1 metrics must derive from verified test-set evaluations. | Inspection of `ml/evaluation/evaluate.py` output scripts. |
| **NFR-07** | **Data Integrity** | Foreign key referential integrity between events, rule matches, ML predictions, and incidents; raw events must remain immutable. | Database constraint verification tests. |
| **NFR-08** | **UI Responsiveness** | Frontend dashboard must load in $< 2\text{ seconds}$ and maintain 60 FPS animation/scrubbing performance during timeline playback. | Chrome DevTools performance audit. |
| **NFR-09** | **Security Hardening** | No plaintext credentials or API keys stored in Git repository; parameterized ORM queries preventing SQL injection; CORS configured for designated frontend origins. | Static code analysis and repository security review. |

---

## 5. User Stories & Acceptance Criteria

### Story 1: Analyst Identifies an Emerging Incident
- **As a** SOC Analyst,
- **I want to** observe incoming network events in real-time with automated threat tags,
- **So that** I can spot suspicious activity without manually refreshing pages or sifting through raw logs.
- **Acceptance Criteria**:
  - Live Monitor table updates dynamically via WebSockets.
  - Suspicious events are highlighted with severity badges (`HIGH`, `CRITICAL`).
  - Active incidents table increments automatically when an incident threshold is breached.

### Story 2: Reconstructing an Attack Progression (Primary USP)
- **As a** SOC Analyst,
- **I want to** replay an incident step-by-step using an interactive timeline slider,
- **So that** I can understand the attacker's progression from initial reconnaissance to data exfiltration and explain what changed over time.
- **Acceptance Criteria**:
  - Dragging the timeline slider updates the current event display, cumulative risk curve, and behavioral delta card.
  - Auto-play button steps through events chronologically with visual progress indicators.
  - Each step indicates the active kill-chain phase and rule/ML evidence.

### Story 3: Verifying Behavioral Deviation
- **As a** SOC Analyst,
- **I want to** compare an entity's current activity metrics against its established normal baseline,
- **So that** I have quantitative evidence of anomalous behavior (e.g. unexpected outbound connections or protocol surges).
- **Acceptance Criteria**:
  - Investigation view displays baseline values alongside incident-window values.
  - Z-scores and percentage changes are clearly presented with color-coded severity indicators.
