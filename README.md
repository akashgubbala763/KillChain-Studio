# Intelligent Network Security Monitoring & Attack Reconstruction Platform

> **A focused, transparent, and demonstrable full-stack cybersecurity platform combining multi-signal detection, behavioral deviation analysis, event correlation, and interactive incident reconstruction.**

---

## 🎯 Project Overview

Modern organizations are overwhelmed by security alerts. The fundamental challenge for security analysts is not just detecting whether an individual event is malicious, but understanding:
- **WHAT happened?** The exact techniques and evidence behind the detection.
- **WHEN did it happen?** How the incident evolved over time across the attack lifecycle.
- **WHAT CHANGED?** How the affected entity's behavior deviates from its historical normal baseline.
- **HOW DID RISK PROGRESS?** Transparent, explainable risk escalation rather than an opaque black-box score.

This platform implements an end-to-end pipeline:
```text
Network Activity
       ↓
Event Collection & Normalization
       ↓
Rule-Based Detection + ML Supervised Classification + Anomaly Detection
       ↓
Behavioral Deviation Analysis (Z-Score Baseline Profiling)
       ↓
Event Correlation (Entity-Centric & Sliding Time Window)
       ↓
Explainable Risk Scoring (0–100) & Signal Agreement
       ↓
Interactive Attack Reconstruction (Timeline Scrubbing & Step Replay)
       ↓
Human Analyst Investigation
```

---

## 🌟 Primary Differentiating Feature (USP)

### Interactive Attack Reconstruction & Behavioral Deviation Studio
Instead of showing static log tables, the platform reconstructs multi-stage attacks into an interactive temporal narrative:
- **Interactive Timeline Scrubber & Replay Controller**: Step forward, step backward, or auto-play through an attack at 1x, 2x, or 5x speed.
- **Dynamic Risk Progression Curve**: Visualizes cumulative incident risk escalating step-by-step.
- **Entity Behavioral Delta Matrix**: Real-time statistical comparison of normal entity baselines vs. active attack snapshot metrics (e.g. SSH logins $0 \to 14$, uploads $5 \to 85\text{ MB}$).
- **Kill-Chain Stage Mapping**: Reconnaissance $\to$ Initial Access $\to$ Internal Activity $\to$ Data Exfiltration.
- **Direct Forensic Evidence Trail**: Every alert directly hyperlinks to its underlying immutable raw network packet.

---

## 📚 Complete Phase 0 Documentation Suite

Comprehensive technical design specifications have been completed in [`docs/`](file:///Users/akash/Documents/Major%20Project/docs/):

1. **[System Architecture](file:///Users/akash/Documents/Major%20Project/docs/architecture.md)**: End-to-end data flow, subsystem architecture, and technology justifications.
2. **[Requirements Specification](file:///Users/akash/Documents/Major%20Project/docs/requirements.md)**: Functional requirements (FR-01 to FR-15), non-functional requirements, and user stories.
3. **[Database Design & Schema](file:///Users/akash/Documents/Major%20Project/docs/database.md)**: PostgreSQL relational schemas, UUID keys, indexing, and ER diagrams.
4. **[API Architecture](file:///Users/akash/Documents/Major%20Project/docs/api.md)**: REST endpoints (`/api/v1/*`), Pydantic schemas, and WebSocket streaming.
5. **[Multi-Signal Detection & Correlation](file:///Users/akash/Documents/Major%20Project/docs/detection.md)**: 6 deterministic rules, behavioral baselines ($Z$-scores), correlation heuristics, risk formula, and signal agreement matrix.
6. **[Machine Learning Pipeline](file:///Users/akash/Documents/Major%20Project/docs/ml.md)**: Random Forest classifier, Isolation Forest anomaly detector, feature vectors, and evaluation plan.
7. **[Attack Reconstruction Studio (USP)](file:///Users/akash/Documents/Major%20Project/docs/attack-reconstruction.md)**: Detailed specification of timeline playback, state synchronization, and behavioral diff cards.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0 (Async), Alembic, Pydantic v2
- **Database**: PostgreSQL 16
- **Machine Learning**: Scikit-learn (Random Forest & Isolation Forest), NumPy, Joblib
- **Real-Time Streaming**: WebSockets (FastAPI / Starlette)
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React
- **Data Visualization**: Recharts (SVG risk curves and metric distributions)
- **Containerization**: Docker & Docker Compose

---

## 🗓️ Development Roadmap

- [x] **PHASE 0: Architecture, Requirements & Design Specifications** *(Completed)*
- [ ] **PHASE 1: Repository Setup & Development Foundation** *(Next)*
- [ ] **PHASE 2: Database Schema & Authentication Subsystem (RBAC)**
- [ ] **PHASE 3: Realistic Network Event Simulator**
- [ ] **PHASE 4: Event Ingestion Pipeline & Real-Time WebSockets**
- [ ] **PHASE 5: Deterministic Rule Engine**
- [ ] **PHASE 6: Machine Learning Pipeline (Supervised + Anomaly)**
- [ ] **PHASE 7: Behavioral Baseline Engine (Z-Score Deviation)**
- [ ] **PHASE 8: Event Correlation & Incident Grouping Engine**
- [ ] **PHASE 9: Explainable Risk & Confidence Engine**
- [ ] **PHASE 10: Attack Reconstruction Engine (Primary USP)**
- [ ] **PHASE 11: React SOC Investigation Dashboard**
- [ ] **PHASE 12: Comprehensive Testing & Validation**
- [ ] **PHASE 13: Containerization & Deployment Hardening**
- [ ] **PHASE 14: Final Documentation & Presentation Package**
