# AKS Deployment Guide - Complete Process

## Phase 1: Create and Configure AKS Cluster

### Step 1: Create AKS Cluster

```bash
# Set variables
RESOURCE_GROUP="ssc-app-rg"
CLUSTER_NAME="ssc-aks-cluster"
LOCATION="eastus"
NODE_COUNT=3
NODE_SIZE="Standard_D2s_v3"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Create AKS cluster
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --node-count $NODE_COUNT \
  --node-vm-size $NODE_SIZE \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --network-plugin azure \
  --enable-managed-identity

# Get credentials
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME
```

### Step 2: Install NGINX Ingress Controller

```bash
# Add Helm repo
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install NGINX Ingress
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz
```

### Step 3: Create Container Registry (ACR)

```bash
ACR_NAME="sscappregistry"

# Create ACR
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic

# Attach ACR to AKS
az aks update \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --attach-acr $ACR_NAME
```

### Step 4: Build and Push Images to ACR

```bash
# Login to ACR
az acr login --name $ACR_NAME

# Build and push backend image
cd backend
docker build -t $ACR_NAME.azurecr.io/ssc-backend:latest .
docker push $ACR_NAME.azurecr.io/ssc-backend:latest

# Build and push frontend image
cd ../full-version
docker build -f ../deploy/docker/Dockerfile.frontend -t $ACR_NAME.azurecr.io/ssc-frontend:latest .
docker push $ACR_NAME.azurecr.io/ssc-frontend:latest
```

---

## Phase 2: Deploy to AKS

### Step 1: Create Namespace

```bash
kubectl create namespace ssc-app
kubectl config set-context --current --namespace=ssc-app
```

### Step 2: Deploy in Order

```bash
# 1. Deploy ConfigMaps and Secrets
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secrets.yaml

# 2. Deploy Storage (PVCs)
kubectl apply -f k8s/03-storage.yaml

# 3. Deploy Databases
kubectl apply -f k8s/04-postgres.yaml
kubectl apply -f k8s/05-mongodb.yaml
kubectl apply -f k8s/06-redis.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s
kubectl wait --for=condition=ready pod -l app=mongodb --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis --timeout=300s

# 4. Deploy Backend API
kubectl apply -f k8s/07-backend.yaml

# Wait for backend to be ready
kubectl wait --for=condition=ready pod -l app=backend --timeout=300s

# 5. Deploy Frontend
kubectl apply -f k8s/08-frontend.yaml

# 6. Deploy Ingress
kubectl apply -f k8s/09-ingress.yaml
```

### Step 3: Verify Deployment

```bash
# Check all pods
kubectl get pods

# Check services
kubectl get svc

# Check ingress
kubectl get ingress

# Get external IP
kubectl get svc -n ingress-nginx
```

---

## Phase 3: Post-Deployment

### Initialize Database

```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pod -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec -it $BACKEND_POD -- alembic upgrade head

# Optional: Seed initial data
kubectl exec -it $BACKEND_POD -- python -m app.db.seed
```

### Monitor Application

```bash
# View logs
kubectl logs -f deployment/backend
kubectl logs -f deployment/frontend

# Check resource usage
kubectl top pods
kubectl top nodes
```

---

## Phase 4: DNS and SSL (Optional)

### Configure DNS

```bash
# Get Load Balancer IP
EXTERNAL_IP=$(kubectl get svc -n ingress-nginx nginx-ingress-ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Configure DNS A record:"
echo "yourdomain.com -> $EXTERNAL_IP"
```

### Install cert-manager for SSL

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f k8s/10-cert-issuer.yaml
```

---

## Troubleshooting

### Common Commands

```bash
# Describe pod issues
kubectl describe pod <pod-name>

# View pod logs
kubectl logs <pod-name> --previous

# Get events
kubectl get events --sort-by='.lastTimestamp'

# Restart deployment
kubectl rollout restart deployment/backend
kubectl rollout restart deployment/frontend

# Scale deployment
kubectl scale deployment/backend --replicas=3
kubectl scale deployment/frontend --replicas=3
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
kubectl run -it --rm --image=postgres:16-alpine pg-test -- psql -h postgres -U postgres -d appdb

# Test MongoDB connection
kubectl run -it --rm --image=mongo:7 mongo-test -- mongosh mongodb://mongodb:27017/appdb

# Test Redis connection
kubectl run -it --rm --image=redis:7-alpine redis-test -- redis-cli -h redis ping
```
