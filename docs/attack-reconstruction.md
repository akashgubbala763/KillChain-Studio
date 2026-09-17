# Interactive Attack Reconstruction & Behavioral Deviation Specification (Primary USP)

## Intelligent Network Security Monitoring & Attack Reconstruction Platform

---

## 1. Executive Summary & Core USP Concept

The central innovation and primary differentiating feature of this platform is the **Interactive Attack Reconstruction Studio & Behavioral Deviation Analysis Engine**.

Most security monitoring systems (even commercial ones) simply display a static table of triggered alerts or a wall of raw log entries. An analyst is left with the burden of mentally piecing together what happened, how the attacker gained a foothold, what changed in the host's normal behavior, and how the threat escalated over time.

This platform transforms static alerts into an **interactive, chronological temporal narrative**:
- **WHAT happened?** The specific malicious actions and evidence supporting each detection.
- **WHEN did it happen?** The exact temporal progression across cyber kill-chain phases.
- **WHAT CHANGED?** Quantitative behavioral deviation showing how the affected entity's current metrics depart from its learned baseline.
- **HOW DID RISK EVOLVE?** A dynamic risk progression curve showing how score rose from benign to critical as the attacker advanced.

---

## 2. Temporal Kill-Chain Phase Progression

The attack reconstruction engine maps correlated events into standard cybersecurity kill-chain phases:

```text
  [STAGE 1: RECONNAISSANCE]
  - Horizontal/Vertical Port Sweeps
  - Host & Service Discovery
            │
            ▼
  [STAGE 2: INITIAL ACCESS]
  - Brute Force Authentication Attempts
  - Credential Stuffing & Unauthorized Login
            │
            ▼
  [STAGE 3: INTERNAL ACTIVITY & LATERAL MOVEMENT]
  - Internal Pivoting (Accessing DBs, File Shares)
  - Abnormal Internal Connections
            │
            ▼
  [STAGE 4: ACTION ON OBJECTIVES & EXFILTRATION]
  - High-Volume Outbound Data Transfer
  - Connection to Suspicious External C2 Ports (e.g. 4444)
```

---

## 3. Interactive Attack Reconstruction Studio UI Architecture

The React investigation interface (`src/pages/Investigation.tsx`) is architected with three tightly synchronized components:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ INC-2026-0001: Multi-Stage Compromise & Data Exfiltration                              │
│ Severity: CRITICAL | Risk: 87/100 | Confidence: 94% (High Agreement) | Status: OPEN    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [⏮ Step Back]  [▶ Play / ⏸ Pause]  [⏭ Step Forward]  [Speed: 1x ▾]  [Step 3 of 6]      │
│ ──────────────────────────●─────────────────────────────────────────────────────────── │
│  10:31:02              10:31:15              10:31:24              10:31:37            │
│  Failed Login          Port Scan          Internal Pivot          Data Exfil           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ CURRENT STEP FORENSIC VIEW (Step 3: 10:31:24)                                          │
│ ┌───────────────────────────────┐ ┌──────────────────────────────────────────────────┐ │
│ │ Cumulative Risk Progression   │ │ Entity Behavioral Deviation (192.168.1.150)      │ │
│ │  100 ┤              ● 87/100  │ │ Metric         Baseline     Current    Z-Score   │ │
│ │   75 ┤           ╭──╯         │ │ SSH Logins:    0/hr         14/hr      +14.0 (🚨)│ │
│ │   50 ┤      ╭────╯            │ │ Upload Vol:    5 MB/hr      85 MB/hr   +16.0 (🚨)│ │
│ │   25 ┤  ╭───╯                 │ │ Unique Ports:  4/hr         47/hr      +28.6 (🚨)│ │
│ │    0 ┴──┴───────┴───────┴───  │ │ DNS Queries:   80/hr        92/hr       +1.5 (🟢)│ │
│ │      10:31:02 10:31:15 10:31  │ └──────────────────────────────────────────────────┘ │
│ └───────────────────────────────┘                                                      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ FORENSIC EVIDENCE AT ACTIVE STEP                                                       │
│ - Triggered Rules: [RULE-SP-01] Known Malicious C2 Port 4444                           │
│ - Supervised Classifier: DataExfiltration (96% Confidence)                             │
│ - Unsupervised Anomaly: Score 0.97 (Extreme Outlier)                                   │
│ - Raw Event Packet: TCP 192.168.1.150:52410 -> 198.51.100.44:4444 (85 MB transferred) │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Playback Controller Mechanics

1. **Stateful Step Index ($k \in [1, N]$)**:
   - When the user presses **Play**, a JavaScript timer advances the step index every interval (e.g. 1500ms at 1x speed, 750ms at 2x speed).
   - Dragging the timeline slider directly sets the step index to $k$.
2. **Deterministic State Synchronization**:
   - At step $k$, all components query the pre-calculated slice of incident events from $1$ to $k$:
     - **Active Event Card**: Displays event metadata for step $k$.
     - **Cumulative Risk Curve**: Draws the risk line up to step $k$, with a glowing highlight point at $(T_k, \text{Risk}_k)$.
     - **Behavioral Comparison Card**: Evaluates the cumulative deviation up to time $T_k$.
     - **Evidence Matrix**: Displays all rules and ML predictions triggered up to step $k$.
3. **Forensic Integrity**:
   - The analyst can click **"Inspect Raw Packet"** at any step to view the exact, immutable JSON payload stored in `network_events`.

---

## 5. Behavioral Deviation Comparison Matrix

The behavioral analysis engine computes a direct before-and-after comparison table for the involved primary entity:

| Behavioral Dimension | Monitored Normal Baseline | Active Incident Snapshot | Standard Score ($Z$) | Evaluation Status |
| :--- | :--- | :--- | :--- | :--- |
| **SSH Connections** | $0 \text{ / hour}$ ($\sigma = 1.0$) | $14 \text{ / hour}$ | $+14.0$ | 🚨 **Severe Anomaly** |
| **Outbound Upload Volume** | $5.2 \text{ MB / hour}$ ($\sigma = 1.5$) | $85.0 \text{ MB / hour}$ | $+53.2$ | 🚨 **Severe Anomaly** |
| **Unique Destination Ports** | $4 \text{ / hour}$ ($\sigma = 1.5$) | $47 \text{ / hour}$ | $+28.6$ | 🚨 **Severe Anomaly** |
| **DNS Request Frequency** | $80 \text{ / hour}$ ($\sigma = 8.0$) | $92 \text{ / hour}$ | $+1.5$ | 🟢 **Within Normal Range** |
| **Failed Authentications** | $0 \text{ / hour}$ ($\sigma = 0.5$) | $6 \text{ / hour}$ | $+12.0$ | 🚨 **Severe Anomaly** |

### Visual Delta Representation
The frontend renders these differences as visual comparison bars:
- **Baseline Bar**: Cool slate gray showing expected operating range.
- **Incident Bar**: Dynamic color (Amber for moderate deviation, Crimson for severe deviation).
- **Z-Score Badge**: Explicit numeric tag (e.g. `+14.0σ`) providing mathematical justification.
