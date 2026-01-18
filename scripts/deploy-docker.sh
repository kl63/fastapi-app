#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 FastAPI Docker Deployment Script${NC}"

# Configuration
REGISTRY="ghcr.io"
REPO_OWNER="${GITHUB_REPOSITORY_OWNER:-kevinlin192003}"
REPO_NAME="${GITHUB_REPOSITORY_NAME:-fastapi-app}"
IMAGE_NAME="${REGISTRY}/${REPO_OWNER}/${REPO_NAME}"
CONTAINER_NAME="fastapi-app"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please create a .env file with required variables:"
    echo "  - DATABASE_URL"
    echo "  - SECRET_KEY"
    echo "  - STRIPE_SECRET_KEY"
    echo "  - STRIPE_PUBLISHABLE_KEY"
    echo "  - STRIPE_WEBHOOK_SECRET"
    exit 1
fi

# Load environment variables
source .env

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        echo "Please install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker is installed${NC}"
}

# Function to login to GitHub Container Registry
login_to_registry() {
    echo -e "${YELLOW}🔐 Logging in to GitHub Container Registry...${NC}"
    
    if [ -z "${GITHUB_TOKEN:-}" ]; then
        echo -e "${YELLOW}⚠️  GITHUB_TOKEN not set. Please enter your GitHub personal access token:${NC}"
        read -s GITHUB_TOKEN
    fi
    
    echo "${GITHUB_TOKEN}" | docker login ghcr.io -u "${REPO_OWNER}" --password-stdin
    echo -e "${GREEN}✅ Logged in to GHCR${NC}"
}

# Function to pull latest image
pull_image() {
    local TAG="${1:-latest}"
    echo -e "${YELLOW}📥 Pulling image: ${IMAGE_NAME}:${TAG}${NC}"
    docker pull "${IMAGE_NAME}:${TAG}"
    echo -e "${GREEN}✅ Image pulled successfully${NC}"
}

# Function to stop and remove old container
stop_old_container() {
    echo -e "${YELLOW}🛑 Stopping old container...${NC}"
    docker stop "${CONTAINER_NAME}" 2>/dev/null || true
    docker rm "${CONTAINER_NAME}" 2>/dev/null || true
    echo -e "${GREEN}✅ Old container removed${NC}"
}

# Function to run new container
run_container() {
    local TAG="${1:-latest}"
    echo -e "${YELLOW}🚀 Starting new container...${NC}"
    
    docker run -d \
        --name "${CONTAINER_NAME}" \
        --restart unless-stopped \
        -p 8000:8000 \
        -e DATABASE_URL="${DATABASE_URL}" \
        -e SECRET_KEY="${SECRET_KEY}" \
        -e STRIPE_SECRET_KEY="${STRIPE_SECRET_KEY}" \
        -e STRIPE_PUBLISHABLE_KEY="${STRIPE_PUBLISHABLE_KEY}" \
        -e STRIPE_WEBHOOK_SECRET="${STRIPE_WEBHOOK_SECRET}" \
        "${IMAGE_NAME}:${TAG}"
    
    echo -e "${GREEN}✅ Container started successfully${NC}"
}

# Function to check container health
check_health() {
    echo -e "${YELLOW}🏥 Checking container health...${NC}"
    
    for i in {1..30}; do
        if docker exec "${CONTAINER_NAME}" curl -f http://localhost:8000/health 2>/dev/null; then
            echo -e "${GREEN}✅ App is healthy!${NC}"
            return 0
        fi
        echo "Waiting... ($i/30)"
        sleep 2
    done
    
    echo -e "${RED}❌ Health check failed${NC}"
    echo "Container logs:"
    docker logs "${CONTAINER_NAME}" --tail 50
    return 1
}

# Function to show container status
show_status() {
    echo -e "${GREEN}📊 Container Status:${NC}"
    docker ps -a | grep "${CONTAINER_NAME}" || true
    echo ""
    echo -e "${GREEN}📝 Recent logs:${NC}"
    docker logs "${CONTAINER_NAME}" --tail 20
}

# Function to cleanup old images
cleanup_images() {
    echo -e "${YELLOW}🧹 Cleaning up old images...${NC}"
    docker images "${IMAGE_NAME}" --format '{{.ID}} {{.CreatedAt}}' | \
        sort -rk 2 | \
        tail -n +4 | \
        awk '{print $1}' | \
        xargs -r docker rmi 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Main deployment flow
main() {
    local TAG="${1:-latest}"
    
    echo ""
    echo -e "${GREEN}Starting deployment with tag: ${TAG}${NC}"
    echo ""
    
    check_docker
    login_to_registry
    pull_image "${TAG}"
    stop_old_container
    run_container "${TAG}"
    
    if check_health; then
        show_status
        cleanup_images
        echo ""
        echo -e "${GREEN}🎉 Deployment successful!${NC}"
        echo -e "${GREEN}🌐 API is running at: http://localhost:8000${NC}"
        echo -e "${GREEN}📚 Docs available at: http://localhost:8000/docs${NC}"
    else
        echo -e "${RED}❌ Deployment failed${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
