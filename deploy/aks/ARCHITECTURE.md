# SSC Application - AKS Deployment Architecture

## Overview

This document describes the Azure Kubernetes Service (AKS) deployment architecture for the SSC Application.

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         Azure Cloud                                       │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                  Azure Kubernetes Service (AKS)                     │  │
│  │                                                                      │  │
│  │  ┌────────────────────────────────────────────────────────────┐    │  │
│  │  │              Namespace: ssc-app                             │    │  │
│  │  │                                                              │    │  │
│  │  │  ┌──────────────────────────────────────────────────────┐  │    │  │
│  │  │  │         Ingress Controller (nginx-ingress)            │  │    │  │
│  │  │  │  ┌─────────────────────────────────────────────┐     │  │    │  │
│  │  │  │  │  Load Balancer (Azure LB)                    │     │  │    │  │
│  │  │  │  │  External IP: x.x.x.x                        │     │  │    │  │
│  │  │  │  └─────────────────────────────────────────────┘     │  │    │  │
│  │  │  │           │                        │                   │  │    │  │
│  │  │  │      /api/*                       /*                   │  │    │  │
│  │  │  └──────────────────────────────────────────────────────┘  │    │  │
│  │  │           │                        │                         │    │  │
│  │  │           ▼                        ▼                         │    │  │
│  │  │  ┌───────────────────┐   ┌───────────────────┐             │    │  │
│  │  │  │   Backend API     │   │   Frontend UI     │             │    │  │
│  │  │  │   (FastAPI)       │   │   (React/Vite)    │             │    │  │
│  │  │  │                   │   │                   │             │    │  │
│  │  │  │  Pod Replicas: 2  │   │  Pod Replicas: 2  │             │    │  │
│  │  │  │  Port: 8000       │   │  Port: 3000       │             │    │  │
│  │  │  │  Image: ACR       │   │  Image: ACR       │             │    │  │
│  │  │  │                   │   │                   │             │    │  │
│  │  │  │  Resources:       │   │  Resources:       │             │    │  │
│  │  │  │  • CPU: 250m-1    │   │  • CPU: 100m-500m │             │    │  │
│  │  │  │  • Mem: 256Mi-1Gi │   │  • Mem: 128Mi-512Mi│             │    │  │
│  │  │  │                   │   │                   │             │    │  │
│  │  │  │  Autoscaling:     │   │  Autoscaling:     │             │    │  │
│  │  │  │  Min: 2 Max: 5    │   │  Min: 2 Max: 5    │             │    │  │
│  │  │  └─────────┬─────────┘   └───────────────────┘             │    │  │
│  │  │            │                                                 │    │  │
│  │  │            ▼                                                 │    │  │
│  │  │  ┌─────────────────────────────────────────────────────┐   │    │  │
│  │  │  │              Data Layer (Stateful)                   │   │    │  │
│  │  │  │                                                       │   │    │  │
│  │  │  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │   │    │  │
│  │  │  │  │  PostgreSQL  │  │   MongoDB    │  │   Redis   │ │   │    │  │
│  │  │  │  │              │  │              │  │           │ │   │    │  │
│  │  │  │  │  Port: 5432  │  │  Port: 27017 │  │ Port: 6379│ │   │    │  │
│  │  │  │  │  Replicas: 1 │  │  Replicas: 1 │  │Replicas: 1│ │   │    │  │
│  │  │  │  │              │  │              │  │           │ │   │    │  │
│  │  │  │  │  CPU: 250m   │  │  CPU: 250m   │  │ CPU: 100m │ │   │    │  │
│  │  │  │  │  Mem: 256Mi  │  │  Mem: 256Mi  │  │Mem: 128Mi │ │   │    │  │
│  │  │  │  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘ │   │    │  │
│  │  │  │         │                 │                 │       │   │    │  │
│  │  │  │         ▼                 ▼                 ▼       │   │    │  │
│  │  │  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │   │    │  │
│  │  │  │  │ postgres-pvc │  │ mongodb-pvc  │  │ redis-pvc │ │   │    │  │
│  │  │  │  │   20 GB      │  │   20 GB      │  │   5 GB    │ │   │    │  │
│  │  │  │  │ Premium SSD  │  │ Premium SSD  │  │Premium SSD│ │   │    │  │
│  │  │  │  └──────────────┘  └──────────────┘  └───────────┘ │   │    │  │
│  │  │  └─────────────────────────────────────────────────────┘   │    │  │
│  │  │                                                              │    │  │
│  │  │  ┌──────────────────────────────────────────────────────┐  │    │  │
│  │  │  │         ConfigMaps & Secrets                          │  │    │  │
│  │  │  │  • app-config: Application configuration              │  │    │  │
│  │  │  │  • app-secrets: Sensitive credentials                 │  │    │  │
│  │  │  │  • frontend-config: Frontend environment vars         │  │    │  │
│  │  │  └──────────────────────────────────────────────────────┘  │    │  │
│  │  └──────────────────────────────────────────────────────────┘    │  │
│  │                                                                    │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │              Namespace: ingress-nginx                       │  │  │
│  │  │  • NGINX Ingress Controller (Helm Chart)                   │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │          Azure Container Registry (ACR)                         │  │
│  │  • ssc-backend:latest                                           │  │
│  │  • ssc-frontend:latest                                          │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │          Azure Monitor (Optional)                               │  │
│  │  • Container Insights                                           │  │
│  │  • Application Insights                                         │  │
│  │  • Log Analytics Workspace                                      │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. **Frontend Pods (React/Vite)**
- **Deployment**: `frontend`
- **Service**: `ClusterIP` on port 3000
- **Replicas**: 2-5 (with HPA - Horizontal Pod Autoscaler)
- **Image**: `{ACR}.azurecr.io/ssc-frontend:latest`
- **Resources**:
  - Requests: 100m CPU, 128Mi Memory
  - Limits: 500m CPU, 512Mi Memory
- **Health Checks**: HTTP GET on `/`
- **Scaling**: Auto-scales based on CPU (70%) and Memory (80%)

### 2. **Backend Pods (FastAPI)**
- **Deployment**: `backend`
- **Service**: `ClusterIP` on port 8000
- **Replicas**: 2-5 (with HPA)
- **Image**: `{ACR}.azurecr.io/ssc-backend:latest`
- **Resources**:
  - Requests: 250m CPU, 256Mi Memory
  - Limits: 1 CPU, 1Gi Memory
- **Health Checks**: HTTP GET on `/health`
- **Scaling**: Auto-scales based on CPU (70%) and Memory (80%)
- **Workers**: 4 uvicorn workers

### 3. **PostgreSQL Database**
- **Deployment**: `postgres`
- **Service**: `ClusterIP` on port 5432
- **Replicas**: 1 (stateful)
- **Image**: `postgres:16-alpine`
- **Storage**: 20GB Azure Premium SSD (PVC)
- **Resources**:
  - Requests: 250m CPU, 256Mi Memory
  - Limits: 1 CPU, 1Gi Memory
- **Production Alternative**: Azure Database for PostgreSQL (managed)

### 4. **MongoDB Database**
- **Deployment**: `mongodb`
- **Service**: `ClusterIP` on port 27017
- **Replicas**: 1 (stateful)
- **Image**: `mongo:7-jammy`
- **Storage**: 20GB Azure Premium SSD (PVC)
- **Resources**:
  - Requests: 250m CPU, 256Mi Memory
  - Limits: 1 CPU, 1Gi Memory
- **Production Alternative**: Azure Cosmos DB for MongoDB API (managed)

### 5. **Redis Cache**
- **Deployment**: `redis`
- **Service**: `ClusterIP` on port 6379
- **Replicas**: 1 (stateful)
- **Image**: `redis:7-alpine`
- **Storage**: 5GB Azure Premium SSD (PVC)
- **Resources**:
  - Requests: 100m CPU, 128Mi Memory
  - Limits: 500m CPU, 512Mi Memory
- **Production Alternative**: Azure Cache for Redis (managed)

### 6. **Ingress Controller**
- **Type**: NGINX Ingress Controller (Helm)
- **Service**: LoadBalancer (Azure LB)
- **Routes**:
  - `/api/*` → Backend Service (port 8000)
  - `/*` → Frontend Service (port 3000)
- **SSL**: Supports Let's Encrypt via cert-manager
- **Features**: Rate limiting, CORS, compression

---

## Total Pod Count

### Minimum Configuration (Development):
- Frontend: 2 pods
- Backend: 2 pods
- PostgreSQL: 1 pod
- MongoDB: 1 pod
- Redis: 1 pod
- **Total: 7 pods**

### Maximum Configuration (Under Load):
- Frontend: 5 pods (autoscaled)
- Backend: 5 pods (autoscaled)
- PostgreSQL: 1 pod
- MongoDB: 1 pod
- Redis: 1 pod
- **Total: 13 pods**

### Production Recommended (Managed Services):
- Frontend: 2-5 pods
- Backend: 2-5 pods
- Azure Database for PostgreSQL (managed - no pods)
- Azure Cosmos DB (managed - no pods)
- Azure Cache for Redis (managed - no pods)
- **Total: 4-10 application pods**

---

## Resource Requirements

### Node Pool Configuration:
- **Node VM Size**: Standard_D2s_v3 (2 vCPU, 8 GB RAM)
- **Node Count**: 3-5 nodes
- **Total Cluster Capacity**: 6-10 vCPU, 24-40 GB RAM

### Resource Allocation:
```
Component      | Requests      | Limits        | Pods | Total Request | Total Limit
---------------|---------------|---------------|------|---------------|------------
Frontend       | 100m / 128Mi  | 500m / 512Mi  | 2-5  | 200m-500m     | 1-2.5 CPU
Backend        | 250m / 256Mi  | 1 / 1Gi       | 2-5  | 500m-1.25     | 2-5 CPU
PostgreSQL     | 250m / 256Mi  | 1 / 1Gi       | 1    | 250m          | 1 CPU
MongoDB        | 250m / 256Mi  | 1 / 1Gi       | 1    | 250m          | 1 CPU
Redis          | 100m / 128Mi  | 500m / 512Mi  | 1    | 100m          | 500m
---------------|---------------|---------------|------|---------------|------------
TOTAL (min)    |               |               | 7    | ~1.3 CPU      | ~5 CPU
TOTAL (max)    |               |               | 13   | ~2.6 CPU      | ~10 CPU
```

---

## Storage Configuration

### Persistent Volumes:
1. **postgres-pvc**: 20GB Premium SSD (ReadWriteOnce)
2. **mongodb-pvc**: 20GB Premium SSD (ReadWriteOnce)
3. **redis-pvc**: 5GB Premium SSD (ReadWriteOnce)

**Total Storage**: 45GB

### Storage Classes:
- `managed-premium`: Azure Premium SSD (faster, production)
- `default`: Azure Standard SSD (cheaper, development)
- `azurefile`: Azure Files (for ReadWriteMany)

---

## Network Architecture

### Internal Communication (ClusterIP):
- Frontend → Backend: `http://backend:8000`
- Backend → PostgreSQL: `postgres:5432`
- Backend → MongoDB: `mongodb:27017`
- Backend → Redis: `redis:6379`

### External Access (Ingress):
- Users → Azure Load Balancer → Ingress → Frontend/Backend

### DNS Configuration:
```
yourdomain.com           A    <Load Balancer IP>
www.yourdomain.com       A    <Load Balancer IP>
```

---

## Security

### Network Policies:
- Pods communicate only within namespace
- Databases only accessible by backend
- Frontend only accessible via Ingress

### Secrets Management:
- Kubernetes Secrets for sensitive data
- Azure Key Vault integration (recommended)
- Environment variables from ConfigMaps

### Container Security:
- Non-root user in containers
- Read-only root filesystem where possible
- Security context constraints

---

## High Availability

### Application Layer:
- Multiple replicas (2-5) for frontend and backend
- Rolling updates with zero downtime
- Health checks and automatic restarts

### Data Layer:
- Persistent volumes for data persistence
- Regular backups (Azure Backup)
- **Production**: Use managed services (HA built-in)

### Load Balancing:
- Azure Load Balancer for external traffic
- Kubernetes Services for internal traffic
- Session affinity support

---

## Monitoring and Logging

### Metrics:
- Azure Monitor Container Insights
- Prometheus (optional)
- Grafana dashboards (optional)

### Logging:
- Application logs → stdout/stderr
- Centralized logging via Azure Log Analytics
- Log retention: 30-90 days

### Alerts:
- Pod crashes or restarts
- High CPU/Memory usage
- Failed health checks
- Database connection errors

---

## Backup and Disaster Recovery

### Database Backups:
- PostgreSQL: pg_dump scheduled jobs
- MongoDB: mongodump scheduled jobs
- Automated backup to Azure Blob Storage

### Application Backups:
- Helm charts and manifests in Git
- Docker images in ACR with retention policy

### Disaster Recovery:
- Multi-region deployment (optional)
- Automated failover with Traffic Manager
- RTO: < 1 hour, RPO: < 15 minutes

---

## Cost Optimization

### Recommendations:
1. **Use Azure Reserved Instances**: Save 30-50% on VM costs
2. **Managed Services**: Replace in-cluster databases with Azure PaaS
3. **Autoscaling**: Scale down during off-hours
4. **Storage Tiers**: Use Standard SSD for non-critical workloads
5. **Spot Instances**: For non-production workloads

### Estimated Monthly Cost:
- **Development**: $200-400/month
- **Production (self-managed)**: $800-1200/month
- **Production (managed services)**: $1200-2000/month

---

## Deployment Workflow

```
1. Build Docker Images
   ├── Backend: FastAPI app
   └── Frontend: React build with nginx

2. Push to ACR
   ├── Tag with version
   └── Latest tag

3. Deploy to AKS
   ├── ConfigMaps & Secrets
   ├── Storage (PVCs)
   ├── Databases (Postgres, Mongo, Redis)
   ├── Backend (wait for ready)
   ├── Frontend
   └── Ingress

4. Run Migrations
   └── Alembic upgrade head

5. Verify Deployment
   ├── Check pod status
   ├── Test health endpoints
   └── Validate ingress routing
```

---

## Next Steps

1. Review and update configuration files
2. Update secrets with production values
3. Configure DNS records
4. Set up SSL certificates (Let's Encrypt)
5. Configure Azure Monitor and alerts
6. Set up CI/CD pipeline (Azure DevOps or GitHub Actions)
7. Plan backup strategy
8. Conduct load testing
9. Document runbooks for common operations
10. Train team on Kubernetes operations
