# Multi-Signal Detection & Correlation Engine Specification

## Intelligent Network Security Monitoring & Attack Reconstruction Platform

---

## 1. Multi-Signal Detection Philosophy

Modern threats easily bypass single-vector detection systems. Signature rules fail against zero-days, pure supervised ML struggles on out-of-distribution traffic, and pure anomaly detectors produce alert fatigue.

This platform solves this by coupling three independent intelligence sources into a unified, transparent correlation engine:

```text
                               RAW NETWORK EVENT
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
 [SIGNAL A: RULES]              [SIGNAL B: ML]               [SIGNAL C: ANOMALY]
 Deterministic Engine          Supervised Classifier         Isolation Forest
 - Known Attack Patterns       - Multiclass Probabilities    - Multivariate Outliers
 - Strict Evidence Record      - Feature Importance          - Unsupervised Profiling
        │                              │                              │
        └──────────────────────────────┼──────────────────────────────┘
                                       ▼
                       [SIGNAL COMBINER & CONFIDENCE]
                                       │
                                       ▼
                       [BEHAVIORAL BASELINE DEVIATION]
                                       │
                                       ▼
                         [EVENT CORRELATION ENGINE]
                                       │
                                       ▼
                         [EXPLAINABLE RISK SCORING]
```

---

## 2. Signal A: Deterministic Rule Engine

Deterministic rules provide instant, unambiguous matching for well-understood attack patterns. Every triggered rule produces a structured forensic evidence object.

### Rule 1: SSH / Service Brute Force (`RULE-BF-01`)
- **Category**: Initial Access / Credential Probing
- **Condition**: $\ge N$ failed authentication attempts from the same source IP/user against a target within time window $T$.
- **Default Parameters**:
  - `threshold_attempts`: 5
  - `window_seconds`: 60
- **Severity**: `HIGH`
- **Evidence Structure**:
  ```json
  {
    "rule_code": "RULE-BF-01",
    "trigger_type": "AUTHENTICATION_THRESHOLD_EXCEEDED",
    "source_ip": "192.168.1.150",
    "target_ip": "10.0.0.5",
    "attempt_count": 6,
    "window_seconds": 60,
    "user_targeted": "root",
    "explanation": "6 failed login attempts observed within 42 seconds."
  }
  ```

### Rule 2: Horizontal / Vertical Port Scan (`RULE-PS-01`)
- **Category**: Reconnaissance
- **Condition**: A single source IP initiates connections to $\ge P$ unique destination ports (vertical) or across multiple destination hosts (horizontal) within time window $T$.
- **Default Parameters**:
  - `unique_port_threshold`: 15
  - `window_seconds`: 30
- **Severity**: `MEDIUM` / `HIGH`
- **Evidence Structure**:
  ```json
  {
    "rule_code": "RULE-PS-01",
    "trigger_type": "PORT_SWEEP_DETECTED",
    "source_ip": "192.168.1.150",
    "unique_ports_contacted": 22,
    "ports_sample": [21, 22, 23, 25, 80, 443, 3306, 8080],
    "window_seconds": 18,
    "explanation": "22 unique destination ports probed in 18 seconds."
  }
  ```

### Rule 3: Network Traffic Surge (`RULE-BW-01`)
- **Category**: Anomalous Volume / Denial of Service
- **Condition**: Total bytes transmitted by an entity in a 5-minute interval exceeds $M \times$ its established hourly average.
- **Default Parameters**:
  - `multiplier`: 5.0
  - `min_bytes_threshold`: 50,000,000 (50 MB)
- **Severity**: `HIGH`
- **Evidence Structure**:
  ```json
  {
    "rule_code": "RULE-BW-01",
    "trigger_type": "TRAFFIC_VOLUME_SURGE",
    "observed_bytes": 125829120,
    "baseline_avg_bytes": 15000000,
    "surge_factor": 8.38,
    "explanation": "Outbound traffic is 8.38x higher than baseline hourly average."
  }
  ```

### Rule 4: Suspicious Port / Known C2 Beaconing (`RULE-SP-01`)
- **Category**: Command & Control / Egress
- **Condition**: Connection established over high-risk or known malware/C2 ports (e.g. 4444 [Metasploit], 6667 [IRC Botnets], 1337, 31337 [Back Orifice]).
- **Severity**: `HIGH`
- **Evidence Structure**:
  ```json
  {
    "rule_code": "RULE-SP-01",
    "trigger_type": "KNOWN_MALICIOUS_PORT",
    "destination_port": 4444,
    "destination_ip": "198.51.100.44",
    "explanation": "Outbound TCP connection to known Metasploit default listener port 4444."
  }
  ```

### Rule 5: Repeated Connection Drops & TCP Probing (`RULE-RF-01`)
- **Category**: Reconnaissance / Active Probing
- **Condition**: Ratio of TCP RST or dropped SYN packets exceeds 75% across $\ge 20$ attempts.
- **Severity**: `MEDIUM`
- **Evidence Structure**:
  ```json
  {
    "rule_code": "RULE-RF-01",
    "trigger_type": "FAILED_HANDSHAKE_CLUSTER",
    "reset_count": 28,
    "total_attempts": 30,
    "failure_ratio": 0.933,
    "explanation": "93.3% of connection attempts resulted in TCP RST/rejection."
  }
  ```

### Rule 6: Large Data Exfiltration Threshold (`RULE-EX-01`)
- **Category**: Exfiltration
- **Condition**: Outbound data transfer to an external IP $> 50\text{ MB}$ within 10 minutes over non-standard protocols.
- **Severity**: `CRITICAL`
- **Evidence Structure**:
  ```json
  {
    "rule_code": "RULE-EX-01",
    "trigger_type": "LARGE_EGRESS_TRANSFER",
    "bytes_transferred": 85000000,
    "destination_ip": "198.51.100.44",
    "protocol": "TCP",
    "explanation": "85.0 MB transferred to external IP 198.51.100.44 within 2 minutes."
  }
  ```

---

## 3. Behavioral Baseline & Statistical Deviation Engine

The behavioral baseline engine quantifies how an entity's current behavior departs from its established profile.

### 3.1 Monitored Dimensions
For each entity (IP, Hostname, User Account):
1. $c$: Connection attempts per hour
2. $b$: Outbound bytes per hour
3. $p$: Count of unique destination ports accessed per hour
4. $f$: Failed authentication attempts per hour

### 3.2 Statistical Standard Score (Z-Score)
For each metric $x_i$:
$$Z_i = \frac{x_i - \mu_i}{\sigma_i + \epsilon}$$
Where:
- $\mu_i$: Historical mean
- $\sigma_i$: Historical standard deviation
- $\epsilon = 10^{-5}$: Stability constant preventing zero-division

### 3.3 Deviation Classification
- **Normal Activity**: $|Z_i| < 2.0$
- **Anomalous Activity**: $2.0 \le |Z_i| < 3.5$
- **Severe Statistical Deviation**: $|Z_i| \ge 3.5$

### 3.4 Baseline Update Mechanics (EMA)
To prevent rapid poisoning while allowing gradual operational shifts, baselines update with an Exponential Moving Average (EMA) with decay factor $\alpha = 0.05$:
$$\mu_{\text{new}} = (1 - \alpha)\mu_{\text{old}} + \alpha x$$
$$\sigma_{\text{new}} = \sqrt{(1 - \alpha)\sigma_{\text{old}}^2 + \alpha (x - \mu_{\text{new}})^2}$$

---

## 4. Event Correlation & Incident Grouping Engine

Individual security events are clustered into cohesive incidents using a multi-factor graph approach:

```text
    EVENT 1               EVENT 2               EVENT 3
 (10:31:02 - SSH Fail)   (10:31:15 - Port Scan)  (10:31:37 - Exfil)
          \                      |                      /
           \                     |                     /
            ▼                    ▼                    ▼
     [Entity: 192.168.1.150] + [Sliding Window: 15 min] + [Phase Transitions]
                                 │
                                 ▼
                    [UNIFIED INCIDENT CREATION]
                           INC-2026-0001
```

### Correlation Criteria
1. **Entity Convergence**: Events sharing `source_ip`, target `destination_ip`, or authenticated `user_identifier`.
2. **Temporal Window**: Events occurring within 15 minutes of the most recent correlated event.
3. **Kill-Chain Stage Progression**: Mapping event behavior across sequential attack phases:
   - Phase 1: **Reconnaissance** (Port scans, sweeps)
   - Phase 2: **Initial Access** (Brute force, credential access)
   - Phase 3: **Internal Activity / Pivoting** (Database access, lateral connections)
   - Phase 4: **Exfiltration / Impact** (Data transfer, bandwidth surge)

---

## 5. Explainable Risk Scoring Engine ($0 - 100$)

The risk score reflects how dangerous the incident appears based on five transparent, auditable factors:

$$\text{Risk} = \min\left(100, W_{\text{rule}} + W_{\text{ml}} + W_{\text{anomaly}} + W_{\text{behavior}} + W_{\text{correlation}}\right)$$

### Factor Breakdown

| Component | Max Points | Formula / Calculation | Rationale |
| :--- | :--- | :--- | :--- |
| **$W_{\text{rule}}$ (Rule Severity)** | **35** | `CRITICAL` $\to 35$, `HIGH` $\to 25$, `MEDIUM` $\to 15$, `LOW` $\to 5$ | Highest deterministic rule violation detected in the incident. |
| **$W_{\text{ml}}$ (ML Classification)** | **25** | $P(\text{Attack}) \times 25$ | Supervised Random Forest probability that traffic is malicious. |
| **$W_{\text{anomaly}}$ (Anomaly Score)** | **15** | $\text{Score}_{\text{norm}} \times 15$ | Isolation Forest distance from the normal cluster. |
| **$W_{\text{behavior}}$ (Baseline Deviation)** | **15** | $\min\left(15, \frac{\max(0, Z - 2.0)}{4.0} \times 15\right)$ | Statistical $Z$-score departure from historical entity norms. |
| **$W_{\text{correlation}}$ (Incident Scale)** | **10** | $\min\left(10, (\text{Events} \times 2) + (\text{Phases} \times 2)\right)$ | Multi-event accumulation and progression across kill-chain phases. |

Every risk assessment returns the exact point-by-point breakdown so analysts can verify why a score increased.

---

## 6. Detection Confidence & Signal Agreement Engine

Detection confidence is distinct from risk:
- **Risk**: How dangerous the incident appears ($0 - 100$).
- **Confidence**: How strongly the detection signals agree ($0 - 100\%$).

### Signal Agreement Matrix

| Rule Engine | Random Forest | Isolation Forest | Consensus Level | Confidence Rating | Action Flag |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Malicious** | **Malicious** | **Anomalous** | **STRONG AGREEMENT** | **$90\% - 98\%$** | Immediate Triage |
| **Malicious** | **Malicious** | Normal | **MODERATE** | **$75\% - 85\%$** | High Priority |
| **Malicious** | Normal | **Anomalous** | **MODERATE** | **$70\% - 80\%$** | Investigate |
| Normal | **Malicious** | **Anomalous** | **MODERATE** | **$65\% - 75\%$** | Investigate |
| Normal | **Malicious** | Normal | **CONFLICTING** | **$35\% - 50\%$** | Review Required |
| **Malicious** | Normal | Normal | **CONFLICTING** | **$40\% - 55\%$** | Review Required |
| Normal | Normal | **Anomalous** | **WEAK** | **$25\% - 40\%$** | Low Priority |
| Normal | Normal | Normal | **BENIGN** | **$5\% - 15\%$** | Discard / Filter |
