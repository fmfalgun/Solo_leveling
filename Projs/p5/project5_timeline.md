# Project 5: Threat Hunting AI - Detailed Timeline & Gantt Chart
## 8-Week Week-by-Week Execution Plan with Critical Path Analysis

---

## EXECUTIVE TIMELINE

```
Project Duration: 8 Weeks (300-360 hours)
Recommended Start: January 2027 (Post-Projects 1-4)
Expected Completion: February-March 2027
Pace: 35-45 hours/week sustained
Critical Path: Weeks 1-4 (data prep + ML training: 160 hours)
```

---

## PHASE-LEVEL GANTT CHART (8 WEEKS)

```
THREAT HUNTING AI PLATFORM TIMELINE
═══════════════════════════════════════════════════════════════════════════════

PHASE 1: DATA PREPARATION (Weeks 1-2, 60 hours)
├─ Week 1: Dataset Collection & Exploration
│  └─ ████████████████████ 100%
└─ Week 2: Feature Engineering & Preprocessing
   └─ ████████████████████ 100%
   
   Deliverable: Cleaned dataset with 80+ features ✓

PHASE 2: ML MODELS (Weeks 3-4, 80 hours)
├─ Week 3: Traditional ML Models
│  └─ ████████████████████ 100%
└─ Week 4: Deep Learning Models
   └─ ████████████████████ 100%
   
   Deliverable: Trained ensemble model (95%+ accuracy) ✓

PHASE 3: MITRE INTEGRATION (Week 5, 40 hours)
├─ MITRE ATT&CK Mapping
│  └─ ████████████████████ 100%
└─ Hunt Hypothesis Documentation
   └─ ████████████████████ 100%
   
   Deliverable: 100+ techniques mapped, 6 hypotheses ✓

PHASE 4: ALERTS & AUTOMATION (Week 6, 40 hours)
├─ Alert Generation System
│  └─ ████████████████████ 100%
└─ Automated Hunt Execution
   └─ ████████████████████ 100%
   
   Deliverable: Automated threat detection working ✓

PHASE 5: DASHBOARDS & APIs (Week 7, 40 hours)
├─ Web Dashboard
│  └─ ████████████████████ 100%
├─ REST API
│  └─ ████████████████████ 100%
└─ CLI Tool
   └─ ████████████████████ 100%
   
   Deliverable: Complete user interface ✓

PHASE 6: VALIDATION & PUBLISHING (Week 8, 40 hours)
├─ Testing & Case Studies
│  └─ ████████████████████ 100%
└─ Documentation & Release
   └─ ████████████████████ 100%
   
   Deliverable: Production-ready system ✓

TOTAL: 300 hours across 8 weeks
```

---

## DETAILED WEEK-BY-WEEK BREAKDOWN

### WEEK 1: DATA COLLECTION & EXPLORATION (40 hours)

```
MONDAY: CDAC Dataset Setup (8 hours)
├─ 09:00-10:30 (1.5h): Load CDAC attack dataset
├─ 10:30-12:00 (1.5h): Exploratory data analysis (EDA)
├─ 13:00-14:30 (1.5h): Statistical summary & visualization
├─ 14:30-16:00 (1.5h): Identify attack types, patterns
├─ 16:00-17:00 (1h): Data quality assessment
└─ Notes: Record findings, visualize distributions

TUESDAY: UNSW-NB15 Integration (8 hours)
├─ 09:00-11:00 (2h): Download & extract UNSW-NB15 (2.5M records)
├─ 11:00-13:00 (2h): Format alignment (same schema as CDAC)
├─ 13:00-15:00 (2h): Combine datasets (unified training set)
├─ 15:00-16:00 (1h): Statistical analysis (class distribution)
└─ 16:00-17:00 (1h): Duplicate detection & removal

WEDNESDAY: Bot-IoT & Other Datasets (8 hours)
├─ 09:00-11:00 (2h): Download Bot-IoT dataset
├─ 11:00-13:00 (2h): Format alignment & integration
├─ 13:00-15:00 (2h): Data quality checks
├─ 15:00-16:00 (1h): Missing value handling
└─ 16:00-17:00 (1h): Outlier detection

THURSDAY: Data Profiling (8 hours)
├─ 09:00-10:30 (1.5h): Feature analysis (50+ features)
├─ 10:30-12:00 (1.5h): Correlation analysis
├─ 13:00-14:30 (1.5h): Class imbalance assessment
├─ 14:30-16:00 (1.5h): Temporal analysis (time patterns)
└─ 16:00-17:00 (1h): Documentation

FRIDAY: Summary & Planning (8 hours)
├─ 09:00-11:00 (2h): Consolidate Week 1 findings
├─ 11:00-13:00 (2h): Create data dictionary (80+ features)
├─ 13:00-14:30 (1.5h): Plan feature engineering approach
├─ 14:30-16:00 (1.5h): Document insights & decisions
└─ 16:00-17:00 (1h): Team review (if applicable)

WEEK 1 SUMMARY: 40 hours
├─ Datasets explored: 3+ (CDAC, UNSW-NB15, Bot-IoT)
├─ Records processed: 5M+
├─ Features identified: 50+
└─ Foundation: Complete understanding of data
```

### WEEK 2: FEATURE ENGINEERING & PREPROCESSING (40 hours)

```
MONDAY-TUESDAY: Feature Extraction (16 hours)
├─ Network features (flow duration, packet count, byte count)
├─ Temporal features (time-of-day, day-of-week, inter-arrival time)
├─ Statistical features (mean, std, min, max per flow)
├─ Behavioral features (protocol ratios, flag combinations)
├─ Create 80+ total features
└─ Code: Pandas + NumPy feature engineering

WEDNESDAY: Encoding & Scaling (8 hours)
├─ One-hot encoding (categorical variables)
├─ Label encoding (low-cardinality features)
├─ StandardScaler (normalize features to mean=0, std=1)
├─ MinMaxScaler (scale to 0-1 range)
└─ Test pipeline on sample data

THURSDAY: Train/Test Split (8 hours)
├─ Stratified split (maintain class distribution)
├─ Train: 60%, Validation: 20%, Test: 20%
├─ SMOTE (handle class imbalance)
├─ Class weights (give minority class higher weight)
└─ Verify no data leakage

FRIDAY: Pipeline & Validation (8 hours)
├─ sklearn Pipeline (reproducible preprocessing)
├─ Save pipeline (pickle format)
├─ Document feature list (80+ features)
├─ Performance baseline (simple models)
└─ Phase 1 Complete ✓

WEEK 2 SUMMARY: 40 hours
├─ Features engineered: 80+
├─ Train/test split: Created
├─ No data leakage: Verified
└─ Ready for ML model training
```

### WEEK 3: TRADITIONAL ML MODELS (40 hours)

```
MONDAY: Isolation Forest (8 hours)
├─ Implement sklearn IsolationForest
├─ Hyperparameter tuning:
│  ├─ contamination: 0.03, 0.05, 0.1
│  ├─ n_estimators: 100-1000
│  └─ max_samples: auto vs fixed
├─ Training (full dataset)
├─ Evaluate: accuracy, precision, recall, F1, ROC-AUC

TUESDAY: Statistical Methods (8 hours)
├─ Baseline detection (mean ± 2σ)
├─ Mahalanobis distance
├─ Z-score method
├─ Compare with Isolation Forest

WEDNESDAY: Random Forest Classifier (8 hours)
├─ Supervised learning (labeled attacks)
├─ Hyperparameter tuning
├─ Cross-validation (k-fold=5)
├─ Feature importance analysis

THURSDAY-FRIDAY: SVM & Ensemble (16 hours)
├─ One-Class SVM (novelty detection)
├─ Multi-class SVM
├─ Voting Classifier (ensemble)
├─ Performance comparison (all models)
└─ Select top 3 for final ensemble

WEEK 3 SUMMARY: 40 hours
├─ Models trained: 5+
├─ Accuracy: 94-95%
├─ FPR: 3-5% (need to reduce)
└─ Ready for deep learning models
```

### WEEK 4: DEEP LEARNING & ENSEMBLE (40 hours)

```
MONDAY-TUESDAY: LSTM Autoencoder (16 hours)
├─ Architecture design:
│  ├─ Encoder: 2x LSTM (128→64)
│  ├─ Decoder: 2x LSTM (64→128)
│  └─ Sequence length: 30 timesteps
├─ Training (50-100 epochs)
├─ Hyperparameter tuning:
│  ├─ Learning rate: 0.001-0.01
│  ├─ Batch size: 32-256
│  └─ Early stopping patience: 10 epochs

WEDNESDAY: GRU & Final Models (8 hours)
├─ GRU implementation (compare to LSTM)
├─ ConvLSTM (optional, if needed)
├─ Model performance comparison

THURSDAY-FRIDAY: Ensemble & Evaluation (16 hours)
├─ Ensemble: Voting across 5+ models
├─ Performance metrics:
│  ├─ Accuracy ≥95%
│  ├─ Precision ≥94%
│  ├─ Recall ≥96%
│  └─ F1 ≥95%
├─ False positive rate: <3%
├─ Save trained models
└─ Phase 2 Complete ✓

WEEK 4 SUMMARY: 40 hours
├─ Deep learning models: 2-3
├─ Ensemble accuracy: 95%+
├─ FPR reduced to: <3%
└─ Models production-ready
```

### WEEK 5: MITRE INTEGRATION (40 hours)

```
MONDAY-TUESDAY: Detection Rules (16 hours)
├─ YARA rules: 50+ (file-based artifacts)
├─ Sigma rules: 50+ (log patterns)
├─ Suricata rules: 30+ (network patterns)
├─ Test rules against samples

WEDNESDAY: MITRE Mapping (8 hours)
├─ Load MITRE ATT&CK framework
├─ Map 100+ techniques to detection rules
├─ Create mapping database
├─ MITRE Navigator integration

THURSDAY-FRIDAY: Hunt Hypotheses (16 hours)
├─ Document 6 threat hunting hypotheses:
│  ├─ Lateral movement (service accounts)
│  ├─ DNS exfiltration
│  ├─ Token manipulation
│  ├─ C2 communication
│  ├─ Data exfiltration
│  └─ Persistence mechanisms
├─ For each: detection method, data requirements, investigation steps
├─ Create hunt playbooks (PDF documents)
└─ Phase 3 Complete ✓

WEEK 5 SUMMARY: 40 hours
├─ Detection rules: 130+
├─ MITRE techniques: 100+ mapped
├─ Hunt hypotheses: 6 documented
└─ Framework integrated with threat intel
```

### WEEK 6: ALERT SYSTEM & AUTOMATION (40 hours)

```
MONDAY-TUESDAY: Alert Generation (16 hours)
├─ Anomaly score calculation (0-100)
├─ Confidence scoring (model agreement)
├─ Severity assignment (Critical/High/Medium/Low)
├─ MITRE technique attribution
├─ False positive filtering (multi-model voting)

WEDNESDAY: Automated Hunting (8 hours)
├─ Hypothesis-based hunt automation
├─ Scheduled job execution
├─ Evidence collection
├─ Report generation (automated)

THURSDAY-FRIDAY: SIEM Integration (16 hours)
├─ Splunk integration (SPL queries)
├─ ELK integration (KQL queries)
├─ API connectivity (webhook forwarding)
├─ Dashboard alerts configured
└─ Phase 4 Complete ✓

WEEK 6 SUMMARY: 40 hours
├─ Alert pipeline: Working
├─ SIEM integration: Complete
├─ Automation: Operational
└─ Ready for user interface
```

### WEEK 7: DASHBOARDS & APIS (40 hours)

```
MONDAY-TUESDAY: Web Dashboard (16 hours)
├─ Real-time alert display
├─ MITRE ATT&CK navigator overlay
├─ Threat timeline visualization
├─ Hunt status tracking
├─ Evidence gallery & search

WEDNESDAY: REST API (8 hours)
├─ Detection endpoint (/api/detect)
├─ Hunt endpoint (/api/hunt)
├─ Report endpoint (/api/report)
├─ Authentication & rate limiting

THURSDAY-FRIDAY: CLI Tool (16 hours)
├─ Command-line threat hunter interface
├─ Hunt hypothesis execution
├─ Evidence export
├─ Report generation
└─ Phase 5 Complete ✓

WEEK 7 SUMMARY: 40 hours
├─ Dashboard: Operational
├─ API: Documented & tested
├─ CLI: Functional
└─ Full user interface ready
```

### WEEK 8: VALIDATION & PUBLISHING (40 hours)

```
MONDAY: Unit Testing (8 hours)
├─ 100+ test cases
├─ Model training tests
├─ Feature engineering tests
├─ Code coverage >80%

TUESDAY: Integration Testing (8 hours)
├─ End-to-end workflows
├─ Multi-data source correlation
├─ SIEM integration
├─ All tests passing

WEDNESDAY: Case Studies (8 hours)
├─ 5 real threat scenarios
├─ Detection timeline
├─ Investigation steps
├─ Remediation actions

THURSDAY: Documentation (8 hours)
├─ API reference
├─ User guide
├─ Deployment guide
├─ Threat hunting playbook

FRIDAY: Publishing (8 hours)
├─ GitHub release
├─ Blog posts (3-4)
├─ Research paper
└─ Phase 6 Complete ✓

WEEK 8 SUMMARY: 40 hours
├─ Tests: 100+ passing
├─ Case studies: 5 documented
├─ Documentation: Complete
└─ System: Production-ready & published
```

---

## CRITICAL PATH & DEPENDENCIES

```
CRITICAL PATH (Longest Sequence):

Week 1-2: Data Preparation (must complete first)
   ↓ (Dataset ready)
Week 3-4: ML Model Training (cannot start without data)
   ↓ (Models trained)
Week 5: MITRE Integration (independent, can overlap)
   ↓ (Threat context added)
Week 6: Alert System (depends on models + MITRE)
   ↓ (Automation ready)
Week 7: Dashboards & APIs (independent, can overlap)
   ↓ (UI ready)
Week 8: Validation & Publishing (final step)

TOTAL CRITICAL PATH: 8 weeks (sequential)
SLACK: Minimal (can overlap weeks 5 & 7 with previous)

PARALLELIZATION OPPORTUNITIES:
├─ Weeks 1-2 must be sequential (data prep dependent)
├─ Weeks 3-4 must be sequential (training dependent)
├─ Week 5 (MITRE) can start during Week 4
├─ Week 7 (UI) can start during Week 6
└─ Potential compression: 7 weeks (1 week saved via overlap)
```

---

## WEEKLY RESOURCE ALLOCATION

| Week | Phase | Hours | Focus | Key Milestone |
|---|---|---|---|---|
| 1 | P1 | 40 | Data collection & EDA | Datasets understood |
| 2 | P1 | 40 | Feature engineering | 80+ features extracted |
| 3 | P2 | 40 | Traditional ML | 5+ models trained |
| 4 | P2 | 40 | Deep learning | Ensemble working (95%+ acc) |
| 5 | P3 | 40 | MITRE integration | 100+ techniques mapped |
| 6 | P4 | 40 | Alert automation | Alerts operational |
| 7 | P5 | 40 | UI & APIs | Dashboard + API working |
| 8 | P6 | 40 | Testing & publishing | System released |

**TOTAL: 320 hours over 8 weeks (40 hours/week)**

---

**Timeline Version:** 1.0  
**Last Updated:** December 15, 2025  
**Estimated Total Hours:** 300-360 across 8 weeks  
**Critical Path:** 8 weeks (sequential phases)  
**Status:** Ready for Execution  
**Recommended Start:** January 2027
