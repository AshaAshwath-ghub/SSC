# AKS Deployment - Quick Reference Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Deployment Commands](#deployment-commands)
- [Common Operations](#common-operations)
- [Troubleshooting](#troubleshooting)
- [Scaling](#scaling)
- [Updates and Rollbacks](#updates-and-rollbacks)

---

## Prerequisites

### Required Tools
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install kubectl
az aks install-cli

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installations
az --version
kubectl version --client
helm version
```

### Login to Azure
```bash
az login
az account set --subscription <subscription-id>
```

---

## Initial Setup

### 1. Create AKS Cluster (One-time)
```bash
# Set variables
export RESOURCE_GROUP="ssc-app-rg"
export CLUSTER_NAME="ssc-aks-cluster"
export LOCATION="eastus"
export ACR_NAME="sscappregistry"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create AKS cluster (takes 10-15 minutes)
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3 \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --network-plugin azure \
  --enable-managed-identity

# Get credentials
az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME
```

### 2. Create Container Registry (One-time)
```bash
# Create ACR
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic

# Attach ACR to AKS
az aks update --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME --attach-acr $ACR_NAME
```

### 3. Install NGINX Ingress (One-time)
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

---

## Deployment Commands

### Full Automated Deployment
```bash
# Use the deployment script
cd deploy/aks
chmod +x deploy.sh
./deploy.sh

# Select option 1 for full deployment
```

### Manual Step-by-Step Deployment

#### 1. Build and Push Images
```bash
# Login to ACR
az acr login --name $ACR_NAME

# Build backend
docker build -f deploy/docker/Dockerfile.backend.production -t $ACR_NAME.azurecr.io/ssc-backend:latest .
docker push $ACR_NAME.azurecr.io/ssc-backend:latest

# Build frontend
docker build -f deploy/docker/Dockerfile.frontend.production -t $ACR_NAME.azurecr.io/ssc-frontend:latest .
docker push $ACR_NAME.azurecr.io/ssc-frontend:latest
```

#### 2. Create Namespace
```bash
kubectl create namespace ssc-app
kubectl config set-context --current --namespace=ssc-app
```

#### 3. Deploy Kubernetes Resources
```bash
cd deploy/aks/k8s

# Deploy in order
kubectl apply -f 01-configmap.yaml
kubectl apply -f 02-secrets.yaml          # Update secrets first!
kubectl apply -f 03-storage.yaml
kubectl apply -f 04-postgres.yaml
kubectl apply -f 05-mongodb.yaml
kubectl apply -f 06-redis.yaml

# Wait for databases
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s
kubectl wait --for=condition=ready pod -l app=mongodb --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis --timeout=300s

# Deploy application
kubectl apply -f 07-backend.yaml
kubectl wait --for=condition=ready pod -l app=backend --timeout=300s

kubectl apply -f 08-frontend.yaml
kubectl apply -f 09-ingress.yaml
```

#### 4. Run Database Migrations
```bash
BACKEND_POD=$(kubectl get pod -l app=backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $BACKEND_POD -- alembic upgrade head
```

---

## Common Operations

### View Resources
```bash
# All pods
kubectl get pods

# All services
kubectl get svc

# All deployments
kubectl get deployments

# Ingress
kubectl get ingress

# Persistent volumes
kubectl get pvc

# All resources
kubectl get all
```

### View Logs
```bash
# Backend logs
kubectl logs -f deployment/backend

# Frontend logs
kubectl logs -f deployment/frontend

# Specific pod
kubectl logs -f <pod-name>

# Previous container logs (after crash)
kubectl logs <pod-name> --previous

# All pods with label
kubectl logs -f -l app=backend --all-containers=true
```

### Describe Resources (for debugging)
```bash
kubectl describe pod <pod-name>
kubectl describe deployment <deployment-name>
kubectl describe service <service-name>
```

### Execute Commands in Pods
```bash
# Shell into backend pod
kubectl exec -it deployment/backend -- /bin/sh

# Run database migrations
kubectl exec -it deployment/backend -- alembic upgrade head

# Connect to PostgreSQL
kubectl exec -it deployment/postgres -- psql -U postgres -d appdb

# Connect to MongoDB
kubectl exec -it deployment/mongodb -- mongosh appdb

# Connect to Redis
kubectl exec -it deployment/redis -- redis-cli
```

### Port Forwarding (for debugging)
```bash
# Access backend locally
kubectl port-forward deployment/backend 8000:8000
# Access at: http://localhost:8000

# Access frontend locally
kubectl port-forward deployment/frontend 3000:3000
# Access at: http://localhost:3000

# Access PostgreSQL locally
kubectl port-forward deployment/postgres 5432:5432
# Connect with: psql -h localhost -U postgres -d appdb
```

### Get External IP
```bash
# Get Load Balancer IP
kubectl get svc -n ingress-nginx

# Or extract just the IP
EXTERNAL_IP=$(kubectl get svc -n ingress-nginx nginx-ingress-ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "External IP: $EXTERNAL_IP"
```

---

## Scaling

### Manual Scaling
```bash
# Scale backend
kubectl scale deployment/backend --replicas=5

# Scale frontend
kubectl scale deployment/frontend --replicas=3

# Scale to 0 (stop)
kubectl scale deployment/backend --replicas=0
```

### Autoscaling Status
```bash
# View HPA status
kubectl get hpa

# Detailed HPA info
kubectl describe hpa backend-hpa
kubectl describe hpa frontend-hpa
```

### Node Pool Scaling
```bash
# Scale AKS nodes
az aks scale \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --node-count 5
```

---

## Updates and Rollbacks

### Update Application Image
```bash
# Build and push new image
docker build -f deploy/docker/Dockerfile.backend.production -t $ACR_NAME.azurecr.io/ssc-backend:v2.0 .
docker push $ACR_NAME.azurecr.io/ssc-backend:v2.0

# Update deployment
kubectl set image deployment/backend backend=$ACR_NAME.azurecr.io/ssc-backend:v2.0

# Watch rollout
kubectl rollout status deployment/backend
```

### Rollout History
```bash
# View rollout history
kubectl rollout history deployment/backend

# View specific revision
kubectl rollout history deployment/backend --revision=2
```

### Rollback
```bash
# Rollback to previous version
kubectl rollout undo deployment/backend

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=3

# Restart deployment (force new pods)
kubectl rollout restart deployment/backend
```

### Update ConfigMap or Secrets
```bash
# Edit ConfigMap
kubectl edit configmap app-config

# Edit Secrets
kubectl edit secret app-secrets

# Restart pods to pick up changes
kubectl rollout restart deployment/backend
kubectl rollout restart deployment/frontend
```

---

## Troubleshooting

### Pod Issues

#### Pod Not Starting
```bash
# Check pod status
kubectl get pods

# Describe pod (see events)
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Check previous container logs
kubectl logs <pod-name> --previous
```

#### CrashLoopBackOff
```bash
# View logs
kubectl logs <pod-name> --previous

# Check resource limits
kubectl describe pod <pod-name> | grep -A 5 "Limits"

# Check liveness/readiness probes
kubectl describe pod <pod-name> | grep -A 10 "Liveness"
```

#### ImagePullBackOff
```bash
# Check image name
kubectl describe pod <pod-name> | grep "Image:"

# Check if ACR is attached
az aks show --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME --query "servicePrincipalProfile"

# Reattach ACR
az aks update --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME --attach-acr $ACR_NAME
```

### Database Connection Issues
```bash
# Test PostgreSQL connection
kubectl run -it --rm pg-test --image=postgres:16-alpine --restart=Never -- psql -h postgres -U postgres -d appdb

# Test MongoDB connection
kubectl run -it --rm mongo-test --image=mongo:7 --restart=Never -- mongosh mongodb://mongodb:27017/appdb

# Test Redis connection
kubectl run -it --rm redis-test --image=redis:7-alpine --restart=Never -- redis-cli -h redis ping
```

### Ingress Issues
```bash
# Check ingress
kubectl describe ingress app-ingress

# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/nginx-ingress-ingress-nginx-controller

# Test backend service
kubectl run -it --rm curl-test --image=curlimages/curl --restart=Never -- curl http://backend:8000/health

# Test frontend service
kubectl run -it --rm curl-test --image=curlimages/curl --restart=Never -- curl http://frontend:3000
```

### Resource Issues
```bash
# Check node resources
kubectl top nodes

# Check pod resources
kubectl top pods

# Check resource quotas
kubectl describe resourcequota

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

---

## Monitoring

### Real-time Monitoring
```bash
# Watch pods
watch kubectl get pods

# Watch all resources
watch kubectl get all

# Stream logs
kubectl logs -f deployment/backend --all-containers=true
```

### Metrics
```bash
# Node metrics
kubectl top nodes

# Pod metrics
kubectl top pods

# Specific pod
kubectl top pod <pod-name>
```

### Azure Monitor
```bash
# View container insights in Azure Portal
az aks show --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME --query "addonProfiles.omsagent"

# Enable container insights (if not enabled)
az aks enable-addons --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME --addons monitoring
```

---

## Backup and Restore

### Database Backup
```bash
# PostgreSQL backup
kubectl exec deployment/postgres -- pg_dump -U postgres appdb > backup-$(date +%Y%m%d).sql

# MongoDB backup
kubectl exec deployment/mongodb -- mongodump --db appdb --archive > backup-$(date +%Y%m%d).archive

# Copy backup to local
kubectl cp <postgres-pod>:/backup.sql ./backup.sql
```

### Database Restore
```bash
# PostgreSQL restore
kubectl exec -i deployment/postgres -- psql -U postgres appdb < backup.sql

# MongoDB restore
kubectl exec -i deployment/mongodb -- mongorestore --db appdb --archive < backup.archive
```

---

## Cleanup

### Delete Application (keep cluster)
```bash
kubectl delete namespace ssc-app
```

### Delete Everything
```bash
# Delete AKS cluster
az aks delete --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME --yes --no-wait

# Delete resource group (including ACR)
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

---

## Useful Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# kubectl aliases
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgd='kubectl get deployments'
alias kga='kubectl get all'
alias kl='kubectl logs -f'
alias kd='kubectl describe'
alias ke='kubectl exec -it'

# namespace
alias kn='kubectl config set-context --current --namespace'

# quick pod shell
alias ksh='kubectl exec -it deployment/backend -- /bin/sh'

# quick logs
alias klb='kubectl logs -f deployment/backend'
alias klf='kubectl logs -f deployment/frontend'
```

---

## Support and Resources

- **Kubernetes Docs**: https://kubernetes.io/docs/
- **AKS Docs**: https://docs.microsoft.com/en-us/azure/aks/
- **kubectl Cheat Sheet**: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- **Helm Docs**: https://helm.sh/docs/

---

## Emergency Contacts

- **Azure Support**: Open ticket in Azure Portal
- **Development Team**: [Your team contact]
- **On-Call**: [Your on-call rotation]
