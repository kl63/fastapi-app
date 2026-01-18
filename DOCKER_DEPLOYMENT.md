# 🐳 Docker Deployment Guide

This guide explains how to deploy your FastAPI app using Docker to avoid OOM (Out of Memory) issues on DigitalOcean.

## 📋 Architecture

```
┌─────────────────┐
│  Your Laptop    │
│                 │
│  git push       │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ GitHub Actions  │
│ (builds image)  │
│                 │
│ docker build    │
│ docker push     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│      GHCR       │
│   (Registry)    │
│                 │
│ Container Image │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ DigitalOcean    │
│    Droplet      │
│                 │
│ docker pull     │
│ docker run      │
└─────────────────┘
```

**Key Principle:** The droplet **NEVER** builds - it only pulls and runs pre-built images.

## 🎯 Benefits

- ✅ **No OOM issues** - Building happens on GitHub's servers, not your droplet
- ✅ **Faster deployments** - Pre-built images deploy in seconds
- ✅ **Consistent environments** - Same image everywhere
- ✅ **Easy rollbacks** - Tag-based versioning
- ✅ **Zero downtime** - Automated health checks

## 🚀 Setup Instructions

### 1️⃣ Prerequisites

#### On Your DigitalOcean Droplet:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (avoid sudo)
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
exit
# Then SSH back in

# Verify Docker installation
docker --version
```

#### On GitHub:

1. Go to your repository settings
2. Navigate to: **Settings → Secrets and variables → Actions**
3. Ensure these secrets exist:
   - `SSH_PRIVATE_KEY` - Your SSH key for the droplet
   - `DATABASE_URL` - PostgreSQL connection string
   - `SECRET_KEY` - JWT secret key
   - `STRIPE_SECRET_KEY` - Stripe API secret
   - `STRIPE_PUBLISHABLE_KEY` - Stripe publishable key
   - `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret

### 2️⃣ Enable GitHub Container Registry (GHCR)

Your images will be automatically pushed to `ghcr.io/YOUR_USERNAME/fastapi-app`.

GitHub Actions has automatic permissions to push to GHCR when using `GITHUB_TOKEN`.

### 3️⃣ Initial Deployment

#### Option A: Automatic (via Git Push)

```bash
# Simply push to main branch
git add .
git commit -m "Enable Docker deployment"
git push origin main

# GitHub Actions will:
# 1. Build the Docker image
# 2. Push to GHCR
# 3. SSH to your droplet
# 4. Pull and run the image
```

#### Option B: Manual (via Workflow Dispatch)

1. Go to: **Actions → Docker Build & Deploy → Run workflow**
2. Click "Run workflow" on the main branch

### 4️⃣ Local Development with Docker

#### Build and Run Locally:

```bash
# Build the image
docker build -t fastapi-app .

# Run with docker-compose (includes PostgreSQL)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop everything
docker-compose down
```

#### Or run just the app (if you have external DB):

```bash
# Create .env file with your variables
cp .env.example .env

# Run the container
docker run -d \
  --name fastapi-app \
  -p 8000:8000 \
  --env-file .env \
  fastapi-app

# View logs
docker logs -f fastapi-app

# Stop container
docker stop fastapi-app
docker rm fastapi-app
```

## 🔄 Deployment Workflow

### Automatic Deployment (Recommended)

Every push to `main` triggers:

1. **Build Phase** (GitHub Actions)
   - Checkout code
   - Build Docker image
   - Tag with branch name and commit SHA
   - Push to GHCR

2. **Deploy Phase** (GitHub Actions → Droplet)
   - SSH to droplet
   - Login to GHCR
   - Pull latest image
   - Stop old container
   - Run new container
   - Health check
   - Cleanup old images

### Manual Deployment (SSH to Droplet)

```bash
# SSH to your droplet
ssh kevinlin192003@134.122.5.11

# Navigate to app directory
cd /var/www/fastapi-app

# Use the deployment script
chmod +x scripts/deploy-docker.sh
./scripts/deploy-docker.sh latest

# Or manually:
# 1. Pull latest image
docker pull ghcr.io/kevinlin192003/fastapi-app:latest

# 2. Stop old container
docker stop fastapi-app
docker rm fastapi-app

# 3. Run new container
docker run -d \
  --name fastapi-app \
  --restart unless-stopped \
  -p 8000:8000 \
  -e DATABASE_URL="your_db_url" \
  -e SECRET_KEY="your_secret" \
  -e STRIPE_SECRET_KEY="your_stripe_key" \
  -e STRIPE_PUBLISHABLE_KEY="your_stripe_pub_key" \
  -e STRIPE_WEBHOOK_SECRET="your_webhook_secret" \
  ghcr.io/kevinlin192003/fastapi-app:latest
```

## 🔍 Monitoring & Debugging

### View Container Status

```bash
# List running containers
docker ps

# View all containers
docker ps -a

# Check container logs
docker logs fastapi-app

# Follow logs in real-time
docker logs -f fastapi-app

# View last 50 lines
docker logs fastapi-app --tail 50
```

### Health Check

```bash
# Check app health
curl http://localhost:8000/health

# Or from outside the droplet
curl https://fastapi.kevinlinportfolio.com/health
```

### Enter Container Shell

```bash
# Execute bash in running container
docker exec -it fastapi-app bash

# Run Python commands
docker exec -it fastapi-app python -c "from app.db.session import engine; print(engine.url)"
```

### Inspect Container

```bash
# View container details
docker inspect fastapi-app

# View resource usage
docker stats fastapi-app

# View port mappings
docker port fastapi-app
```

## 🛠️ Troubleshooting

### Container Won't Start

```bash
# View full logs
docker logs fastapi-app

# Check if port is already in use
sudo lsof -i :8000

# Remove and recreate
docker stop fastapi-app
docker rm fastapi-app
./scripts/deploy-docker.sh latest
```

### Database Connection Issues

```bash
# Test database connectivity from container
docker exec fastapi-app python -c "
from sqlalchemy import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    print('Connected!')
"
```

### Image Pull Fails

```bash
# Login to GHCR manually
echo "YOUR_GITHUB_TOKEN" | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Pull specific tag
docker pull ghcr.io/kevinlin192003/fastapi-app:main-abc123
```

### Out of Disk Space

```bash
# Remove unused images
docker image prune -a

# Remove unused containers
docker container prune

# Remove everything unused
docker system prune -a

# Check disk usage
docker system df
```

## 📦 Image Tags

Images are tagged with:

- `latest` - Latest build from main branch
- `main` - Latest main branch build
- `main-<commit-sha>` - Specific commit (e.g., `main-abc123def`)

### Deploy Specific Version

```bash
# Deploy specific commit
./scripts/deploy-docker.sh main-abc123def

# Rollback to previous version
docker images ghcr.io/kevinlin192003/fastapi-app
./scripts/deploy-docker.sh main-<previous-sha>
```

## 🔐 Security Best Practices

1. **Never commit secrets** - Use GitHub Secrets and .env files
2. **Use multi-stage builds** - Smaller, more secure images
3. **Run as non-root** - Consider adding USER in Dockerfile
4. **Keep images updated** - Regularly rebuild with latest base images
5. **Scan for vulnerabilities** - Use `docker scan` or GitHub security features

## 📊 Resource Management

### Set Container Limits (Optional)

```bash
docker run -d \
  --name fastapi-app \
  --restart unless-stopped \
  -p 8000:8000 \
  --memory="512m" \
  --cpus="1.0" \
  --env-file .env \
  ghcr.io/kevinlin192003/fastapi-app:latest
```

## 🎯 Production Checklist

- [ ] Docker installed on droplet
- [ ] GitHub secrets configured
- [ ] Initial deployment successful
- [ ] Health check endpoint responding
- [ ] Database migrations running
- [ ] Nginx reverse proxy configured (if applicable)
- [ ] SSL/TLS certificates installed
- [ ] Monitoring set up
- [ ] Backup strategy in place

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Docker Compose](https://docs.docker.com/compose/)

## 🆘 Support

If you encounter issues:

1. Check container logs: `docker logs fastapi-app`
2. Verify environment variables are set
3. Check GitHub Actions workflow logs
4. Test health endpoint: `curl http://localhost:8000/health`
5. Review this documentation

---

**Happy Deploying! 🚀**
