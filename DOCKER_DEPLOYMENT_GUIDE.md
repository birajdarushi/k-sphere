# K-Sphere Docker Deployment Guide

This guide explains how to deploy K-Sphere using pre-built Docker images from Docker Hub.

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB of available RAM (recommended 8GB+)
- Internet connection for downloading models

## Quick Start

### 1. Download the deployment files

```bash
# Create a new directory for K-Sphere
mkdir k-sphere-deployment
cd k-sphere-deployment

# Download the production docker-compose file
curl -O https://raw.githubusercontent.com/birajdarushi/k-sphere/main/docker-compose.production.yml

# Rename it for convenience
mv docker-compose.production.yml docker-compose.yml
```

### 2. Update the Docker Hub username

Edit the `docker-compose.yml` file and replace `YOUR_DOCKERHUB_USERNAME` with the actual Docker Hub username where the images are hosted.

### 3. Start the services

```bash
# Pull the latest images and start services
docker-compose pull
docker-compose up -d

# Check status
docker-compose ps
```

### 4. Download AI models

The system will automatically download the required AI models on first startup. This may take several minutes.

```bash
# Monitor the download progress
docker-compose logs -f ollama

# Once Ollama is ready, download the models
docker-compose exec ollama ollama pull phi3.5:latest
docker-compose exec ollama ollama pull nomic-embed-text
```

### 5. Access the application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Troubleshooting

### Memory Issues

If you encounter memory errors:

1. Use a smaller model:
   ```bash
   docker-compose exec ollama ollama pull llama3.2:1b
   ```
   Then update the `LLM_MODEL` environment variable in docker-compose.yml to `llama3.2:1b`

2. Restart the backend:
   ```bash
   docker-compose restart backend
   ```

### Checking Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs ollama
```

### Reset Everything

```bash
# Stop and remove containers and volumes
docker-compose down -v

# Remove downloaded models (optional)
docker volume rm k-sphere-deployment_ollama_data

# Start fresh
docker-compose up -d
```

## Configuration

### Environment Variables

You can customize the deployment by modifying these environment variables in `docker-compose.yml`:

- `LLM_MODEL`: The language model to use (default: phi3.5:latest)
- `EMBEDDING_MODEL`: The embedding model for document processing (default: nomic-embed-text)
- `NEXT_PUBLIC_BACKEND_URL`: Backend URL for the frontend (default: http://backend:8000)

### Persistent Data

The following data is persisted in Docker volumes:

- `ollama_data`: Downloaded AI models
- `backend_data`: Uploaded files and vector database
- `backend_logs`: Application logs

## Security Notes

- Change default ports if needed
- Set up SSL/TLS for production use
- Configure firewall rules appropriately
- Consider using Docker secrets for sensitive environment variables

## Updates

To update to the latest version:

```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose up -d
```

## Support

For issues and support, please check:
- Application logs: `docker-compose logs`
- GitHub repository issues
- Docker Hub image pages