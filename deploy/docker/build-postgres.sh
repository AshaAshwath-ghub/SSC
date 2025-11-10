#!/bin/bash

# Build and Push PostgreSQL Image Script
# This script builds the custom PostgreSQL image and optionally pushes to ACR

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="ssc-postgres"
VERSION="${VERSION:-16.0}"
ACR_NAME="${ACR_NAME:-sscappregistry}"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/../.."

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to build image locally
build_local() {
    print_info "Building PostgreSQL image locally..."

    cd "$PROJECT_ROOT"

    docker build \
        -f deploy/docker/Dockerfile.postgres \
        -t $IMAGE_NAME:$VERSION \
        -t $IMAGE_NAME:latest \
        .

    print_info "Image built successfully!"
    print_info "Tagged as: $IMAGE_NAME:$VERSION and $IMAGE_NAME:latest"
}

# Function to test image locally
test_local() {
    print_info "Testing PostgreSQL image locally..."

    # Check if container already exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${IMAGE_NAME}-test$"; then
        print_warning "Removing existing test container..."
        docker rm -f ${IMAGE_NAME}-test
    fi

    # Run container
    print_info "Starting test container..."
    docker run -d \
        --name ${IMAGE_NAME}-test \
        -e POSTGRES_PASSWORD=testpass \
        -e POSTGRES_DB=testdb \
        -p 5433:5432 \
        $IMAGE_NAME:latest

    # Wait for PostgreSQL to be ready
    print_info "Waiting for PostgreSQL to be ready..."
    sleep 10

    # Test connection
    if docker exec ${IMAGE_NAME}-test pg_isready -U postgres; then
        print_info "PostgreSQL is ready and accepting connections!"

        # Show database info
        print_info "Database information:"
        docker exec ${IMAGE_NAME}-test psql -U postgres -d testdb -c "SELECT version();"
        docker exec ${IMAGE_NAME}-test psql -U postgres -d testdb -c "SELECT * FROM pg_extension;"

        print_info "Test successful!"
    else
        print_error "PostgreSQL health check failed!"
        docker logs ${IMAGE_NAME}-test
        exit 1
    fi

    # Cleanup
    print_info "Cleaning up test container..."
    docker rm -f ${IMAGE_NAME}-test
}

# Function to push to ACR
push_to_acr() {
    print_info "Pushing image to Azure Container Registry..."

    # Login to ACR
    print_info "Logging into ACR: $ACR_NAME"
    az acr login --name $ACR_NAME

    # Tag for ACR
    ACR_IMAGE="$ACR_NAME.azurecr.io/$IMAGE_NAME"

    docker tag $IMAGE_NAME:$VERSION $ACR_IMAGE:$VERSION
    docker tag $IMAGE_NAME:latest $ACR_IMAGE:latest

    # Push to ACR
    print_info "Pushing $ACR_IMAGE:$VERSION"
    docker push $ACR_IMAGE:$VERSION

    print_info "Pushing $ACR_IMAGE:latest"
    docker push $ACR_IMAGE:latest

    print_info "Successfully pushed to ACR!"
    print_info "Image: $ACR_IMAGE:$VERSION"
    print_info "Image: $ACR_IMAGE:latest"
}

# Main menu
show_menu() {
    echo ""
    echo "PostgreSQL Image Build Script"
    echo "=============================="
    echo "1. Build locally only"
    echo "2. Build and test locally"
    echo "3. Build, test, and push to ACR"
    echo "4. Push existing image to ACR"
    echo "5. Exit"
    echo ""
}

main() {
    print_info "PostgreSQL Image Builder for SSC Application"
    print_info "Current settings:"
    echo "  - Image name: $IMAGE_NAME"
    echo "  - Version: $VERSION"
    echo "  - ACR name: $ACR_NAME"
    echo ""

    if [ "$1" ]; then
        # Non-interactive mode
        case $1 in
            build)
                build_local
                ;;
            test)
                build_local
                test_local
                ;;
            push)
                build_local
                test_local
                push_to_acr
                ;;
            push-only)
                push_to_acr
                ;;
            *)
                print_error "Invalid option: $1"
                echo "Usage: $0 {build|test|push|push-only}"
                exit 1
                ;;
        esac
    else
        # Interactive mode
        while true; do
            show_menu
            read -p "Select option (1-5): " option

            case $option in
                1)
                    build_local
                    break
                    ;;
                2)
                    build_local
                    test_local
                    break
                    ;;
                3)
                    build_local
                    test_local
                    push_to_acr
                    break
                    ;;
                4)
                    push_to_acr
                    break
                    ;;
                5)
                    print_info "Exiting..."
                    exit 0
                    ;;
                *)
                    print_error "Invalid option. Please select 1-5."
                    ;;
            esac
        done
    fi

    print_info "Done!"
}

# Run main function
main "$@"
