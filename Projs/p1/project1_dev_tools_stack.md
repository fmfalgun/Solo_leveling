# Project 1: ML-Based IDS - Complete Developer Resources & Tools Stack
## From Development to Production Deployment

---

## PART 1: DEVELOPMENT ENVIRONMENT SETUP

### 1.1 Programming Languages & Frameworks

| Language | Purpose | Version | Installation | Package Manager | Use Case |
|---|---|---|---|---|---|
| **Python** | Primary language | 3.10+ | `python3.10` or conda | pip / conda | All ML/DL development |
| **Go** | High-performance backend (optional) | 1.21+ | golang.org | go get | Streaming pipeline, API optimization |
| **Bash/Shell** | Scripting, automation | 4.0+ | Built-in | N/A | Deployment scripts, CI/CD |
| **YAML** | Configuration files | - | Text editor | N/A | Config, Kubernetes manifests |
| **SQL** | Database queries | - | Database native | N/A | Data analytics, reporting |

### 1.2 ML/DL Frameworks & Libraries

| Framework | Version | Installation | GPU Support | Use Case | Alternative |
|---|---|---|---|---|---|
| **TensorFlow** | 2.13+ | `pip install tensorflow[and-cuda]` | CUDA 11.8+ | CNN, LSTM, DNN models | PyTorch |
| **Keras** | 3.0+ (integrated TF) | Included with TF | Built-in GPU | High-level model API | torch.nn |
| **PyTorch** | 2.0+ | `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118` | CUDA 11.8+ | Research, custom architectures | TensorFlow |
| **Scikit-learn** | 1.3.0+ | `pip install scikit-learn` | CPU-only | RF, XGB, SVM, preprocessing | sklearn alternatives |
| **XGBoost** | 2.0+ | `pip install xgboost` | CPU/GPU | Gradient boosting | LightGBM |
| **NumPy** | 1.24+ | `pip install numpy` | NumPy CUDA (optional) | Numerical computations | N/A |
| **Pandas** | 2.0+ | `pip install pandas` | CPU-only | Data manipulation, EDA | Polars, DuckDB |
| **Scikit-image** | 0.21+ | `pip install scikit-image` | CPU-only | Image processing | OpenCV |

### 1.3 Development Tools & IDEs

| Tool | Purpose | Installation | Free | Use Case | Alternative |
|---|---|---|---|---|---|
| **Jupyter Notebook** | Interactive development | `pip install jupyter` | ✓ | EDA, prototyping, notebooks | JupyterLab, Colab |
| **JupyterLab** | Advanced notebook environment | `pip install jupyterlab` | ✓ | Debugging, multiple notebooks | VS Code + Jupyter |
| **VS Code** | Code editor | Download from code.visualstudio.com | ✓ | Full development, debugging | PyCharm, Sublime |
| **PyCharm Professional** | IDE | Download from jetbrains.com | ✗ (Community free) | Professional development | VS Code + Extensions |
| **Google Colab** | Cloud notebook | Access via colab.research.google.com | ✓ (GPU limited) | Quick prototyping, free GPU | Kaggle Notebooks |
| **Git** | Version control | `git --version` or apt install git | ✓ | Code management, GitHub | Mercurial |
| **GitHub Desktop** | Git GUI | Download from desktop.github.com | ✓ | User-friendly Git management | GitKraken |

### 1.4 Data Processing & Visualization Libraries

| Library | Version | Installation | Purpose | Alternative |
|---|---|---|---|---|
| **Matplotlib** | 3.7+ | `pip install matplotlib` | Static plots, visualizations | Plotly |
| **Seaborn** | 0.12+ | `pip install seaborn` | Statistical data visualization | Plotly, Altair |
| **Plotly** | 5.14+ | `pip install plotly` | Interactive visualizations | Bokeh |
| **Pandas Profiling** | 4.0+ | `pip install ydata-profiling` | Automated EDA reports | Sweetviz |
| **OpenCV** | 4.8+ | `pip install opencv-python` | Image/video processing, PCAP analysis | scikit-image |
| **Imbalanced-learn** | 0.11+ | `pip install imbalanced-learn` | SMOTE, class balancing | imblearn alternatives |

### 1.5 Data Science & Utilities

| Library | Version | Installation | Purpose | Alternative |
|---|---|---|---|---|
| **SciPy** | 1.11+ | `pip install scipy` | Scientific computing, statistics | NumPy |
| **StatsModels** | 0.14+ | `pip install statsmodels` | Statistical modeling, hypothesis testing | SciPy.stats |
| **Joblib** | 1.3+ | `pip install joblib` | Parallel computing, model persistence | Pickle, dask |
| **Dask** | 2023.9+ | `pip install dask[complete]` | Distributed computing, parallel processing | Spark, Ray |
| **MLflow** | 2.6+ | `pip install mlflow` | Experiment tracking, model registry | Weights & Biases |
| **Optuna** | 3.14+ | `pip install optuna` | Hyperparameter optimization | Hyperopt, Ray Tune |

---

## PART 2: DATABASE & DATA STORAGE

### 2.1 Time-Series Databases (For Network Traffic Data)

| Database | Type | Installation | Best For | Pros | Cons |
|---|---|---|---|---|---|
| **InfluxDB** | Time-series TSDB | Docker: `docker run -p 8086:8086 influxdb:latest` | Network metrics, real-time data | High throughput, tagging system | Learning curve, limited SQL |
| **TimescaleDB** | PostgreSQL extension | `docker run -p 5432:5432 -e POSTGRES_PASSWORD=password timescale/timescaledb:latest-pg15` | Time-series + relational | Native PostgreSQL, SQL queries | Requires PostgreSQL knowledge |
| **Prometheus** | Metrics database | Docker: `docker run -p 9090:9090 prom/prometheus` | System metrics, monitoring | Pull-based, built-in alerting | Not for high-volume events |
| **Elasticsearch** | Search & analytics | `docker run -p 9200:9200 -e discovery.type=single-node docker.elastic.co/elasticsearch/elasticsearch:8.10.0` | Log storage, alert indexing | Full-text search, aggregations | High memory usage |
| **MongoDB** | NoSQL document DB | `docker run -p 27017:27017 mongo` | JSON-like traffic data | Flexible schema, scalability | High memory, slower queries |
| **PostgreSQL** | Relational RDBMS | `docker run -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15` | Raw flow records, metadata | ACID compliance, SQL, TimescaleDB extension | Slower than time-series DBs |

### 2.2 Recommended Data Pipeline

```
Network Traffic Data Flow:
┌──────────────┐
│ Network PCAP │
│   (Raw Data) │
└──────┬───────┘
       │
       ↓
┌──────────────────────────┐
│ Feature Extraction       │
│ (Python scripts)         │
└──────┬───────────────────┘
       │
       ↓
┌────────────────────────────────────┐
│ Time-Series DB (InfluxDB/Prometheus)
│ Raw Features (1-minute buckets)     │
└──────┬─────────────────────────────┘
       │
       ↓
┌──────────────────────────────────┐
│ Feature Aggregation              │
│ (Time windows: 5min, 15min, 1hr) │
└──────┬─────────────────────────────┘
       │
       ↓
┌──────────────────────────────────┐
│ ML Model Inference               │
│ (Flask/FastAPI API)              │
└──────┬─────────────────────────────┘
       │
       ↓
┌──────────────────────────────────┐
│ Alerts & Results                 │
│ (Elasticsearch + Kibana)         │
└──────────────────────────────────┘
```

---

## PART 3: CONTAINERIZATION & ORCHESTRATION

### 3.1 Container & VM Technologies

| Technology | Type | Purpose | Installation | Learning Curve | Use Case |
|---|---|---|---|---|---|
| **Docker** | Container Runtime | Package entire IDS stack | `curl https://get.docker.com \| sh` | Low | Development, testing, production |
| **Docker Compose** | Container Orchestration (local) | Multi-container local setup | Built-in with Docker Desktop | Low | Local development (3-5 containers) |
| **Kubernetes (K8s)** | Container Orchestration | Production deployment, auto-scaling | `minikube start` (local) or cloud K8s | High | Production clusters (10+ replicas) |
| **Kind (K8s in Docker)** | Local K8s Testing | Test Kubernetes locally | `kind create cluster` | Low | Learning, CI/CD testing |
| **VirtualBox** | Hypervisor/VM | Local virtual machines | Download from virtualbox.org | Low | Testing on multiple OS |
| **QEMU** | Hypervisor | Network interface emulation | `apt install qemu` | Medium | Complex networking scenarios |

### 3.2 Docker Configuration for IDS

**Dockerfile (Multi-stage build):**
```dockerfile
# Stage 1: Builder
FROM python:3.10-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src/ .
COPY models/ ./models/
ENV PATH=/root/.local/bin:$PATH
EXPOSE 5000
CMD ["python", "app.py"]
```

**Docker Compose (Local Development):**
```yaml
version: '3.9'
services:
  ml-ids-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - MODEL_PATH=/app/models/ensemble_model.h5
      - DEBUG=True
    volumes:
      - ./src:/app/src
      - ./models:/app/models

  influxdb:
    image: influxdb:latest
    ports:
      - "8086:8086"
    environment:
      - INFLUXDB_DB=network_traffic
    volumes:
      - influxdb_data:/var/lib/influxdb2

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    ports:
      - "9200:9200"
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false

  kibana:
    image: docker.elastic.co/kibana/kibana:8.10.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

volumes:
  influxdb_data:
```

### 3.3 Kubernetes Deployment

**Kubernetes Deployment YAML:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-ids-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-ids
  template:
    metadata:
      labels:
        app: ml-ids
    spec:
      containers:
      - name: ml-ids
        image: your-registry/ml-ids:latest
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 20
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ml-ids-service
spec:
  selector:
    app: ml-ids
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-ids-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-ids-deployment
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## PART 4: SECURITY & MONITORING TOOLS

### 4.1 Network Security & Analysis Tools

| Tool | Category | Installation | Purpose | Use Case |
|---|---|---|---|---|
| **Wireshark** | Packet Analyzer | `apt install wireshark` or GUI download | PCAP analysis, traffic inspection | Protocol analysis, debugging |
| **tcpdump** | Packet Capture | `apt install tcpdump` | Lightweight packet capture | Command-line traffic capture |
| **Zeek (formerly Bro)** | Network IDS | Docker: `docker pull zeek/zeek` | Advanced network analysis | Log analysis, event detection |
| **Suricata** | Network IDS/IPS | `apt install suricata` | Signature-based detection | Real-time threat detection |
| **Metasploit** | Penetration Testing | Download from metasploit.com | Attack simulation | Testing model robustness |
| **nmap** | Network Scanner | `apt install nmap` | Network reconnaissance | Port scanning, service enumeration |
| **netcat** | Network Utility | Built-in (nc) | Raw network communication | Testing API endpoints |
| **curl** | HTTP Client | `apt install curl` | API testing | REST endpoint validation |

### 4.2 Logging & Monitoring Stack (ELK - Elasticsearch, Logstash, Kibana)

| Component | Purpose | Version | Installation | Port |
|---|---|---|---|---|
| **Elasticsearch** | Search & analytics engine | 8.10+ | Docker or apt | 9200 |
| **Logstash** | Log processing pipeline | 8.10+ | Docker or apt | 5000 (input), 9600 (API) |
| **Kibana** | Visualization & dashboards | 8.10+ | Docker or apt | 5601 |
| **Beats** | Lightweight data shippers | 8.10+ | `apt install filebeat metricbeat packetbeat` | Various |

**ELK Docker Setup:**
```bash
# Elasticsearch
docker run -d --name elasticsearch \
  -e discovery.type=single-node \
  -e xpack.security.enabled=false \
  -p 9200:9200 \
  docker.elastic.co/elasticsearch/elasticsearch:8.10.0

# Kibana
docker run -d --name kibana \
  -p 5601:5601 \
  -e ELASTICSEARCH_HOSTS=http://elasticsearch:9200 \
  docker.elastic.co/kibana/kibana:8.10.0

# Logstash (with IDS alert config)
docker run -d --name logstash \
  -p 5000:5000 \
  -v $(pwd)/logstash.conf:/usr/share/logstash/pipeline/logstash.conf \
  docker.elastic.co/logstash/logstash:8.10.0
```

### 4.3 Splunk (Alternative to ELK)

| Aspect | Splunk | ELK |
|---|---|---|
| **Cost** | Commercial (expensive) | Open-source (free) |
| **Learning Curve** | High | Medium |
| **GUI Quality** | Excellent | Good |
| **Data Volume** | Limited (license-based) | Unlimited |
| **Search Language** | SPL (Splunk Query Language) | Kibana Query Language (KQL) + Lucene |
| **Setup Time** | 2-3 days | 4-6 hours |
| **Best For** | Enterprise deployments | Startups, research |

**Splunk Installation (Enterprise):**
```bash
# Download from splunk.com
tar xvzf splunk-*.tgz
cd splunk/bin
./splunk start --accept-license

# Access at http://localhost:8000
```

---

## PART 5: API FRAMEWORKS & SERVER TECHNOLOGIES

### 5.1 Web Frameworks for Model Serving

| Framework | Language | Installation | Speed | Learning Curve | Use Case |
|---|---|---|---|---|---|
| **FastAPI** | Python | `pip install fastapi uvicorn` | Very fast (3-5x Flask) | Low | Production API (recommended) |
| **Flask** | Python | `pip install flask` | Medium speed | Very low | Prototyping, simple APIs |
| **Django REST** | Python | `pip install django djangorestframework` | Medium speed | Medium | Large-scale applications |
| **Gunicorn** | Python | `pip install gunicorn` | Fast | Low | WSGI server (production) |
| **Uvicorn** | Python | `pip install uvicorn` | Very fast | Low | ASGI server (async) |
| **Starlette** | Python | `pip install starlette` | Very fast | Low | Light async framework |

**FastAPI Example:**
```python
from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from tensorflow import keras

app = FastAPI()
model = keras.models.load_model('ensemble_model.h5')

class PredictionRequest(BaseModel):
    features: list[float]

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/predict")
def predict(request: PredictionRequest):
    features = np.array([request.features])
    prediction = model.predict(features)
    return {
        "prediction": int(prediction[0] > 0.5),
        "confidence": float(prediction[0])
    }

@app.post("/predict_batch")
def predict_batch(requests: list[PredictionRequest]):
    features = np.array([req.features for req in requests])
    predictions = model.predict(features)
    return [{"prediction": int(p > 0.5), "confidence": float(p)} for p in predictions]
```

---

## PART 6: CI/CD & DEPLOYMENT PIPELINES

### 6.1 CI/CD Tools

| Tool | Purpose | Language | Installation | Use Case |
|---|---|---|---|---|
| **GitHub Actions** | CI/CD (integrated with GitHub) | YAML | Built-in to GitHub | Automated testing, deployment |
| **GitLab CI/CD** | CI/CD (integrated with GitLab) | YAML | Built-in to GitLab | Similar to GitHub Actions |
| **Jenkins** | CI/CD orchestration | Groovy/YAML | `docker run -p 8080:8080 jenkins/jenkins:lts` | Enterprise deployments |
| **CircleCI** | Cloud CI/CD | YAML | circleci.com | Quick setup, cloud-native |
| **Travis CI** | Cloud CI/CD | YAML | travis-ci.org | GitHub integration, simple |
| **Argo CD** | GitOps, Kubernetes CD | YAML | `kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml` | K8s deployments |

**GitHub Actions Workflow (.github/workflows/deploy.yml):**
```yaml
name: ML-IDS CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest tests/
      - run: python -m pytest --cov=src tests/

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - uses: docker/setup-buildx-action@v2
      - uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      - uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/ml-ids:latest

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: azure/setup-kubectl@v3
      - run: kubectl set image deployment/ml-ids-deployment ml-ids=${{ secrets.DOCKER_USERNAME }}/ml-ids:latest
```

---

## PART 7: PERFORMANCE & PROFILING TOOLS

### 7.1 Model Optimization & Profiling

| Tool | Purpose | Installation | Use Case |
|---|---|---|---|---|
| **TensorFlow Profiler** | Model performance analysis | Built-in TF | CPU/GPU bottleneck identification |
| **PyTorch Profiler** | PyTorch performance analysis | Built-in PyTorch | Layer-wise timing |
| **Memory Profiler** | Memory usage analysis | `pip install memory-profiler` | Memory leak detection |
| **cProfile** | Python code profiling | Built-in Python | CPU profiling, hotspot analysis |
| **line_profiler** | Line-by-line profiling | `pip install line-profiler` | Detailed function profiling |
| **NVIDIA Nsys** | GPU profiling | NVIDIA toolkit | GPU utilization analysis |
| **NVIDIA Nsight** | GPU debugging | NVIDIA toolkit | GPU debugging, optimization |

---

## PART 8: HARDWARE REQUIREMENTS

### 8.1 Development Machine Specifications

| Component | Minimum | Recommended | High-End | Notes |
|---|---|---|---|---|
| **CPU** | i5-8400 (6-core) | i7-12700 (12-core) | Xeon W5-3435X (60-core) | 6+ cores for parallel training |
| **RAM** | 16 GB | 32-64 GB | 128+ GB | 32GB minimum for large datasets |
| **GPU** | None | RTX 3070 (8GB) | RTX 4090 (24GB) / A100 (40GB) | GPU 10-20x faster training |
| **Storage** | 512 GB SSD | 1-2 TB NVMe SSD | 4-8 TB NVMe SSD | Fast I/O for data pipeline |
| **Network** | Gigabit Ethernet | 10Gbps (optional) | 25Gbps (optional) | Network traffic capture |

### 8.2 Deployment Server Specifications

| Component | Minimum | Recommended | High-End | Notes |
|---|---|---|---|---|
| **CPU** | 4 cores | 16 cores | 32+ cores | Parallel inference requests |
| **RAM** | 8 GB | 32 GB | 64+ GB | Model in memory |
| **GPU** | Optional | RTX 3080 (10GB) | RTX 4090 (24GB) / H100 (80GB) | <2.5ms inference latency |
| **Storage** | 100 GB | 500 GB | 1+ TB | Model versioning, logs |
| **Network Bandwidth** | 100 Mbps | 1 Gbps | 10 Gbps | Network traffic capture |

---

## PART 9: COMPLETE DEPENDENCY STACK (requirements.txt)

```txt
# Core ML/DL Frameworks
tensorflow==2.13.0
torch==2.0.1
torchvision==0.15.2

# Data Processing
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
scipy==1.11.0
imbalanced-learn==0.10.1

# Visualization
matplotlib==3.7.2
seaborn==0.12.2
plotly==5.14.0
ydata-profiling==4.3.1

# Model Training & Optimization
xgboost==2.0.0
optuna==3.14.0
mlflow==2.6.0
joblib==1.3.0

# API & Web Frameworks
fastapi==0.103.0
uvicorn==0.23.2
flask==2.3.2
gunicorn==21.2.0
pydantic==2.2.0

# Database & Storage
sqlalchemy==2.0.20
psycopg2-binary==2.9.7
pymongo==4.4.1
redis==5.0.0
influxdb-client==1.18.0

# Logging & Monitoring
python-json-logger==2.0.7
prometheus-client==0.18.0
structlog==23.1.0

# Testing & Quality
pytest==7.4.0
pytest-cov==4.1.0
black==23.7.0
flake8==6.0.0
mypy==1.4.1

# Security & Utilities
cryptography==41.0.0
pyyaml==6.0.1
python-dotenv==1.0.0
requests==2.31.0
click==8.1.6

# Network/Packet Processing
scapy==2.4.5
pyshark==0.6

# Documentation
sphinx==7.1.2
sphinx-rtd-theme==1.3.0
```

---

## PART 10: INSTALLATION & SETUP GUIDE

### 10.1 Quick Setup Script (setup.sh)

```bash
#!/bin/bash

# Create Python virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# For GPU support (CUDA 11.8)
pip install tensorflow[and-cuda]==2.13.0

# Download datasets
mkdir -p data/raw
wget -O data/raw/nsl_kdd.zip "https://www.kaggle.com/api/v1/datasets/download/mrwellsdavid/nsl-kdd"
unzip data/raw/nsl_kdd.zip -d data/raw/

# Create project structure
mkdir -p src/{data_processing,models,evaluation,deployment}
mkdir -p tests config docker logs results

# Initialize git
git init
git add .
git commit -m "Initial commit: ML-based IDS project structure"

echo "✅ Setup complete! Run 'source venv/bin/activate' to activate environment"
```

### 10.2 Docker Compose Full Stack (docker-compose.yml)

```yaml
version: '3.9'

services:
  # ML Model API
  ml-ids-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - MODEL_PATH=/app/models/ensemble_model.h5
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/ids_db
    volumes:
      - ./src:/app/src
      - ./models:/app/models
      - ./logs:/app/logs
    depends_on:
      - postgres
      - influxdb
      - elasticsearch
    networks:
      - ml-ids-network

  # PostgreSQL Database
  postgres:
    image: timescale/timescaledb:latest-pg15
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=ids_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - ml-ids-network

  # Time-Series Database
  influxdb:
    image: influxdb:latest
    ports:
      - "8086:8086"
    environment:
      - INFLUXDB_DB=network_traffic
      - INFLUXDB_ADMIN_USER=admin
      - INFLUXDB_ADMIN_PASSWORD=password
    volumes:
      - influxdb_data:/var/lib/influxdb2
    networks:
      - ml-ids-network

  # Elasticsearch (Log Storage)
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    ports:
      - "9200:9200"
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - ml-ids-network

  # Kibana (Visualization)
  kibana:
    image: docker.elastic.co/kibana/kibana:8.10.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch
    networks:
      - ml-ids-network

  # Prometheus (Metrics)
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    networks:
      - ml-ids-network

  # Grafana (Dashboard)
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - ml-ids-network

  # Redis (Caching)
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - ml-ids-network

volumes:
  postgres_data:
  influxdb_data:
  elasticsearch_data:
  prometheus_data:
  grafana_data:
  redis_data:

networks:
  ml-ids-network:
    driver: bridge
```

---

## PART 11: COST ANALYSIS

### Development Setup (One-Time)

| Item | Cost | Notes |
|---|---|---|
| Development Machine (RTX 3070) | $1,500-2,000 | One-time investment |
| IDEs & Tools (VS Code, Git) | Free | Open-source |
| Datasets (NSL-KDD, UNSW-NB15) | Free | Public datasets |
| Cloud GPU Hours (if needed) | $50-500/month | Alternative if no local GPU |
| **Total Development** | **$1,500-2,500** | One-time or monthly cloud |

### Production Deployment (Monthly)

| Component | Cost | Scale | Notes |
|---|---|---|---|
| Kubernetes Cluster (AWS EKS) | $73/month | Control plane | Base cost for 3 nodes |
| Compute Nodes (3x t3.xlarge) | $200/month | 3 nodes | ~$300/month for GPU nodes |
| Storage (1TB) | $25/month | Data persistence | EBS + S3 backup |
| Load Balancer | $20/month | Ingress | Network load balancer |
| Monitoring (Prometheus/Grafana) | Free | Self-hosted | ELK alternative |
| **Total Cloud Deployment** | **$318-400+/month** | Production | AWS pricing (varies by region) |

### On-Premises Deployment

| Item | Cost | One-Time/Monthly | Notes |
|---|---|---|---|
| Server Hardware | $3,000-5,000 | One-time | 16-core CPU, 32GB RAM, RTX 3080 |
| Networking (10Gbps NIC) | $500-1,000 | One-time | Network interface card |
| Rack/Colocation | $300-500 | Monthly | Data center space |
| Power/Cooling | $100-200 | Monthly | Utilities |
| **Total On-Premises** | **$3,500-5,500 + $400-700/mo** | Hybrid | Lower long-term costs |

---

## REFERENCES

[1] TensorFlow Installation Guide. (2025). https://www.tensorflow.org/install/pip

[2] PyTorch Getting Started. (2024). https://pytorch.org/get-started/locally/

[3] Docker Official Documentation. (2025). https://docs.docker.com/

[4] Kubernetes Documentation. (2024). https://kubernetes.io/docs/

[5] FastAPI Documentation. (2024). https://fastapi.tiangolo.com/

[6] Elasticsearch Documentation. (2024). https://www.elastic.co/guide/

[7] BuildPiper. (2025). "Deploying ML Models with Kubernetes." Retrieved from buildpiper.io

[8] DataCamp. (2023). "Containerization: Docker and Kubernetes for ML." Retrieved from datacamp.com

[9] ELK Stack Network Monitoring. (2024). YouTube Ashnik presentation.

[10] ServerStadium. (2024). "Setting Up AI Development Environment with PyTorch and TensorFlow."

---

**Document Version:** 1.0  
**Last Updated:** December 15, 2025  
**Total Tools/Resources Listed:** 100+ tools across all categories  
**Setup Complexity:** Low-Medium (4-8 hours for full stack)
