# Machine Learning Pipeline & Model Specification

## Intelligent Network Security Monitoring & Attack Reconstruction Platform

---

## 1. Machine Learning Philosophy & Feasibility

The machine learning subsystem is engineered with strict adherence to academic and scientific integrity:
1. **No "Fake AI"**: Alerts triggered by deterministic rules are never credited to ML.
2. **No Faked Metrics**: All reported precision, recall, accuracy, and F1 metrics are evaluated against real test sets and reproducible evaluation scripts.
3. **No Heavy Neural Networks**: Designed around lightweight, highly explainable tree-based algorithms (**Random Forest** and **Isolation Forest**) that execute on standard student CPU hardware with inference latency $< 5\text{ ms}$ and memory usage $< 150\text{ MB}$.
4. **Transparent Explainability**: Every prediction includes class probability distributions and feature contribution weights.

---

## 2. Dataset Strategy & Feature Engineering

### 2.1 Benchmark Foundation
The training pipeline utilizes a normalized subset of the reputable **CIC-IDS2017** and **NSL-KDD** network security datasets, mapped to the system's live telemetry feature schema.

### 2.2 Feature Vector Definition (12 Dimensions)

Every network event is transformed into a fixed-length numerical feature vector $\mathbf{x} \in \mathbb{R}^{12}$:

| Index | Feature Name | Description | Data Type | Normalization |
| :---: | :--- | :--- | :--- | :--- |
| 1 | `source_port` | Ephemeral or service source port | Integer | Scaled $[0, 1]$ |
| 2 | `destination_port` | Target service port | Integer | Scaled $[0, 1]$ |
| 3 | `protocol_encoded` | Categorical encoding (TCP=1, UDP=2, ICMP=3, etc.) | Integer | One-Hot / Label |
| 4 | `bytes_sent` | Total payload and header bytes sent | Float | Log1p + StandardScale |
| 5 | `bytes_received` | Total bytes returned from target | Float | Log1p + StandardScale |
| 6 | `duration_seconds` | Connection flow duration | Float | RobustScale |
| 7 | `packet_count` | Number of packets in flow | Integer | Log1p + StandardScale |
| 8 | `bytes_per_packet` | $\frac{\text{bytes\_sent} + \text{bytes\_received}}{\max(1, \text{packet\_count})}$ | Float | StandardScale |
| 9 | `bytes_ratio` | $\frac{\text{bytes\_sent} + 1}{\text{bytes\_received} + 1}$ | Float | MinMaxScale |
| 10 | `is_syn_only` | 1 if TCP SYN flag set without ACK, else 0 | Binary | Raw |
| 11 | `is_rst` | 1 if TCP RST flag present, else 0 | Binary | Raw |
| 12 | `auth_failure_flag` | 1 if auth event with status FAILURE, else 0 | Binary | Raw |

---

## 3. Model 1: Supervised Random Forest Classifier

### 3.1 Objectives & Target Classes
Classifies network events into 4 discrete operational categories:
- `Class 0`: **Normal** (Standard benign web, DNS, and internal traffic)
- `Class 1`: **PortScan** (Horizontal/vertical reconnaissance)
- `Class 2`: **BruteForce** (High-rate authentication attempts)
- `Class 3`: **DataExfiltration** (Anomalous high-ratio egress transfers)

### 3.2 Hyperparameter Configuration
- `n_estimators`: 100
- `max_depth`: 15
- `min_samples_split`: 5
- `min_samples_leaf`: 2
- `class_weight`: `balanced` (compensates for class imbalance)
- `random_state`: 42 (ensures exact reproducibility)

### 3.3 Evaluation Protocol
- **Data Split**: $70\%$ Training, $15\%$ Validation, $15\%$ Independent Test Set.
- **Stratified K-Fold**: 5-fold cross-validation during tuning.
- **Reported Metrics**:
  - Macro & Weighted Precision, Recall, F1-Score
  - Multi-class Confusion Matrix saved to `ml/models/confusion_matrix.png` and `ml/models/metadata.json`.
  - Multi-class ROC-AUC (One-vs-Rest).

---

## 4. Model 2: Unsupervised Isolation Forest Anomaly Detector

### 4.1 Objectives & Mechanism
Detects novel or zero-day anomalies that do not match existing supervised labels or rule signatures.
- Evaluates the average path length required to isolate a sample in randomized decision trees.
- Outliers have significantly shorter paths than normal points.

### 4.2 Hyperparameter Configuration
- `n_estimators`: 100
- `contamination`: 0.03 (estimated $3\%$ outlier rate in baseline training distribution)
- `max_samples`: 256
- `random_state`: 42

### 4.3 Output Scoring
- **Raw Decision Function**: $s(\mathbf{x}) \in [-1, 1]$.
- **Normalized Anomaly Score**:
  $$\text{Score}_{\text{norm}} = \frac{1 - s(\mathbf{x})}{2} \in [0, 1]$$
  Where values $> 0.65$ indicate high outlier confidence.

---

## 5. Offline Training vs. Online Inference

```text
       OFFLINE TRAINING PIPELINE                ONLINE INFERENCE (FASTAPI)
 ┌────────────────────────────────────┐       ┌───────────────────────────────┐
 │ Benchmark Data (CIC-IDS / NSL-KDD) │       │   Raw Event from Ingestion    │
 └─────────────────┬──────────────────┘       └──────────────┬────────────────┘
                   ▼                                         ▼
 ┌────────────────────────────────────┐       ┌───────────────────────────────┐
 │   Feature Extraction & Scaler      │       │     Extract 12-dim Vector     │
 └─────────────────┬──────────────────┘       └──────────────┬────────────────┘
                   ▼                                         ▼
 ┌────────────────────────────────────┐       ┌───────────────────────────────┐
 │ Train RF Classifier & Iso Forest   │       │   Transform with Scaler.joblib│
 └─────────────────┬──────────────────┘       └──────────────┬────────────────┘
                   ▼                                         ▼
 ┌────────────────────────────────────┐       ┌───────────────────────────────┐
 │ Save Models to ml/models/*.joblib  │──────▶│ In-Memory Predictor (< 5ms)   │
 └────────────────────────────────────┘       └──────────────┬────────────────┘
                                                             ▼
                                              ┌───────────────────────────────┐
                                              │ Returns Prediction & Probabilities
                                              └───────────────────────────────┘
```

1. **Strict Separation**: Models are never trained during live event ingestion. Training is an offline batch process.
2. **Artifact Persistence**: Models are serialized using `joblib` into `ml/models/`:
   - `random_forest.joblib` (~10 MB)
   - `isolation_forest.joblib` (~4 MB)
   - `scaler.joblib` (~50 KB)
   - `metadata.json` (Stores verified performance metrics, training timestamp, Git commit)
3. **Low-Latency Runtime**: The FastAPI application loads the model artifacts into memory once at startup via the lifespan context manager. Vectorized prediction takes $< 3\text{ ms}$ per event.

---

## 6. Documented Limitations & Edge Cases

1. **Encrypted Payloads**: Features rely on transport/flow metadata (ports, bytes, packets, timing). DPI (Deep Packet Inspection) of TLS/SSL payloads is not attempted.
2. **Concept Drift**: Network baselines change when new services deploy. The Isolation Forest must be retrained periodically to adapt to structural topology shifts.
3. **Adversarial Perturbation**: Slow-and-low port scans (e.g. 1 probe every 3 hours) evade short-window supervised models, demonstrating why multi-signal correlation and long-term behavioral baselines are necessary.
