#!/bin/bash

# AKS Deployment Script for SSC Application
# This script automates the deployment process to Azure Kubernetes Service

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-ssc-app-rg}"
CLUSTER_NAME="${CLUSTER_NAME:-ssc-aks-cluster}"
ACR_NAME="${ACR_NAME:-sscappregistry}"
NAMESPACE="${NAMESPACE:-ssc-app}"
LOCATION="${LOCATION:-eastus}"

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check if Azure CLI is installed
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI is not installed. Please install it first."
        exit 1
    fi

    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install it first."
        exit 1
    fi

    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        print_error "helm is not installed. Please install it first."
        exit 1
    fi

    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "docker is not installed. Please install it first."
        exit 1
    fi

    print_info "All prerequisites are met!"
}

create_aks_cluster() {
    print_info "Creating AKS cluster..."

    # Check if resource group exists
    if ! az group show --name "$RESOURCE_GROUP" &> /dev/null; then
        print_info "Creating resource group: $RESOURCE_GROUP"
        az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
    else
        print_info "Resource group already exists: $RESOURCE_GROUP"
    fi

    # Check if AKS cluster exists
    if ! az aks show --resource-group "$RESOURCE_GROUP" --name "$CLUSTER_NAME" &> /dev/null; then
        print_info "Creating AKS cluster: $CLUSTER_NAME (this may take 10-15 minutes)"
        az aks create \
            --resource-group "$RESOURCE_GROUP" \
            --name "$CLUSTER_NAME" \
            --node-count 3 \
            --node-vm-size Standard_D2s_v3 \
            --enable-addons monitoring \
            --generate-ssh-keys \
            --network-plugin azure \
            --enable-managed-identity
    else
        print_info "AKS cluster already exists: $CLUSTER_NAME"
    fi

    # Get credentials
    print_info "Getting AKS credentials..."
    az aks get-credentials --resource-group "$RESOURCE_GROUP" --name "$CLUSTER_NAME" --overwrite-existing
}

create_acr() {
    print_info "Creating Azure Container Registry..."

    # Check if ACR exists
    if ! az acr show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        print_info "Creating ACR: $ACR_NAME"
        az acr create --resource-group "$RESOURCE_GROUP" --name "$ACR_NAME" --sku Basic
    else
        print_info "ACR already exists: $ACR_NAME"
    fi

    # Attach ACR to AKS
    print_info "Attaching ACR to AKS..."
    az aks update --resource-group "$RESOURCE_GROUP" --name "$CLUSTER_NAME" --attach-acr "$ACR_NAME"
}

build_and_push_images() {
    print_info "Building and pushing Docker images..."

    # Login to ACR
    az acr login --name "$ACR_NAME"

    # Get script directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    PROJECT_ROOT="$SCRIPT_DIR/../.."

    # Build backend image
    print_info "Building backend image..."
    cd "$PROJECT_ROOT"
    docker build -f deploy/docker/Dockerfile.backend.production -t "$ACR_NAME.azurecr.io/ssc-backend:latest" .

    print_info "Pushing backend image..."
    docker push "$ACR_NAME.azurecr.io/ssc-backend:latest"

    # Build frontend image
    print_info "Building frontend image..."
    docker build -f deploy/docker/Dockerfile.frontend.production -t "$ACR_NAME.azurecr.io/ssc-frontend:latest" .

    print_info "Pushing frontend image..."
    docker push "$ACR_NAME.azurecr.io/ssc-frontend:latest"

    cd "$SCRIPT_DIR"
}

install_nginx_ingress() {
    print_info "Installing NGINX Ingress Controller..."

    # Add Helm repo
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update

    # Check if already installed
    if helm list -n ingress-nginx | grep -q nginx-ingress; then
        print_info "NGINX Ingress already installed"
    else
        print_info "Installing NGINX Ingress..."
        helm install nginx-ingress ingress-nginx/ingress-nginx \
            --namespace ingress-nginx \
            --create-namespace \
            --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz
    fi
}

create_namespace() {
    print_info "Creating namespace: $NAMESPACE"

    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        print_info "Namespace already exists: $NAMESPACE"
    else
        kubectl create namespace "$NAMESPACE"
    fi

    # Set current context to namespace
    kubectl config set-context --current --namespace="$NAMESPACE"
}

deploy_application() {
    print_info "Deploying application to AKS..."

    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    K8S_DIR="$SCRIPT_DIR/k8s"

    # Deploy in order
    print_info "1. Deploying ConfigMaps and Secrets..."
    kubectl apply -f "$K8S_DIR/01-configmap.yaml"

    print_warning "Please update secrets in 02-secrets.yaml before deploying!"
    read -p "Have you updated the secrets? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl apply -f "$K8S_DIR/02-secrets.yaml"
    else
        print_error "Please update secrets and run deployment again"
        exit 1
    fi

    print_info "2. Deploying Storage (PVCs)..."
    kubectl apply -f "$K8S_DIR/03-storage.yaml"

    print_info "3. Deploying Databases..."
    kubectl apply -f "$K8S_DIR/04-postgres.yaml"
    kubectl apply -f "$K8S_DIR/05-mongodb.yaml"
    kubectl apply -f "$K8S_DIR/06-redis.yaml"

    print_info "Waiting for databases to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s
    kubectl wait --for=condition=ready pod -l app=mongodb --timeout=300s
    kubectl wait --for=condition=ready pod -l app=redis --timeout=300s

    print_info "4. Deploying Backend API..."
    kubectl apply -f "$K8S_DIR/07-backend.yaml"

    print_info "Waiting for backend to be ready..."
    kubectl wait --for=condition=ready pod -l app=backend --timeout=300s

    print_info "5. Deploying Frontend..."
    kubectl apply -f "$K8S_DIR/08-frontend.yaml"

    print_info "6. Deploying Ingress..."
    kubectl apply -f "$K8S_DIR/09-ingress.yaml"

    print_info "Deployment completed!"
}

run_migrations() {
    print_info "Running database migrations..."

    # Get backend pod name
    BACKEND_POD=$(kubectl get pod -l app=backend -o jsonpath='{.items[0].metadata.name}')

    if [ -z "$BACKEND_POD" ]; then
        print_error "No backend pod found!"
        return 1
    fi

    print_info "Running migrations on pod: $BACKEND_POD"
    kubectl exec -it "$BACKEND_POD" -- alembic upgrade head
}

show_status() {
    print_info "Deployment Status:"
    echo ""

    print_info "Pods:"
    kubectl get pods
    echo ""

    print_info "Services:"
    kubectl get svc
    echo ""

    print_info "Ingress:"
    kubectl get ingress
    echo ""

    print_info "Getting external IP (this may take a few minutes)..."
    EXTERNAL_IP=$(kubectl get svc -n ingress-nginx nginx-ingress-ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

    if [ -z "$EXTERNAL_IP" ]; then
        print_warning "External IP not yet assigned. Check again in a few minutes."
    else
        print_info "External IP: $EXTERNAL_IP"
        print_info "Configure your DNS A record to point to this IP"
    fi
}

# Main deployment flow
main() {
    print_info "Starting AKS deployment for SSC Application"
    print_info "============================================="
    echo ""

    check_prerequisites

    # Menu
    echo "Select deployment option:"
    echo "1. Full deployment (create cluster, build images, deploy)"
    echo "2. Deploy only (assumes cluster exists)"
    echo "3. Build and push images only"
    echo "4. Run migrations only"
    echo "5. Show status"
    read -p "Enter option (1-5): " option

    case $option in
        1)
            create_aks_cluster
            create_acr
            install_nginx_ingress
            build_and_push_images
            create_namespace
            deploy_application
            run_migrations
            show_status
            ;;
        2)
            create_namespace
            deploy_application
            run_migrations
            show_status
            ;;
        3)
            build_and_push_images
            ;;
        4)
            run_migrations
            ;;
        5)
            show_status
            ;;
        *)
            print_error "Invalid option"
            exit 1
            ;;
    esac

    print_info "Done!"
}

# Run main function
main
