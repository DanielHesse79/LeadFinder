# LeadFinder Deployment Guide

## Overview

This guide covers deploying LeadFinder in various environments, from local development to production servers.

## Prerequisites

### System Requirements
- **Python 3.8+** (3.12 recommended)
- **Ollama** for AI functionality
- **SQLite** (included with Python)
- **4GB+ RAM** (8GB+ recommended for AI models)
- **2GB+ disk space** for models and data

### Software Dependencies
- **Ollama** - Local AI server
- **Python packages** (see requirements.txt)
- **Web server** (optional: nginx, Apache)

## Local Development Deployment

### 1. Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd leadfinder

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy and edit configuration
cp config.py config_local.py

# Set environment variables
export SERPAPI_KEY="your_api_key_here"
export FLASK_ENV="development"
```

### 3. Start Services

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start LeadFinder
python app.py
```

### 4. Access Application
- **Web Interface**: http://localhost:5050
- **Ollama API**: http://localhost:11434

## Production Server Deployment

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Create application user
sudo useradd -m -s /bin/bash leadfinder
sudo usermod -aG sudo leadfinder
```

### 2. Application Setup

```bash
# Switch to application user
sudo su - leadfinder

# Clone application
git clone <repository-url> /home/leadfinder/app
cd /home/leadfinder/app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install production dependencies
pip install gunicorn
```

### 3. Configuration

```bash
# Create production config
cp config.py config_prod.py

# Edit configuration for production
nano config_prod.py
```

**Production Configuration:**
```python
# Production settings
FLASK_DEBUG = False
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5050

# Secure file paths
EXPORT_FOLDER = '/home/leadfinder/exports'
SCIHUB_FOLDER = '/home/leadfinder/scihub'

# Environment variables
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
```

### 4. Systemd Service Setup

```bash
# Create systemd service file
sudo nano /etc/systemd/system/leadfinder.service
```

**Service Configuration:**
```ini
[Unit]
Description=LeadFinder Web Application
After=network.target

[Service]
Type=simple
User=leadfinder
WorkingDirectory=/home/leadfinder/app
Environment=PATH=/home/leadfinder/app/venv/bin
Environment=SERPAPI_KEY=your_api_key_here
ExecStart=/home/leadfinder/app/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5050 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5. Start Services

```bash
# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable leadfinder
sudo systemctl start leadfinder

# Check status
sudo systemctl status leadfinder
```

### 6. Nginx Reverse Proxy (Optional)

```bash
# Install nginx
sudo apt install nginx -y

# Create nginx configuration
sudo nano /etc/nginx/sites-available/leadfinder
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static file serving
    location /static {
        alias /home/leadfinder/app/static;
        expires 30d;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/leadfinder /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Docker Deployment

### 1. Dockerfile

```dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /app/exports /app/scihub

# Expose ports
EXPOSE 5050 11434

# Start script
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
```

### 2. Start Script

```bash
#!/bin/bash
# start.sh

# Start Ollama in background
ollama serve &

# Wait for Ollama to start
sleep 10

# Pull default model
ollama pull mistral:latest

# Start Flask application
python app.py
```

### 3. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  leadfinder:
    build: .
    ports:
      - "5050:5050"
      - "11434:11434"
    environment:
      - SERPAPI_KEY=${SERPAPI_KEY}
    volumes:
      - ./exports:/app/exports
      - ./scihub:/app/scihub
      - ./leads.db:/app/leads.db
    restart: unless-stopped
```

### 4. Build and Run

```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Cloud Deployment

### AWS EC2

```bash
# Launch EC2 instance (t3.medium or larger)
# Connect via SSH

# Install dependencies
sudo yum update -y
sudo yum install python3 python3-pip git -y

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Clone and setup application
git clone <repository-url>
cd leadfinder
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure security groups
# - Port 22 (SSH)
# - Port 80 (HTTP)
# - Port 443 (HTTPS)
# - Port 5050 (LeadFinder)

# Start application
python app.py
```

### Google Cloud Platform

```bash
# Create VM instance
gcloud compute instances create leadfinder \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=debian-11 \
  --image-project=debian-cloud

# Connect and setup
gcloud compute ssh leadfinder

# Install and configure as above
```

### DigitalOcean Droplet

```bash
# Create droplet with Ubuntu 22.04
# Connect via SSH

# Install dependencies
sudo apt update
sudo apt install python3 python3-pip git -y

# Setup application as above
```

## Monitoring and Maintenance

### 1. Log Management

```bash
# View application logs
sudo journalctl -u leadfinder -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Database Backup

```bash
# Create backup script
nano /home/leadfinder/backup.sh
```

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
cp /home/leadfinder/app/leads.db /home/leadfinder/backups/leads_$DATE.db
```

### 3. Health Checks

```bash
# Check application status
curl http://localhost:5050/ollama_status

# Check Ollama models
curl http://localhost:11434/api/tags
```

### 4. Updates

```bash
# Update application
cd /home/leadfinder/app
git pull
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart leadfinder
```

## Security Considerations

### 1. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. SSL/TLS Setup

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 3. Environment Variables

```bash
# Store sensitive data in environment
export SERPAPI_KEY="your_key"
export FLASK_SECRET_KEY="your_secret"
```

## Troubleshooting

### Common Issues

1. **Ollama not responding**
   ```bash
   # Check if Ollama is running
   systemctl status ollama
   
   # Restart Ollama
   sudo systemctl restart ollama
   ```

2. **Port already in use**
   ```bash
   # Find process using port
   sudo netstat -tulpn | grep :5050
   
   # Kill process
   sudo kill -9 <PID>
   ```

3. **Permission errors**
   ```bash
   # Fix file permissions
   sudo chown -R leadfinder:leadfinder /home/leadfinder/app
   sudo chmod -R 755 /home/leadfinder/app
   ```

### Performance Optimization

1. **Increase workers**
   ```bash
   # Edit gunicorn workers
   --workers 8 --bind 0.0.0.0:5050
   ```

2. **Database optimization**
   ```sql
   -- Add indexes
   CREATE INDEX idx_leads_source ON leads(source);
   CREATE INDEX idx_leads_created ON leads(created_at);
   ```

3. **Caching**
   ```python
   # Add Redis caching
   pip install redis flask-caching
   ```

## Support

For deployment issues:
- Check application logs
- Verify all services are running
- Ensure proper network configuration
- Review security group/firewall settings 