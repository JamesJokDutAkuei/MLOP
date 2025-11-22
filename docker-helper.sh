#!/bin/bash

# Docker Helper Script for MLOP
# Usage: ./docker-helper.sh [command]

set -e

PROJECT_DIR="/Users/apple/MLOP"
cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
print_banner() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}   🐳 MLOP Docker Helper${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_status() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker Desktop"
        echo "Visit: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    print_status "Docker is installed"
}

build_images() {
    print_banner
    print_info "Building Docker images (this may take 2-3 minutes)..."
    echo ""
    docker compose build --no-cache
    print_status "Docker images built successfully!"
}

start_services() {
    print_banner
    print_info "Starting services..."
    echo ""
    docker compose up -d
    echo ""
    sleep 3
    print_status "Services starting..."
    echo ""
    docker compose ps
    echo ""
    print_status "Services started!"
    echo ""
    echo -e "${YELLOW}Access points:${NC}"
    echo "  UI:        http://localhost:8501"
    echo "  API:       http://localhost:80"
    echo "  API Docs:  http://localhost/docs"
    echo ""
}

stop_services() {
    print_banner
    print_info "Stopping services..."
    docker compose down
    print_status "Services stopped"
}

restart_services() {
    print_banner
    print_info "Restarting services..."
    docker compose restart
    sleep 2
    docker compose ps
    print_status "Services restarted"
}

view_logs() {
    print_banner
    if [ -z "$1" ]; then
        print_info "Viewing all logs (Ctrl+C to exit)..."
        docker compose logs -f
    else
        print_info "Viewing logs for $1 (Ctrl+C to exit)..."
        docker compose logs -f "$1"
    fi
}

check_status() {
    print_banner
    print_info "Service Status:"
    echo ""
    docker compose ps
    echo ""
    print_info "Health Check:"
    echo ""
    if curl -s http://localhost/health > /dev/null 2>&1; then
        print_status "API is healthy"
        curl -s http://localhost/health | python3 -m json.tool
    else
        print_error "API is not responding"
    fi
}

clean_all() {
    print_banner
    print_info "Cleaning Docker resources..."
    docker compose down -v
    docker system prune -a
    print_status "Docker system cleaned"
}

test_api() {
    print_banner
    print_info "Testing API endpoints..."
    echo ""
    
    echo -e "${YELLOW}1. Health Check:${NC}"
    curl -s http://localhost/health | python3 -m json.tool
    echo ""
    
    echo -e "${YELLOW}2. API Documentation:${NC}"
    print_info "Available at: http://localhost/docs"
    echo ""
}

show_help() {
    cat << EOF
${BLUE}MLOP Docker Helper${NC}

Usage: ./docker-helper.sh [command]

Commands:
  ${GREEN}build${NC}         Build Docker images
  ${GREEN}start${NC}         Start all services (background)
  ${GREEN}stop${NC}          Stop all services
  ${GREEN}restart${NC}       Restart all services
  ${GREEN}logs${NC}          View logs (all services)
  ${GREEN}logs <service>${NC} View logs for specific service
  ${GREEN}status${NC}        Check service status
  ${GREEN}test${NC}          Test API endpoints
  ${GREEN}clean${NC}         Remove all Docker resources
  ${GREEN}help${NC}          Show this help message

Examples:
  ./docker-helper.sh build       # Build images
  ./docker-helper.sh start       # Start all services
  ./docker-helper.sh logs api_1  # View API 1 logs
  ./docker-helper.sh status      # Check status

${YELLOW}Access Points:${NC}
  Web UI:        http://localhost:8501
  API Endpoint:  http://localhost/80
  API Docs:      http://localhost/docs

EOF
}

# Main
case "${1:-help}" in
    build)
        check_docker
        build_images
        ;;
    start)
        check_docker
        start_services
        ;;
    stop)
        check_docker
        stop_services
        ;;
    restart)
        check_docker
        restart_services
        ;;
    logs)
        check_docker
        view_logs "$2"
        ;;
    status)
        check_docker
        check_status
        ;;
    test)
        check_docker
        test_api
        ;;
    clean)
        check_docker
        read -p "Are you sure? This will remove all containers and images (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            clean_all
        fi
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
