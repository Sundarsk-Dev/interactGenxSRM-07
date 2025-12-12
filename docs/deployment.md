# Deployment Guide

## Local Development (Docker)

1. **Build and Run:**
   ```bash
   docker-compose up --build
   ```
2. **Access:**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - API: http://localhost:8000

## Kubernetes / Production

1. **Build Images:**
   ```bash
   docker build -t interactgen-api -f Dockerfile.api .
   docker build -t interactgen-frontend -f Dockerfile.frontend .
   ```
2. **Push to Registry:**
   - Push to ECR/GCR/DockerHub.
3. **Apply manifests:**
   - Create `deployment.yaml` and `service.yaml` for both API and Frontend.
   - Ensure `storage` volume is mounted (PVC).
