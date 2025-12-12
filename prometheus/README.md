# Prometheus Monitoring Demo - Complete Implementation

A comprehensive demonstration of Prometheus monitoring patterns including pull models, push models, multi-cluster federation, and custom exporters.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Demo Script](#demo-script)
- [Use Cases Covered](#use-cases-covered)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This project demonstrates a production-ready Prometheus monitoring setup including:

- ✅ **Infrastructure Monitoring** - Kubernetes cluster metrics
- ✅ **Application Monitoring (Pull)** - NATS messaging system
- ✅ **Custom Exporter (Pull)** - Real-time USDT/VND exchange rate
- ✅ **Multi-Cluster Federation (Remote Write)** - Centralized metrics aggregation
- ✅ **Batch Job Monitoring (Push)** - Airflow DAG metrics via Pushgateway
- ✅ **Visualization** - Grafana dashboards
- ✅ **Alerting** - Production-ready alert rules

---

## 🏗️ Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    Namespace: airflow-3                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Prometheus Server                            │  │
│  │  - Scrapes ServiceMonitors/PodMonitors                    │  │
│  │  - Receives Remote Write from agents                      │  │
│  │  - Stores metrics (10 days retention)                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Grafana                                      │  │
│  │  - Multi-cluster dashboards                               │  │
│  │  - Alerting visualization                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Pushgateway                                  │  │
│  │  - Receives metrics from Airflow DAGs                     │  │
│  │  - Scraped by Prometheus                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Scrapes
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│  Namespace: nats  │  │ Namespace:       │  │  Airflow DAGs   │
│                   │  │ another-cluster  │  │                 │
│  ┌─────────────┐  │  │                  │  │  ┌───────────┐  │
│  │ NATS        │  │  │  ┌─────────────┐ │  │  │ DAG runs  │  │
│  │ - Exporter  │  │  │  │ NATS        │ │  │  │ Push to   │  │
│  │ - Port 7777 │  │  │  │ - Exporter  │ │  │  │ Pushgateway│ │
│  └─────────────┘  │  │  └─────────────┘ │  │  └───────────┘  │
│  ┌─────────────┐  │  │         │        │  │                 │
│  │ PodMonitor  │  │  │  ┌─────────────┐ │  │                 │
│  │ cluster:    │  │  │  │ Prom Agent  │ │  │                 │
│  │ nats-primary│  │  │  │ Remote Write│ │  │                 │
│  └─────────────┘  │  │  │ cluster:    │ │  │                 │
│                   │  │  │ another-    │ │  │                 │
│  ┌─────────────┐  │  │  │ cluster     │ │  │                 │
│  │ USDT        │  │  │  └─────────────┘ │  │                 │
│  │ Exporter    │  │  │         │        │  │                 │
│  │ - Port 5000 │  │  │         └────────┼──┼─Remote Write────┤
│  └─────────────┘  │  │                  │  │                 │
│  ┌─────────────┐  │  │                  │  │                 │
│  │ServiceMonitor│ │  │                  │  │                 │
│  └─────────────┘  │  │                  │  │                 │
└───────────────────┘  └──────────────────┘  └─────────────────┘
```

### Data Flow

1. **Pull Model (NATS, USDT)**: Prometheus scrapes `/metrics` endpoints
2. **Push Model (Airflow)**: Jobs push to Pushgateway → Prometheus scrapes Pushgateway
3. **Remote Write (Federation)**: Prometheus Agent scrapes locally → forwards to central Prometheus
4. **Visualization**: Grafana queries central Prometheus

---

## 🧩 Components

### 1. Prometheus Stack (airflow-3 namespace)
- **Prometheus Server**: Metrics storage and querying
- **Grafana**: Visualization and dashboards
- **AlertManager**: Alert routing and notification
- **Node Exporters**: Host-level metrics
- **kube-state-metrics**: Kubernetes object metrics

### 2. NATS Monitoring (nats namespace)
- **NATS Server**: Messaging system with JetStream
- **Prometheus Exporter**: Exposes NATS metrics on port 7777
- **PodMonitor**: Auto-discovery configuration
- **Labels**: `cluster=nats-primary`, `environment=production`

### 3. USDT Exchange Rate Exporter (nats namespace)
- **Flask Application**: Fetches USDT/VND rate from Binance P2P API
- **Metrics Exposed**:
  - `usdt_vnd_rate`: Current exchange rate
  - `usdt_vnd_last_update`: Last update timestamp
  - `usdt_vnd_fetch_errors_total`: Error counter
- **Update Frequency**: Every 10 minutes

### 4. Multi-Cluster Federation (another-cluster namespace)
- **NATS Server**: Second NATS instance
- **Prometheus Agent**: Lightweight scraper
- **Remote Write**: Forwards metrics to central Prometheus
- **Labels**: `cluster=another-cluster`, `environment=demo`

### 5. Pushgateway & Airflow (airflow-3 namespace)
- **Pushgateway**: Receives metrics from batch jobs
- **Airflow DAG**: Simulates ETL pipeline with metrics
- **Metrics**:
  - Task duration
  - Records processed
  - Success/failure indicators
  - ETL data flow (extract → transform → load)

---

## 📦 Prerequisites

- Kubernetes cluster (AKS, GKE, EKS, or local)
- `kubectl` configured and connected
- `helm` v3+ installed
- Azure Container Registry access (for USDT exporter)
- Airflow installed (optional, for Pushgateway demo)

### Tools
```bash
# Check prerequisites
kubectl version --client
helm version
az --version  # If using Azure
```

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <your-repo>
cd prometheus-monitoring-demo
```

### 2. Install Prometheus Stack
```bash
# Install kube-prometheus-stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install kube-prometheus-stack \
  oci://ghcr.io/prometheus-community/charts/kube-prometheus-stack \
  --namespace airflow-3 \
  --create-namespace \
  --set prometheus.prometheusSpec.enableRemoteWriteReceiver=true
```

### 3. Deploy NATS
```bash
# Add NATS repo
helm repo add nats https://nats-io.github.io/k8s/helm/charts/

# Create namespace
kubectl create namespace nats

# Install NATS
helm install nats nats/nats \
  --namespace nats \
  -f manifests/nats/nats-values.yaml

# Create PodMonitor
kubectl apply -f manifests/nats/nats-podmonitor.yaml
```

### 4. Deploy USDT Exporter
```bash
# Create ACR secret
kubectl create secret docker-registry acr-credentials \
  --docker-server=astratestnet-gfawadgsd9b3d3fe.azurecr.io \
  --docker-username=astratestnet \
  --docker-password='<your-password>' \
  --namespace=nats

# Deploy exporter
kubectl apply -f manifests/usdt-exporter/deployment.yaml
```

### 5. Setup Multi-Cluster Federation
```bash
# Create namespace
kubectl create namespace another-cluster

# Install NATS
helm install nats nats/nats \
  --namespace another-cluster \
  -f manifests/federation/nats-another-cluster-values.yaml

# Deploy Prometheus Agent
kubectl apply -f manifests/federation/prometheus-agent.yaml
kubectl apply -f manifests/federation/nats-metrics-service.yaml
```

### 6. Install Pushgateway
```bash
helm install pushgateway prometheus-community/prometheus-pushgateway \
  --namespace airflow-3 \
  --set serviceMonitor.enabled=true \
  --set serviceMonitor.namespace=airflow-3 \
  --set serviceMonitor.additionalLabels.release=kube-prometheus-stack
```

### 7. Deploy Airflow DAG
```bash
# Copy DAG to Airflow
SCHEDULER_POD=$(kubectl get pods -n airflow-3 -l component=scheduler -o jsonpath='{.items[0].metadata.name}')
kubectl cp manifests/airflow/prometheus_metrics_dag.py airflow-3/${SCHEDULER_POD}:/opt/airflow/dags/

# Restart scheduler
kubectl delete pod -n airflow-3 ${SCHEDULER_POD}
```

### 8. Access UIs
```bash
# Prometheus
kubectl port-forward -n airflow-3 prometheus-kube-prometheus-stack-prometheus-0 9090:9090
# Open: http://localhost:9090

# Grafana
kubectl port-forward -n airflow-3 svc/kube-prometheus-stack-grafana 3000:80
# Open: http://localhost:3000
# Username: admin
# Password: kubectl get secret -n airflow-3 kube-prometheus-stack-grafana -o jsonpath="{.data.admin-password}" | base64 -d

# Pushgateway
kubectl port-forward -n airflow-3 svc/pushgateway-prometheus-pushgateway 9091:9091
# Open: http://localhost:9091
```

---

## 🎬 Demo Script

See [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for detailed presentation flow.

### Quick Demo (30 minutes)

1. **[5 min] Infrastructure Overview**
   - Show Prometheus targets
   - Show Grafana cluster dashboard

2. **[10 min] Pull Model - NATS & USDT**
   - Generate NATS traffic
   - Show real-time USDT rates
   - Query metrics in Prometheus
   - Visualize in Grafana

3. **[10 min] Multi-Cluster Federation**
   - Show metrics from both clusters
   - Query with cluster labels
   - Compare metrics side-by-side

4. **[5 min] Push Model - Airflow**
   - Trigger Airflow DAG
   - Show metrics in Pushgateway
   - Query batch job metrics

---

## 📊 Use Cases Covered

### 1. Pull Model (Long-Running Services)
**Use Case**: Monitor NATS messaging system
```promql
# Current connections
nats_varz_connections{cluster="nats-primary"}

# Message rate
rate(nats_varz_in_msgs[5m])
```

**When to use**:
- Services run 24/7
- Prometheus can reach the service
- Standard microservices monitoring

### 2. Custom Exporter (Business Metrics)
**Use Case**: Monitor USDT/VND exchange rate
```promql
# Current rate
usdt_vnd_rate

# Rate of change
deriv(usdt_vnd_rate[1h])
```

**When to use**:
- Custom business metrics
- External API monitoring
- SaaS metrics collection

### 3. Multi-Cluster Federation (Remote Write)
**Use Case**: Centralize metrics from multiple clusters
```promql
# All clusters
sum(nats_varz_connections) by (cluster)

# Specific cluster
nats_varz_connections{cluster="another-cluster"}
```

**When to use**:
- Multiple Kubernetes clusters
- Edge/IoT deployments
- Hierarchical monitoring

### 4. Push Model (Batch Jobs)
**Use Case**: Monitor Airflow ETL pipelines
```promql
# DAG duration
airflow_data_processing_duration_seconds

# Success rate
avg_over_time(airflow_data_processing_success[1h])
```

**When to use**:
- Batch jobs / cron jobs
- Serverless functions
- CI/CD pipelines
- Jobs that exit after completion

---

## 🔍 Key Metrics

### NATS Metrics
```promql
nats_varz_connections           # Active connections
nats_varz_in_msgs               # Inbound messages
nats_varz_out_msgs              # Outbound messages
nats_jetstream_varz_stats_total_streams  # JetStream streams
```

### USDT Exporter Metrics
```promql
usdt_vnd_rate                   # Current exchange rate
usdt_vnd_last_update            # Last update timestamp
usdt_vnd_fetch_errors_total     # Error counter
```

### Airflow Metrics
```promql
airflow_data_processing_duration_seconds    # Task duration
airflow_data_processing_records_total       # Records processed
airflow_etl_extract_records                 # ETL extract count
airflow_etl_load_records                    # ETL load count
```

---

## 🐛 Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md) for detailed solutions.

### Quick Fixes

**Target is DOWN**:
```bash
# Check pod is running
kubectl get pods -n <namespace>

# Check ServiceMonitor/PodMonitor exists
kubectl get servicemonitor,podmonitor -n <namespace>

# Check labels match
kubectl get servicemonitor <name> -n <namespace> -o yaml | grep "release:"
```

**No metrics in Prometheus**:
```bash
# Wait 30-60 seconds for scrape
# Check Prometheus logs
kubectl logs -n airflow-3 prometheus-kube-prometheus-stack-prometheus-0 -c prometheus

# Manually query target
kubectl port-forward -n <namespace> <pod> <port>:<port>
curl localhost:<port>/metrics
```

**Remote Write failing**:
```bash
# Check Prometheus Agent logs
kubectl logs -n another-cluster -l app=prometheus-agent

# Verify remote write receiver is enabled
kubectl get prometheus -n airflow-3 -o jsonpath='{.spec.enableRemoteWriteReceiver}'
```

---

## 📈 Grafana Dashboards

Import pre-built dashboards from `grafana-dashboards/`:

1. **NATS Dashboard** (`nats-dashboard.json`)
   - Connections, message rates, JetStream stats

2. **Multi-Cluster Dashboard** (`multi-cluster-dashboard.json`)
   - Side-by-side comparison of all clusters
   - Aggregated metrics

3. **Airflow Metrics Dashboard** (`airflow-metrics-dashboard.json`)
   - DAG duration, success rates, ETL flow

### Import Instructions
1. Open Grafana UI
2. Click **Dashboards** → **Import**
3. Upload JSON file or paste JSON content
4. Select Prometheus data source
5. Click **Import**

---

## 🎯 Production Checklist

Before deploying to production:

- [ ] Configure persistent storage for Prometheus
- [ ] Set appropriate retention policies
- [ ] Enable authentication for Grafana
- [ ] Configure AlertManager with notification channels
- [ ] Set up recording rules for expensive queries
- [ ] Enable RBAC and network policies
- [ ] Configure backup strategy
- [ ] Set resource limits and requests
- [ ] Enable TLS for all endpoints
- [ ] Document runbooks for alerts

---

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [NATS Documentation](https://docs.nats.io/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Best Practices](https://prometheus.io/docs/practices/)

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 👥 Authors

- **Your Name** - Initial work

---

## 🙏 Acknowledgments

- Prometheus Community
- NATS.io Team
- Grafana Labs
- Kubernetes SIG Observability

---

**Last Updated**: December 12, 2025  
**Version**: 1.0.0