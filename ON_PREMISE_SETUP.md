# ComChat On-Premise Deployment Guide

This guide covers deploying ComChat in your own infrastructure for maximum security, privacy, and control.

## 🎯 Overview

On-premise deployment provides:
- **Complete data control**: All data stays within your infrastructure
- **Enhanced security**: No external API dependencies (when using local models)
- **Customization**: Full control over configuration and integrations
- **Compliance**: Meet strict regulatory requirements (GDPR, HIPAA, SOC2)
- **Cost predictability**: No per-message or per-token costs

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Web Servers   │    │   AI Models     │
│   (Nginx)       │◄──►│   (FastAPI)     │◄──►│   (Ollama)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Database      │    │   Vector DB     │
│   (React)       │    │   (PostgreSQL)  │    │   (Qdrant)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

### Hardware Requirements

**Minimum (Testing)**
- CPU: 4 cores
- RAM: 16GB
- Storage: 100GB SSD
- Network: 1Gbps

**Recommended (Production)**
- CPU: 8+ cores (16+ for high traffic)
- RAM: 32GB+ (64GB+ for large models)
- Storage: 500GB+ NVMe SSD
- Network: 10Gbps
- GPU: RTX 3090/4090 or A100 (for faster AI inference)

### Software Requirements

- Docker 24.0+
- Docker Compose v2.0+
- Linux (Ubuntu 22.04+ LTS recommended)
- SSL certificates (Let's Encrypt or custom)

## 🚀 Quick Deploy

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Download ComChat

```bash
# Clone repository
git clone https://github.com/your-org/comchat.git
cd comchat

# Or download release
wget https://github.com/your-org/comchat/releases/download/v1.0.0/comchat-onprem.tar.gz
tar -xzf comchat-onprem.tar.gz
cd comchat
```

### 3. Configuration

```bash
# Copy environment template
cp .env.onprem.example .env

# Generate secure passwords
./scripts/generate-secrets.sh

# Edit configuration
nano .env
```

### 4. Launch Platform

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 5. Initialize System

```bash
# Install local AI models
docker exec comchat_ollama ollama pull mistral:latest
docker exec comchat_ollama ollama pull llava:latest

# Create admin user
docker exec comchat_backend python scripts/create_admin.py

# Apply database migrations
docker exec comchat_backend alembic upgrade head
```

## ⚙️ Configuration

### Environment Variables

```bash
# Core Configuration
ENVIRONMENT=production
SECRET_KEY=your-super-secret-key-256-bits
DEBUG=false

# Database
POSTGRES_DB=comchat
POSTGRES_USER=comchat_user
POSTGRES_PASSWORD=secure-db-password
DATABASE_URL=postgresql://comchat_user:secure-db-password@postgres:5432/comchat

# Redis
REDIS_PASSWORD=secure-redis-password
REDIS_URL=redis://:secure-redis-password@redis:6379

# Local AI Models (Recommended for on-premise)
LOCAL_MODEL_ENABLED=true
OLLAMA_BASE_URL=http://ollama:11434

# External AI (Optional)
OPENAI_API_KEY=your-openai-key-optional

# Security
CORS_ORIGINS=["https://your-domain.com"]
TRUSTED_HOSTS=["your-domain.com"]

# SSL/TLS
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/private.key

# Monitoring
GRAFANA_PASSWORD=secure-grafana-password
PROMETHEUS_RETENTION=30d

# Backup
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
BACKUP_S3_BUCKET=comchat-backups
BACKUP_S3_ACCESS_KEY=your-s3-access-key
BACKUP_S3_SECRET_KEY=your-s3-secret-key
```

### SSL/TLS Setup

```bash
# Using Let's Encrypt
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./nginx/ssl/private.key

# Or use custom certificates
cp your-cert.pem ./nginx/ssl/cert.pem
cp your-private-key.pem ./nginx/ssl/private.key
```

### Resource Limits

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
  
  ollama:
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
        reservations:
          memory: 4G
          cpus: '2.0'
```

## 🔒 Security Hardening

### 1. Network Security

```bash
# Configure firewall
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 5432/tcp   # Block external DB access
sudo ufw deny 6379/tcp   # Block external Redis access
```

### 2. Application Security

```bash
# Rotate secrets regularly
./scripts/rotate-secrets.sh

# Enable audit logging
echo "AUDIT_LOG_ENABLED=true" >> .env

# Configure rate limiting
echo "RATE_LIMIT_PER_MINUTE=100" >> .env
echo "RATE_LIMIT_PER_HOUR=5000" >> .env
```

### 3. Data Encryption

```yaml
# Enable encryption at rest
postgres:
  command: postgres -c ssl=on -c ssl_cert_file=/var/lib/postgresql/server.crt
  volumes:
    - ./ssl/postgres.crt:/var/lib/postgresql/server.crt
    - ./ssl/postgres.key:/var/lib/postgresql/server.key
```

## 📊 Monitoring & Observability

### Access Monitoring Dashboards

- **Grafana**: https://your-domain.com:3000 (admin/your-password)
- **Prometheus**: https://your-domain.com:9090
- **Application Logs**: `docker-compose logs -f backend`

### Key Metrics to Monitor

- **Response Time**: Average API response time
- **Throughput**: Requests per second
- **Error Rate**: Failed requests percentage
- **Resource Usage**: CPU, Memory, Disk, Network
- **AI Model Performance**: Inference time, accuracy
- **Database Performance**: Query time, connections

### Alerts Configuration

```yaml
# monitoring/alerts.yml
groups:
- name: comchat-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    labels:
      severity: critical
    annotations:
      summary: High error rate detected
      
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5
    labels:
      severity: warning
    annotations:
      summary: High response time detected
```

## 🔄 Backup & Recovery

### Automated Backups

```bash
# The backup service runs automatically
# Manual backup
docker exec comchat_backup /app/backup.sh

# Restore from backup
docker exec comchat_backup /app/restore.sh backup-2024-01-01.tar.gz
```

### Backup Strategy

- **Database**: Daily PostgreSQL dumps
- **Files**: Application files and uploads
- **Configuration**: Environment and config files
- **Retention**: 30 days local, 1 year offsite

## 🔧 Maintenance

### Updates

```bash
# Download latest release
wget https://github.com/your-org/comchat/releases/download/v1.1.0/comchat-onprem.tar.gz

# Backup current version
./scripts/backup-before-update.sh

# Update
./scripts/update-to-version.sh v1.1.0

# Rollback if needed
./scripts/rollback-version.sh
```

### Health Checks

```bash
# Check all services
./scripts/health-check.sh

# Individual service checks
curl -f http://localhost:8000/health
docker exec comchat_postgres pg_isready
docker exec comchat_redis redis-cli ping
```

## 🎛️ Advanced Configuration

### GPU Support for AI Models

```yaml
# docker-compose.prod.yml
ollama:
  runtime: nvidia
  environment:
    - NVIDIA_VISIBLE_DEVICES=all
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

### High Availability Setup

```yaml
# Multiple backend instances
backend:
  deploy:
    replicas: 3
    placement:
      constraints:
        - node.role == worker
    restart_policy:
      condition: on-failure
      delay: 5s
      max_attempts: 3
```

### Database Clustering

```bash
# PostgreSQL Primary-Replica setup
# See ./postgres/setup-replication.sh
./scripts/setup-postgres-cluster.sh
```

## 📞 Support & Troubleshooting

### Common Issues

1. **Out of Memory**: Increase system RAM or reduce model sizes
2. **Slow AI Responses**: Add GPU support or use smaller models
3. **SSL Certificate Errors**: Check certificate paths and permissions
4. **Database Connection Issues**: Verify credentials and network

### Log Analysis

```bash
# Application logs
docker-compose logs backend | grep ERROR

# System logs
journalctl -u docker.service

# Performance logs
docker stats

# Network logs
docker network inspect comchat_comchat_network
```

### Performance Tuning

```bash
# Database optimization
docker exec comchat_postgres psql -U comchat_user -d comchat -f ./postgres/optimize.sql

# Redis optimization
docker exec comchat_redis redis-cli CONFIG SET maxmemory 2gb
docker exec comchat_redis redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Application optimization
echo "WORKER_COUNT=8" >> .env
echo "MAX_CONNECTIONS=100" >> .env
```

## 📋 Compliance & Auditing

### GDPR Compliance

- **Data Retention**: Configure automatic deletion policies
- **Data Export**: Built-in data export functionality
- **Audit Logs**: Complete audit trail of data access
- **Encryption**: Data encrypted at rest and in transit

### SOC2 Compliance

- **Access Control**: Role-based access control (RBAC)
- **Monitoring**: Comprehensive logging and monitoring
- **Backup**: Automated backup and recovery procedures
- **Incident Response**: Built-in alerting and notification system

---

**Need help?** Contact our enterprise support team or check the [troubleshooting guide](TROUBLESHOOTING.md).