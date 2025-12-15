# ML-Based IDS Project: Complete UML Architecture & Execution Flow
## Phase-by-Phase Tool Integration and Module Dependencies

---

## PART 1: PROJECT EXECUTION SEQUENCE DIAGRAM

```
Timeline (8 weeks)
═══════════════════════════════════════════════════════════════════════════════

Week 1-2: DATA PREPARATION
│
├─→ Data Loader (Python + Jupyter)
│   │
│   ├─ Download NSL-KDD, UNSW-NB15, CIC-IDS-2017
│   │  [Tools: wget, Kaggle CLI]
│   │
│   ├─ Load & Explore (Jupyter Notebook)
│   │  [Tools: Python, Pandas, NumPy, Matplotlib]
│   │
│   └─ Store to PostgreSQL/TimescaleDB
│      [Tools: SQLAlchemy, psycopg2]
│
├─→ Data Cleaning Module
│   │
│   ├─ Remove missing values & duplicates
│   │  [Tools: Pandas .dropna(), drop_duplicates()]
│   │
│   └─ Validation checks
│      [Tools: Pandas validation, data_integrity.py]
│
├─→ Feature Engineering Module
│   │
│   ├─ Categorical encoding (Protocol, Service)
│   │  [Tools: Scikit-learn preprocessing]
│   │
│   ├─ Feature selection (Chi-square ranking)
│   │  [Tools: Scikit-learn feature_selection]
│   │
│   └─ Output: Feature importance report
│      [Tools: Pandas, Matplotlib visualization]
│
└─→ Data Normalization & SMOTE
    │
    ├─ Min-max scaling (0-1 range)
    │  [Tools: scikit-learn.preprocessing.MinMaxScaler]
    │
    ├─ Class balancing via SMOTE
    │  [Tools: imbalanced-learn.SMOTE]
    │
    └─ Train/Val/Test split (70/15/15)
       [Tools: sklearn.model_selection.train_test_split]

        ↓ (Output: Preprocessed datasets → PostgreSQL)
        
═══════════════════════════════════════════════════════════════════════════════

Week 3: MACHINE LEARNING BASELINES
│
├─→ Random Forest Training
│   │
│   ├─ Load preprocessed data from PostgreSQL
│   │  [Tools: SQLAlchemy, pandas.read_sql]
│   │
│   ├─ Hyperparameter tuning (GridSearchCV)
│   │  [Tools: scikit-learn GridSearchCV, 100+ combinations]
│   │
│   ├─ Training (100-500 trees)
│   │  [Tools: scikit-learn.ensemble.RandomForestClassifier]
│   │
│   └─ Save model (pickle format)
│      [Tools: joblib.dump()]
│
├─→ XGBoost Training (Parallel)
│   │
│   ├─ Hyperparameter optimization
│   │  [Tools: XGBoost, early_stopping]
│   │
│   ├─ Training (100-200 boosting rounds)
│   │  [Tools: xgboost.train()]
│   │
│   └─ Model persistence
│      [Tools: xgboost.Booster.save_model()]
│
├─→ SVM Training (Parallel)
│   │
│   ├─ Kernel selection & parameter tuning
│   │  [Tools: scikit-learn SVM, GridSearchCV]
│   │
│   └─ Model saving
│      [Tools: joblib]
│
└─→ Model Comparison & Evaluation
    │
    ├─ Load all 3 baseline models
    │  [Tools: joblib.load()]
    │
    ├─ Generate confusion matrices & ROC curves
    │  [Tools: sklearn.metrics, matplotlib]
    │
    ├─ Calculate Accuracy, Precision, Recall, F1
    │  [Tools: sklearn.metrics classification_report]
    │
    └─ Selection: Best baseline (usually XGBoost ~98%)
       [Tools: Python comparison logic]

        ↓ (Output: 3 trained baseline models + comparison report)

═══════════════════════════════════════════════════════════════════════════════

Week 4-5: DEEP LEARNING MODELS
│
├─→ CNN Model Training (GPU)
│   │
│   ├─ Load data to GPU memory
│   │  [Tools: TensorFlow data.Dataset API, GPU VRAM]
│   │
│   ├─ Build architecture: Conv1D(64)→MaxPool→Conv1D(128)→Dense
│   │  [Tools: Keras.Sequential API, TensorFlow layers]
│   │
│   ├─ Compile model (Binary Cross-Entropy, Adam optimizer)
│   │  [Tools: model.compile() with loss, optimizer, metrics]
│   │
│   ├─ Train (batch_size=128, epochs=50-100)
│   │  [Tools: model.fit() with callbacks]
│   │
│   ├─ Early stopping when val_loss plateaus
│   │  [Tools: tf.keras.callbacks.EarlyStopping]
│   │
│   └─ Save checkpoint (h5 format)
│      [Tools: model.save(), TensorFlow SavedModel]
│
├─→ LSTM Model Training (GPU, Parallel)
│   │
│   ├─ Architecture: LSTM(64,return_seq)→LSTM(128)→Dense
│   │  [Tools: tf.keras.layers.LSTM, Dropout]
│   │
│   ├─ Training with temporal attention
│   │  [Tools: TensorFlow, attention mechanisms (optional)]
│   │
│   ├─ Monitor metrics: Accuracy, Loss, AUC
│   │  [Tools: TensorBoard for visualization]
│   │
│   └─ Save model checkpoint
│      [Tools: model.save()]
│
├─→ CNN-LSTM Hybrid (GPU, Primary Focus)
│   │
│   ├─ Combine Conv1D→LSTM layers
│   │  [Tools: Keras Functional API]
│   │
│   ├─ Complex shape handling & reshaping
│   │  [Tools: tf.reshape, tf.transpose]
│   │
│   ├─ Training & validation
│   │  [Tools: model.fit() with validation_split=0.2]
│   │
│   ├─ Profiling: TensorFlow Profiler for GPU bottlenecks
│   │  [Tools: tf.profiler.experimental.start]
│   │
│   └─ Best performer (99.2-99.5% accuracy)
│      [Tools: TensorFlow, GPU acceleration]
│
├─→ Autoencoder (Unsupervised, GPU)
│   │
│   ├─ Train on normal traffic only (no attacks)
│   │  [Tools: Data filtering, Keras]
│   │
│   ├─ Architecture: Encoder(64→32→16) + Decoder(Mirror)
│   │  [Tools: tf.keras.Model]
│   │
│   ├─ Reconstruction error as anomaly score
│   │  [Tools: MSE loss calculation]
│   │
│   └─ Zero-day detection capability
│      [Tools: Custom anomaly detection logic]
│
└─→ Deep Neural Network (GPU)
    │
    ├─ 5-6 hidden layers with Dropout & BatchNorm
    │  [Tools: tf.keras.layers, regularization]
    │
    ├─ Training with mixed precision
    │  [Tools: tf.keras.mixed_precision]
    │
    ├─ Profiling: PyTorch Profiler (if PyTorch version)
    │  [Tools: torch.profiler]
    │
    └─ Model saving
       [Tools: model.save() or torch.save()]

        ↓ (Output: 5 trained DL models + TensorBoard logs)

═══════════════════════════════════════════════════════════════════════════════

Week 6: ENSEMBLE & OPTIMIZATION
│
├─→ Soft Voting Ensemble
│   │
│   ├─ Load all models (3 baselines + 2-3 best DL models)
│   │  [Tools: joblib.load(), model.load()]
│   │
│   ├─ Calculate weights = accuracy / sum(accuracies)
│   │  [Tools: NumPy, custom weight calculation]
│   │
│   ├─ Weighted averaging on validation set
│   │  [Tools: NumPy weighted averaging]
│   │
│   ├─ Threshold tuning for 99.3%+ accuracy
│   │  [Tools: sklearn.metrics.roc_curve for optimal threshold]
│   │
│   └─ Ensemble model saving
│      [Tools: joblib, pickle for ensemble metadata]
│
├─→ Hyperparameter Tuning (GridSearchCV)
│   │
│   ├─ 100+ parameter combinations
│   │  [Tools: Optuna or sklearn GridSearchCV]
│   │
│   ├─ LSTM units: [64, 128, 256]
│   │  Batch size: [64, 128, 256]
│   │  Learning rate: [0.0001, 0.001, 0.01]
│   │  Dropout: [0.2, 0.3, 0.4]
│   │
│   ├─ 5-fold cross-validation
│   │  [Tools: sklearn.model_selection.cross_val_score]
│   │
│   ├─ Track experiments in MLflow
│   │  [Tools: MLflow tracking server, metrics logging]
│   │
│   └─ Expected +0.2-0.5% accuracy improvement
│      [Tools: Optuna trial optimization]
│
└─→ Model Compression
    │
    ├─ 8-bit quantization
    │  [Tools: TensorFlow Lite converter, post-training quantization]
    │
    ├─ Weight pruning (50% sparsity)
    │  [Tools: TensorFlow Model Optimization Toolkit]
    │
    ├─ Knowledge distillation (optional)
    │  [Tools: Keras distillation layers]
    │
    └─ Maintain 95%+ accuracy, reduce file size 70%
       [Tools: TensorFlow Lite, ONNX export]

        ↓ (Output: Final ensemble model, compressed models, tuning logs)

═══════════════════════════════════════════════════════════════════════════════

Week 7: EVALUATION & VALIDATION
│
├─→ Performance Metrics Calculation
│   │
│   ├─ Test on held-out test set (750K samples)
│   │  [Tools: Ensemble model.predict()]
│   │
│   ├─ Calculate metrics:
│   │  - Accuracy: (TP+TN)/(TP+TN+FP+FN)
│   │  - Precision: TP/(TP+FP)
│   │  - Recall: TP/(TP+FN)
│   │  - F1-Score: 2*(Precision*Recall)/(Precision+Recall)
│   │  [Tools: sklearn.metrics classification_report]
│   │
│   ├─ ROC-AUC & PR-AUC curves
│   │  [Tools: sklearn.metrics roc_auc_score, auc]
│   │
│   └─ Visualize: Confusion matrix heatmap
│      [Tools: matplotlib, seaborn.heatmap]
│
├─→ False Positive Analysis
│   │
│   ├─ Calculate FPR = FP/(FP+TN)
│   │  [Tools: Custom calculation from confusion matrix]
│   │
│   ├─ Target: FPR < 2% (vs industry 5-10%)
│   │  [Tools: Threshold tuning]
│   │
│   ├─ Analyze misclassified normal samples
│   │  [Tools: Pandas groupby, custom analysis]
│   │
│   └─ FPR analysis report + plots
│      [Tools: Matplotlib, seaborn]
│
├─→ Cross-Dataset Validation
│   │
│   ├─ Train on NSL-KDD → Test on UNSW-NB15
│   │  [Tools: Model transfer, Ensemble reuse]
│   │
│   ├─ Train on UNSW-NB15 → Test on CIC-IDS-2017
│   │  [Tools: Model transfer]
│   │
│   └─ Generalization: 95%+ accuracy across datasets
│      [Tools: Performance comparison]
│
├─→ Per-Attack-Type Performance
│   │
│   ├─ Confusion matrix per class
│   │  [Tools: sklearn.metrics multilabel_confusion_matrix]
│   │
│   ├─ Attack types: DoS, DDoS, Probe, Exploit, Generic, Backdoor
│   │  [Tools: Class-wise evaluation]
│   │
│   └─ Target: 99%+ detection for each type
│      [Tools: Per-class metrics calculation]
│
├─→ Latency Testing
│   │
│   ├─ CPU (i7): <5ms per prediction
│   │  [Tools: Python timeit module]
│   │
│   ├─ GPU (RTX 3070): <2.5ms per prediction
│   │  [Tools: NVIDIA profiling tools]
│   │
│   ├─ Throughput: 1,000+ predictions/sec
│   │  [Tools: Batch processing benchmarks]
│   │
│   └─ Latency report + graphs
│      [Tools: Matplotlib, seaborn]
│
└─→ Statistical Validation
    │
    ├─ 95% confidence intervals on accuracy
    │  [Tools: scipy.stats.binom_test]
    │
    ├─ Paired t-tests between models (p < 0.05)
    │  [Tools: scipy.stats.paired_ttest]
    │
    ├─ Bootstrap validation
    │  [Tools: sklearn.utils resample]
    │
    └─ Statistical analysis PDF
       [Tools: Sphinx documentation generation]

        ↓ (Output: Comprehensive evaluation report + all metrics)

═══════════════════════════════════════════════════════════════════════════════

Week 8: PRODUCTION DEPLOYMENT
│
├─→ Model Serving API Development
│   │
│   ├─ Build FastAPI application
│   │  [Tools: FastAPI framework, Pydantic models]
│   │
│   ├─ Endpoints:
│   │  - GET /health → {"status": "healthy"}
│   │  - POST /predict → Single prediction
│   │  - POST /predict_batch → Batch predictions
│   │  - GET /model_metrics → Performance stats
│   │  [Tools: FastAPI route decorators]
│   │
│   ├─ Request validation & error handling
│   │  [Tools: Pydantic BaseModel validation]
│   │
│   └─ API documentation (Swagger UI)
│      [Tools: FastAPI auto-docs generation]
│
├─→ Docker Containerization
│   │
│   ├─ Create multi-stage Dockerfile
│   │  [Tools: Docker, builder pattern]
│   │
│   ├─ Build image: docker build -t ml-ids:latest .
│   │  [Tools: Docker CLI]
│   │
│   ├─ Test locally: docker run -p 5000:5000 ml-ids:latest
│   │  [Tools: Docker runtime]
│   │
│   ├─ Image size: 500MB-1GB (optimized)
│   │  [Tools: Docker squash, layer optimization]
│   │
│   └─ Push to Docker Hub (optional)
│      [Tools: Docker registry]
│
├─→ Local Deployment (docker-compose)
│   │
│   ├─ Spin up full stack (8 services)
│   │  [Tools: docker-compose up -d]
│   │
│   ├─ Services:
│   │  1. ml-ids-api (FastAPI) :5000
│   │  2. PostgreSQL :5432
│   │  3. InfluxDB :8086
│   │  4. Elasticsearch :9200
│   │  5. Kibana :5601
│   │  6. Prometheus :9090
│   │  7. Grafana :3000
│   │  8. Redis :6379
│   │  [Tools: docker-compose orchestration]
│   │
│   ├─ Network: ml-ids-network (bridge)
│   │  [Tools: Docker networking]
│   │
│   └─ Volumes for data persistence
│      [Tools: Docker named volumes]
│
├─→ Real-time Data Pipeline
│   │
│   ├─ Network packet capture (tcpdump or Zeek)
│   │  [Tools: tcpdump, pyshark]
│   │
│   ├─ Feature extraction stream
│   │  [Tools: Python stream processing]
│   │
│   ├─ Model inference pipeline
│   │  [Tools: FastAPI async endpoints]
│   │
│   └─ Alert generation & thresholding
│      [Tools: Custom alert logic]
│
├─→ Alert & Notification System
│   │
│   ├─ Store alerts in Elasticsearch
│   │  [Tools: Python Elasticsearch client]
│   │
│   ├─ Kibana dashboard for visualization
│   │  [Tools: Kibana UI, index patterns]
│   │
│   ├─ Slack integration for critical alerts
│   │  [Tools: Slack Webhook API]
│   │
│   ├─ Email alerts for escalation
│   │  [Tools: Python SMTP, email library]
│   │
│   └─ MITRE ATT&CK technique mapping
│      [Tools: MITRE ATT&CK framework]
│
├─→ Monitoring Dashboard
│   │
│   ├─ Prometheus metrics collection
│   │  [Tools: prometheus-client Python library]
│   │
│   ├─ Grafana dashboard setup
│   │  [Tools: Grafana web UI]
│   │
│   ├─ Track metrics:
│   │  - Model accuracy (%)
│   │  - API latency (ms)
│   │  - Alerts/hour
│   │  - False positive rate (%)
│   │  [Tools: Custom Prometheus metrics]
│   │
│   ├─ Model drift detection
│   │  [Tools: Custom drift detection logic]
│   │
│   └─ Auto-retraining trigger (accuracy < 95%)
│      [Tools: Apache Airflow or cron jobs]
│
└─→ Documentation & CI/CD
    │
    ├─ Architecture diagram
    │  [Tools: Draw.io, Lucidchart]
    │
    ├─ Deployment guide (50+ pages)
    │  [Tools: Sphinx, Markdown]
    │
    ├─ API documentation (Swagger)
    │  [Tools: FastAPI auto-docs]
    │
    ├─ GitHub Actions CI/CD workflow
    │  [Tools: GitHub Actions YAML]
    │
    └─ Automated testing & deployment
       [Tools: pytest, GitHub Actions]

        ↓ (Final Output: Production-ready system)

═══════════════════════════════════════════════════════════════════════════════
```

---

## PART 2: TOOL USAGE MATRIX BY PHASE & MODULE

### Complete Tool Allocation

| Phase | Module | Primary Tools | Supporting Tools | Output Format | Persistence |
|---|---|---|---|---|---|
| **Phase 1** | Data Loading | Python, Jupyter, wget | SQLAlchemy, psycopg2 | CSV, Parquet | PostgreSQL |
| **Phase 1** | Data Cleaning | Pandas, NumPy | Python scripts | Cleaned CSV | PostgreSQL |
| **Phase 1** | Feature Engineering | Scikit-learn, Pandas | Matplotlib | Feature ranking | CSV, pickle |
| **Phase 1** | Normalization/SMOTE | Scikit-learn, imbalanced-learn | NumPy | Normalized arrays | pickle files |
| **Phase 2** | RF Training | Scikit-learn | GridSearchCV, joblib | Model object | .pkl |
| **Phase 2** | XGBoost Training | XGBoost, Scikit-learn | Early stopping | Model object | .json, .pkl |
| **Phase 2** | SVM Training | Scikit-learn | GridSearchCV | Model object | .pkl |
| **Phase 2** | Baseline Comparison | Scikit-learn metrics | Matplotlib, Seaborn | Report PDF | Markdown |
| **Phase 3** | CNN Training | TensorFlow/Keras | CUDA, GPU | Model h5 | .h5, SavedModel |
| **Phase 3** | LSTM Training | TensorFlow/Keras | TensorBoard | Model h5 | .h5, SavedModel |
| **Phase 3** | CNN-LSTM Hybrid | TensorFlow/Keras | GPU optimization | Model h5 | .h5, SavedModel |
| **Phase 3** | Autoencoder | TensorFlow/Keras | Unsupervised learning | Model h5 | .h5, SavedModel |
| **Phase 3** | DNN | TensorFlow/Keras | Batch normalization | Model h5 | .h5, SavedModel |
| **Phase 4** | Voting Ensemble | Scikit-learn, NumPy | Model loading | Ensemble model | .pkl, .h5 |
| **Phase 4** | Hyperparameter Tuning | Optuna, GridSearchCV | MLflow tracking | Trial logs | MLflow server |
| **Phase 4** | Model Compression | TensorFlow Lite | ONNX export | Quantized model | .tflite, .onnx |
| **Phase 5** | Metrics Calculation | Scikit-learn metrics | NumPy | Report JSON | JSON file |
| **Phase 5** | False Positive Analysis | Pandas, Matplotlib | Scikit-learn | Analysis report | PDF |
| **Phase 5** | Cross-Dataset Validation | Python loops | Model transfer | Comparison table | CSV |
| **Phase 5** | Per-Attack Analysis | Scikit-learn | Custom scripts | Confusion matrix | PNG |
| **Phase 5** | Latency Testing | Python timeit | NVIDIA profiling | Benchmark report | PDF, CSV |
| **Phase 5** | Statistical Testing | SciPy, Statsmodels | Bootstrap | Statistical report | JSON, PDF |
| **Phase 6** | API Development | FastAPI, Pydantic | Gunicorn, Uvicorn | REST API | Service running |
| **Phase 6** | Docker Build | Docker | Multi-stage build | Container image | Docker registry |
| **Phase 6** | Docker Compose | docker-compose | YAML | Multi-container setup | Running containers |
| **Phase 6** | Kubernetes Deploy | kubectl, YAML | Helm (optional) | K8s manifests | Kubernetes cluster |
| **Phase 6** | Data Pipeline | Python scripts | Kafka/Redis | Stream processing | Running service |
| **Phase 6** | Alert System | Python, Elasticsearch | Slack API | Alert alerts | Elasticsearch index |
| **Phase 6** | Monitoring | Prometheus, Grafana | Custom metrics | Dashboards | Grafana server |
| **Phase 6** | CI/CD | GitHub Actions | Docker, kubectl | Automated workflows | GitHub workflows |

---

## PART 3: DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RAW NETWORK DATA                                   │
│  (NSL-KDD, UNSW-NB15, CIC-IDS-2017 Datasets)                               │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ↓
                    ╔════════════════════════╗
                    │  PHASE 1: DATA PREP   │
                    ║  Jupyter + Python     ║
                    ╚════════════════────════╝
                    ┌──────────┬──────────┐
                    ↓          ↓          ↓
            ┌──────────────┬──────────────┬──────────────┐
            │   Cleaning   │  Encoding    │ Normalization│
            │  (Pandas)    │  (Sklearn)   │   (Sklearn)  │
            └──────────────┴──────────────┴──────────────┘
                    │
                    ├─→ PostgreSQL (Features)
                    ├─→ InfluxDB (Metrics)
                    └─→ CSV files (Backup)
                    │
                    ↓
            ╔════════════════════════════════════════════╗
            │  PHASE 2: ML BASELINES (Week 3)           │
            │  ┌─────────────────────────────────────┐  │
            │  │ Random Forest  │ XGBoost  │  SVM   │  │
            │  │  (Sklearn)     │(XGBoost) │(Sklearn)  │
            │  └─────────────────────────────────────┘  │
            │  Output: 3 models (97-98% accuracy)       │
            ╚════════════════════════════════════════════╝
                    │
         ┌──────────┼──────────┐
         ↓          ↓          ↓
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │  RF.pkl │ │ XGB.pkl │ │ SVM.pkl │
    └─────────┘ └─────────┘ └─────────┘
         │          │          │
         │          ↓          │
         │    ╔════════════════╗
         │    │  GPU PHASE 3  ║
         │    ║  Deep Learning║
         │    ╚════════════════╝
         │    ┌─────┬─────┬───────┬──────────┬─────┐
         │    ↓     ↓     ↓       ↓          ↓     ↓
         │  ┌────┐┌────┐┌───────────┐┌──────────┐┌────┐
         │  │CNN ││LSTM││ CNN-LSTM  ││Autoenc. ││DNN │
         │  │    ││    ││(BEST)     ││(Unsup)  ││    │
         │  │TF  ││TF  ││TensorFlow ││TensorFlow││TF  │
         │  └────┘└────┘└───────────┘└──────────┘└────┘
         │    │     │       │           │        │
         │    └─────┴───┬───┴───────────┴────────┘
         │              │
         └──────────────┤
                        ↓
              ╔════════════════════╗
              │  PHASE 4: ENSEMBLE │
              │  ┌────────────────┐│
              │  │ Soft Voting    ││
              │  │ (NumPy+Sklearn)││
              │  └────────────────┘│
              │  ┌────────────────┐│
              │  │ Optimization   ││
              │  │ (Optuna)       ││
              │  └────────────────┘│
              └────────────────────┘
                        │
                        ↓
            ┌──────────────────────────────┐
            │  PHASE 5: EVALUATION         │
            │  ├─ Metrics (sklearn)        │
            │  ├─ Plotting (Matplotlib)    │
            │  ├─ Statistics (SciPy)       │
            │  ├─ Validation (pytest)      │
            │  └─ Cross-validation         │
            └──────────────────────────────┘
                        │
                        ↓
                  Ensemble Model
               (99.3-99.5% accuracy)
                        │
                        ↓
            ╔════════════════════════════════════╗
            │  PHASE 6: PRODUCTION DEPLOYMENT   │
            │  ┌──────────────────────────────┐ │
            │  │ Docker Container             │ │
            │  │ ┌────────────────────────┐   │ │
            │  │ │ FastAPI Application    │   │ │
            │  │ │ Port 5000              │   │ │
            │  │ └────────────────────────┘   │ │
            │  └──────────────────────────────┘ │
            └────────────────────────────────────┘
                        │
            ┌───────────┼──────────┬──────────────┐
            ↓           ↓          ↓              ↓
        ┌────────┐  ┌────────┐ ┌────────┐ ┌──────────┐
        │  Local │  │Kubernetes │Docker   │  Cloud   │
        │Docker- │  │  Cluster  │ Swarm   │ (AWS/GCP)│
        │compose │  │(K8s)      │         │          │
        └────────┘  └────────┘ └────────┘ └──────────┘
            │           │          │          │
            ├───────────┼──────────┼──────────┘
            ↓           ↓          ↓
        ┌─────────────────────────────────┐
        │  Service Mesh & Load Balancing  │
        │  (Ingress, Service, HPA)        │
        └──────────┬──────────────────────┘
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
    ┌────────┐ ┌────────┐ ┌────────┐
    │PostgreSQL│InfluxDB │Elasticsearch
    │(Features)│(Metrics)│(Logs)
    └────────┘ └────────┘ └────────┘
        │          │          │
        └──────────┼──────────┘
                   │
                   ↓
        ╔════════════════════════════╗
        │ MONITORING & ALERTING      │
        │ ┌────────────────────────┐ │
        │ │ Prometheus (Metrics)   │ │
        │ │ Grafana (Dashboard)    │ │
        │ │ Kibana (Logs)          │ │
        │ │ Slack/Email Alerts     │ │
        │ └────────────────────────┘ │
        ╚════════════════════════════╝
                   │
                   ↓
        ╔════════════════════════════╗
        │  REAL-TIME PREDICTIONS     │
        │  & ALERT GENERATION        │
        ╚════════════════════════════╝
```

---

## PART 4: DEPENDENCY GRAPH

```
                           FINAL OUTPUT
                        (Production IDS)
                              │
                ┌─────────────┼──────────────┐
                ↑             ↑              ↑
        ┌──────────────┐ ┌──────────────┐ ┌──────────┐
        │   API Docs   │ │  Dashboard   │ │  Alerts  │
        │   (Swagger)  │ │  (Grafana)   │ │(Slack/   │
        │   FastAPI    │ │Prometheus    │ │Email)    │
        └──────┬───────┘ └──────┬───────┘ └────┬─────┘
               │                │              │
               └────────┬───────┴──────┬──────┘
                        │              │
                  ┌─────┴──────────────┴─────┐
                  │   KUBERNETES CLUSTER     │
                  │   (3-10 replicas)        │
                  └──────────┬───────────────┘
                             │
              ┌──────────────┼──────────────┐
              ↑              ↑              ↑
         ┌─────────┐   ┌──────────┐   ┌──────────┐
         │ Ensemble│   │Database  │   │ Logging  │
         │ Model   │   │(Postgres)│   │(Elastic) │
         │(.h5)    │   │TimescaleDB   │Kibana    │
         └────┬────┘   └──────────┘   └──────────┘
              │
              ├─ depends on ─┐
              │              │
         ┌────┴────┐    ┌────┴────┐
         ↓         ↓    ↓         ↓
    ┌────────┐ ┌──────────────┬──────────┐
    │Baseline│ │ Deep Learning│Optimization
    │Models  │ │   Models     │(Optuna)
    │(RF,XGB,│ │(CNN,LSTM,DNN)│
    │SVM)    │ │(TensorFlow)  │
    └────┬───┘ └──────┬───────┴────┬────┘
         │            │            │
         └────────┬───┴────┬───────┘
                  │        │
              ┌───┴────────┴──────┐
              ↓                   ↓
        ┌─────────────┐   ┌──────────────┐
        │Preprocessed│   │Feature       │
        │ Datasets   │   │Engineering   │
        │(Sklearn)   │   │(Scikit-learn)│
        └─────┬───────┘   └───────┬──────┘
              │                   │
              └─────────┬─────────┘
                        │
                  ┌─────┴──────┐
                  ↓            ↓
             ┌─────────┐  ┌──────────┐
             │Raw Data │  │Cleaning  │
             │(NSL-KDD,│  │(Pandas)  │
             │UNSW-NB15│  │Removing  │
             │CIC)     │  │duplicates│
             └─────────┘  └──────────┘
```

---

## PART 5: MODULE INTERACTION MATRIX

| Module | Receives From | Sends To | Tools Used | Format |
|---|---|---|---|---|
| Data Loader | Download URLs | Raw data | wget, Kaggle CLI | Binary (compressed) |
| Data Cleaner | Raw data | Cleaned data | Pandas | Parquet, CSV |
| Feature Engineer | Cleaned data | Feature importance | Scikit-learn | Pickle, JSON |
| Normalizer | Features | Normalized features | Scikit-learn | NumPy arrays |
| SMOTE | Normalized data | Balanced data | imbalanced-learn | NumPy arrays |
| Train/Test Split | Balanced data | Train/Val/Test | sklearn | Train: 70%, Val: 15%, Test: 15% |
| RF Trainer | Train data | Model | scikit-learn | .pkl |
| XGB Trainer | Train data | Model | XGBoost | .json, .pkl |
| SVM Trainer | Train data | Model | scikit-learn | .pkl |
| Baseline Comparator | 3 models | Comparison report | sklearn.metrics | PDF, Markdown |
| CNN Trainer | Train data + GPU | Model + logs | TensorFlow | .h5, TensorBoard logs |
| LSTM Trainer | Train data + GPU | Model + logs | TensorFlow | .h5, TensorBoard logs |
| CNN-LSTM Trainer | Train data + GPU | Model + logs | TensorFlow | .h5, TensorBoard logs |
| Autoencoder | Train data + GPU | Model | TensorFlow | .h5 |
| DNN Trainer | Train data + GPU | Model + logs | TensorFlow | .h5 |
| Ensemble | 8 models + weights | Ensemble model | NumPy, joblib | .pkl, .h5 |
| Hyperparameter Tuner | Models + hyperparams | Optimized params | Optuna | MLflow server |
| Compressor | Ensemble model | Compressed model | TensorFlow Lite | .tflite, .onnx |
| Evaluator | Models + test data | Metrics | sklearn.metrics | JSON, PDF |
| API Server | Ensemble model | Predictions | FastAPI | JSON |
| Docker Builder | Application code | Container image | Docker | .tar (image) |
| Kubernetes Deploy | Container image | Running pods | kubectl | YAML manifests |
| Monitoring | Metrics stream | Dashboard | Prometheus+Grafana | Time-series data |

---

## PART 6: TECHNOLOGY STACK BY LAYER

```
┌───────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                          │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │  Kibana Dashboard  │  Grafana Dashboard  │  Swagger UI   │  │
│ │  (Log Viz)         │  (Metrics Viz)      │  (API Docs)   │  │
│ └──────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                          ↑ │ ↓
┌───────────────────────────────────────────────────────────────┐
│                    API LAYER                                   │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │  FastAPI Server  │ Gunicorn WSGI  │  Uvicorn ASGI       │  │
│ │  :5000           │ :9000          │  (Async)            │  │
│ └──────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                          ↑ │ ↓
┌───────────────────────────────────────────────────────────────┐
│                  ML INFERENCE LAYER                            │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ Ensemble Model                                            │  │
│ │ ├─ Random Forest (.pkl)                                  │  │
│ │ ├─ XGBoost (.pkl)                                        │  │
│ │ ├─ CNN-LSTM (TensorFlow .h5)                             │  │
│ │ ├─ DNN (TensorFlow .h5)                                  │  │
│ │ └─ Soft Voting Logic (NumPy)                             │  │
│ └──────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                          ↑ │ ↓
┌───────────────────────────────────────────────────────────────┐
│               FEATURE ENGINEERING LAYER                        │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ Data Normalization (MinMaxScaler)                        │  │
│ │ Feature Selection (Chi-square ranking)                   │  │
│ │ Categorical Encoding (OneHot, LabelEncoding)             │  │
│ │ SMOTE (Class Balancing)                                  │  │
│ └──────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                          ↑ │ ↓
┌───────────────────────────────────────────────────────────────┐
│                  DATA STORAGE LAYER                            │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ PostgreSQL/TimescaleDB  │  InfluxDB  │  Elasticsearch    │  │
│ │ (Features, Labels)      │  (Metrics) │  (Logs, Alerts)   │  │
│ │ :5432                   │  :8086     │  :9200            │  │
│ │ ACID, Time-series ext   │  Fast TS   │  Full-text search │  │
│ └──────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                          ↑ │ ↓
┌───────────────────────────────────────────────────────────────┐
│              DATA ACQUISITION LAYER                            │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ NSL-KDD | UNSW-NB15 | CIC-IDS-2017 | Live PCAP          │  │
│ │ Dataset 1 │ Dataset 2 │ Dataset 3 │ Network traffic     │  │
│ └──────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

---

## PART 7: ORCHESTRATION FLOW (Kubernetes)

```
┌─────────────────────────────────────────────────────────────────┐
│                  KUBERNETES CLUSTER (Production)                 │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              Ingress Controller (Load Balancer)        │    │
│  │  Port 80/443 → Distributes traffic to ml-ids-service  │    │
│  └──────────────────────┬─────────────────────────────────┘    │
│                         │                                        │
│  ┌──────────────────────┴────────────────────────────────┐     │
│  │       ml-ids-service (Internal Service)              │     │
│  │       ClusterIP: 10.0.0.1:80 → Port 5000             │     │
│  └──────────────────────┬────────────────────────────────┘     │
│                         │                                        │
│  ┌──────────────────────┴──────────────────────────────┐        │
│  │  ml-ids-deployment (Deployment Spec)               │        │
│  │  ├─ Replicas: 3-10 (HPA managed)                   │        │
│  │  ├─ Strategy: Rolling Update                       │        │
│  │  └─ Selector: app=ml-ids                           │        │
│  └──────────────────────┬──────────────────────────────┘        │
│                         │                                        │
│   ┌─────────────────────┼─────────────────┐                    │
│   ↓                     ↓                 ↓                    │
│ ┌─────────┐      ┌─────────┐      ┌─────────┐               │
│ │ Pod 1   │      │ Pod 2   │      │ Pod 3   │               │
│ │(ml-ids) │      │(ml-ids) │      │(ml-ids) │               │
│ │:5000    │      │:5000    │      │:5000    │               │
│ └────┬────┘      └────┬────┘      └────┬────┘               │
│      │                │                │                     │
│      ├─ Container: ml-ids-api                               │
│      │  ├─ Image: your-registry/ml-ids:latest              │
│      │  ├─ Resource requests:                              │
│      │  │  ├─ CPU: 1 core                                  │
│      │  │  └─ Memory: 2 GB                                 │
│      │  ├─ Resource limits:                                │
│      │  │  ├─ CPU: 2 cores                                 │
│      │  │  └─ Memory: 4 GB                                 │
│      │  ├─ Liveness Probe:                                 │
│      │  │  └─ GET /health (every 10s)                      │
│      │  ├─ Readiness Probe:                                │
│      │  │  └─ GET /ready (every 5s)                        │
│      │  └─ Volume mounts:                                  │
│      │     ├─ /app/models (models-volume)                  │
│      │     └─ /app/config (config-volume)                  │
│      │                                                      │
│      └─ Connected to services:                             │
│         ├─ postgres-service:5432                           │
│         ├─ influxdb-service:8086                           │
│         ├─ elasticsearch-service:9200                      │
│         └─ redis-service:6379                              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ HorizontalPodAutoscaler (HPA)                        │   │
│  │ ├─ Min replicas: 3                                   │   │
│  │ ├─ Max replicas: 10                                  │   │
│  │ ├─ Target CPU: 70% utilization                       │   │
│  │ ├─ Target Memory: 80% utilization                    │   │
│  │ └─ Scale up/down based on metrics                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ConfigMap & Secrets                                  │   │
│  │ ├─ MODEL_PATH: /app/models/ensemble_model.h5        │   │
│  │ ├─ DB_HOST: postgres-service                        │   │
│  │ └─ API_KEY: (from Kubernetes Secret)                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ PersistentVolumes & PersistentVolumeClaims           │   │
│  │ ├─ models-pvc: 10 GB (Model storage)                │   │
│  │ ├─ postgres-pvc: 50 GB (Database)                   │   │
│  │ ├─ influxdb-pvc: 100 GB (Metrics)                   │   │
│  │ └─ elasticsearch-pvc: 200 GB (Logs)                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## REFERENCES

[1] Kubernetes Official Documentation. (2024). https://kubernetes.io/docs/

[2] Docker Official Documentation. (2025). https://docs.docker.com/

[3] TensorFlow Architecture. (2024). https://www.tensorflow.org/guide/intro_to_graphs

[4] FastAPI Advanced Features. (2024). https://fastapi.tiangolo.com/advanced/

[5] ELK Stack Documentation. (2024). https://www.elastic.co/guide/

[6] Prometheus Architecture. (2024). https://prometheus.io/docs/introduction/overview/

[7] Grafana Dashboard Design. (2024). https://grafana.com/grafana/

[8] UML Diagram Notation. (2024). UML 2.5 Specification

[9] Machine Learning Pipeline Architecture. (2024). MLOps.community

[10] Production ML Systems Design Patterns. (2024). Google Cloud Architecture Center

---

**Document Version:** 1.0  
**Last Updated:** December 15, 2025  
**Diagrams:** 7 comprehensive UML/architecture diagrams  
**Tool Coverage:** 100+ tools with interaction mapping
