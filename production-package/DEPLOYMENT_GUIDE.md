# Deployment Guide - FashionGo Email Scraper

## Quick Start Deployment

### Option 1: Railway (Recommended - Free Tier Available)

1. **Create Railway Account**
   - Go to [Railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from Repository**
   ```bash
   # Push this production-package to a Git repository
   git init
   git add .
   git commit -m "FashionGo Email Scraper - Production Ready"
   git remote add origin YOUR_REPOSITORY_URL
   git push -u origin main
   ```

3. **Connect to Railway**
   - Create new project in Railway
   - Connect GitHub repository
   - Railway will auto-detect Python app and deploy using `railway.json`

4. **Verify Deployment**
   - Check deployment logs
   - Visit `/health` endpoint
   - Test with sample Excel file

### Option 2: Render (Free Tier)

1. **Create Render Account**
   - Go to [Render.com](https://render.com)
   - Sign up with GitHub

2. **Create Web Service**
   - New → Web Service
   - Connect repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`

3. **Environment Variables**
   - `PORT`: Auto-provided by Render
   - `PYTHON_VERSION`: 3.11.0

### Option 3: Heroku

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Windows/Linux - download from heroku.com
   ```

2. **Deploy**
   ```bash
   heroku create your-app-name
   git push heroku main
   heroku open
   ```

3. **Scale Dynos**
   ```bash
   heroku ps:scale web=1
   ```

### Option 4: DigitalOcean App Platform

1. **Create App**
   - Go to DigitalOcean Apps
   - Create App from GitHub repository

2. **Configure**
   - Runtime: Python 3.11
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `gunicorn --bind 0.0.0.0:$PORT app:app`

## Docker Deployment

### Build and Run Locally
```bash
# Build image
docker build -t fashiongo-scraper .

# Run container
docker run -p 5000:5000 fashiongo-scraper

# Access at http://localhost:5000
```

### Docker Compose (with Redis for future scaling)
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - PORT=5000
    restart: unless-stopped
    
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

### Deploy to Docker Hub
```bash
# Build and tag
docker build -t yourusername/fashiongo-scraper:latest .

# Push to Docker Hub
docker push yourusername/fashiongo-scraper:latest

# Deploy anywhere
docker run -p 5000:5000 yourusername/fashiongo-scraper:latest
```

## Cloud Platform Specific Configuration

### AWS Elastic Beanstalk

1. **Create application.py**
   ```python
   from app import app
   application = app
   
   if __name__ == "__main__":
       application.run()
   ```

2. **Deploy**
   ```bash
   eb init
   eb create production
   eb deploy
   ```

### Google Cloud Run

1. **Deploy**
   ```bash
   gcloud run deploy fashiongo-scraper \
       --source . \
       --platform managed \
       --region us-central1 \
       --allow-unauthenticated
   ```

2. **Scale Configuration**
   ```bash
   gcloud run services update fashiongo-scraper \
       --memory 1Gi \
       --cpu 1 \
       --max-instances 10
   ```

### Azure Container Instances

1. **Create Resource Group**
   ```bash
   az group create --name fashiongo-rg --location eastus
   ```

2. **Deploy Container**
   ```bash
   az container create \
       --resource-group fashiongo-rg \
       --name fashiongo-scraper \
       --image yourusername/fashiongo-scraper:latest \
       --ports 5000 \
       --environment-variables PORT=5000
   ```

## Production Configuration

### Environment Variables
```bash
# Required
PORT=5000                    # Server port

# Optional (for enhanced features)
REDIS_URL=redis://localhost:6379  # For caching
LOG_LEVEL=INFO              # Logging level
MAX_COMPANIES=100           # Processing limit
TIMEOUT_SECONDS=120         # Request timeout
```

### Resource Requirements

#### Minimum (Development)
- **Memory**: 512MB RAM
- **CPU**: 0.5 vCPU
- **Storage**: 1GB
- **Network**: 1Mbps

#### Recommended (Production)
- **Memory**: 1GB RAM
- **CPU**: 1 vCPU  
- **Storage**: 5GB
- **Network**: 10Mbps

#### Enterprise (High Volume)
- **Memory**: 2GB RAM
- **CPU**: 2 vCPU
- **Storage**: 10GB
- **Network**: 100Mbps
- **Load Balancer**: Yes
- **Auto-scaling**: Yes

### Health Check Configuration

#### Railway/Render
```json
{
  "healthcheckPath": "/health",
  "healthcheckTimeout": 30
}
```

#### Docker
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:$PORT/health || exit 1
```

#### Kubernetes
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 30
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Monitoring Setup

### Basic Monitoring (Free)

1. **Health Check Monitoring**
   ```bash
   # Simple uptime monitoring
   curl -f https://your-app.herokuapp.com/health
   ```

2. **Log Monitoring**
   ```bash
   # Heroku logs
   heroku logs --tail
   
   # Docker logs
   docker logs -f container_name
   ```

### Advanced Monitoring

1. **Application Performance Monitoring (APM)**
   - New Relic (free tier available)
   - DataDog (free tier available)
   - Sentry for error tracking

2. **Custom Metrics**
   ```python
   # Add to app.py for monitoring
   import time
   from functools import wraps
   
   def track_processing_time(f):
       @wraps(f)
       def decorated_function(*args, **kwargs):
           start_time = time.time()
           result = f(*args, **kwargs)
           end_time = time.time()
           logger.info(f"Processing time: {end_time - start_time:.2f}s")
           return result
       return decorated_function
   ```

## Performance Optimization

### Database Integration (Optional)
```python
# For caching website discovery results
import redis

redis_client = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))

def cached_website_search(company_name):
    cache_key = f"website:{company_name}"
    cached_result = redis_client.get(cache_key)
    
    if cached_result:
        return cached_result.decode()
    
    result = search_for_website(company_name)
    if result:
        redis_client.setex(cache_key, 3600, result)  # Cache for 1 hour
    
    return result
```

### Load Balancing Setup
```yaml
# nginx.conf for load balancing
upstream fashiongo_app {
    server app1:5000;
    server app2:5000;
    server app3:5000;
}

server {
    listen 80;
    location / {
        proxy_pass http://fashiongo_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Security Hardening

### Production Security Checklist

- [ ] Enable HTTPS (SSL/TLS)
- [ ] Set secure headers
- [ ] Implement rate limiting
- [ ] Add authentication (if needed)
- [ ] Validate all inputs
- [ ] Enable CORS properly
- [ ] Monitor for suspicious activity

### Security Headers
```python
from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)

# Force HTTPS and security headers
Talisman(app, force_https=True)

@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

## Troubleshooting

### Common Issues

1. **Memory Errors**
   ```
   Solution: Increase memory allocation to 1GB+
   Check: Docker memory limits, platform resource settings
   ```

2. **Timeout Errors**
   ```
   Solution: Increase timeout settings
   railway.json: "healthcheckTimeout": 60
   gunicorn: --timeout 180
   ```

3. **Import Errors**
   ```
   Solution: Verify requirements.txt versions
   Check: Python version compatibility (3.11+)
   ```

4. **Port Binding Issues**
   ```
   Solution: Ensure PORT environment variable is set
   Check: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
   ```

### Debug Commands
```bash
# Test local deployment
python app.py

# Check health endpoint
curl http://localhost:5000/health

# View logs
heroku logs --tail  # Heroku
docker logs -f container_name  # Docker

# Check memory usage
docker stats  # Docker
heroku ps  # Heroku
```

## Backup and Recovery

### Data Backup
```bash
# Backup processing results (if stored)
heroku pg:backups:capture --app your-app
```

### Application Backup
```bash
# Version control
git tag v1.0-production
git push origin v1.0-production

# Docker image backup
docker save fashiongo-scraper:latest | gzip > backup.tar.gz
```

### Recovery Procedures
1. **Rollback**: Deploy previous version
2. **Scale down**: Reduce resource usage if needed
3. **Health check**: Verify all endpoints work
4. **Data verification**: Test with known company samples

---

**Production Deployment Status**: ✅ Ready for immediate deployment on any major cloud platform 