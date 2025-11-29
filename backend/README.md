# Cyber HealthGuard AI - Backend API

A multi-tenant healthcare cybersecurity platform with AI-powered threat detection, built with FastAPI, MongoDB, and machine learning.

## 🌟 Features

### Core Capabilities
- **📥 Log Ingestion**: Ingest security logs from endpoints, SIEM, EDR, and other sources
- **🤖 AI/ML Anomaly Detection**: Isolation Forest-based anomaly detection with per-organisation models
- **📋 Rule-Based Detection**: Pre-configured rules for common attack patterns (failed logins, suspicious processes, etc.)
- **🚨 Alert Management**: Create, view, filter, and manage security alerts
- **📊 Risk Assessment**: Automatic endpoint risk scoring based on alerts and anomalies
- **✅ Compliance Monitoring**: HIPAA security control assessment and scoring
- **🏢 Multi-Tenancy**: Organisation-based data isolation with header-based authentication

### ML/AI Features
The anomaly detection system:
- Extracts numeric features from log events (temporal, behavioral, contextual)
- Maintains per-organisation Isolation Forest models
- Automatically trains models when sufficient data is available
- Scores events and creates alerts for anomalies exceeding threshold
- Considers historical context (failed login counts, event patterns, etc.)

### Rule-Based Detection
Built-in detection rules:
- **Failed Login Threshold**: Multiple failed login attempts
- **Suspicious Processes**: Known attack tools (mimikatz, psexec, encoded PowerShell, etc.)
- **Off-Hours Access**: Access during nights and weekends
- **Multiple Host Access**: User accessing many hosts in short timeframe

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)

### Option 1: Docker Compose (Recommended)

```bash
# Navigate to backend directory
cd backend

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# API will be available at http://localhost:8000
```

### Option 2: Local Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start MongoDB (separate terminal)
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# Run the API
uvicorn app.main:app --reload

# API will be available at http://localhost:8000
```

## 📚 API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Authentication

All API requests require the `X-Org-Id` header with your organisation ID:

```bash
curl -H "X-Org-Id: org_001" http://localhost:8000/alerts
```

## 📡 API Endpoints

### Log Ingestion
- `POST /ingest/logs` - Ingest a log event with automatic threat detection

### Alerts
- `GET /alerts` - List alerts (paginated, filterable)
- `GET /alerts/{alert_id}` - Get specific alert
- `PATCH /alerts/{alert_id}` - Update alert status/add comment

### Endpoints
- `GET /endpoints` - List endpoints with risk metrics

### Compliance
- `GET /compliance` - Get compliance score and control status

### Health
- `GET /health` - API health check

## 🧪 Testing with Seed Data

Generate fake log data to test the platform:

```bash
# Install requests library
pip install requests

# Run seed script
python scripts/seed_data.py
```

This will:
- Generate 200 log events (normal, suspicious, and anomalous)
- Create alerts based on rules and anomalies
- Populate endpoints and risk data
- Calculate compliance scores

### Quick Test Script

```bash
# Make test script executable
chmod +x scripts/test_api.sh

# Run tests
./scripts/test_api.sh
```

## 📊 Example Usage

### 1. Ingest a Log Event

```bash
curl -X POST "http://localhost:8000/ingest/logs" \
  -H "X-Org-Id: org_001" \
  -H "Content-Type: application/json" \
  -d '{
    "organisation_id": "org_001",
    "host": "WKS-001",
    "user": "john.doe",
    "event_type": "login",
    "source": "ActiveDirectory",
    "details": {
      "success": false,
      "ip_address": "192.168.1.100",
      "failure_reason": "Invalid credentials"
    }
  }'
```

### 2. Get Alerts

```bash
curl -H "X-Org-Id: org_001" "http://localhost:8000/alerts?page=1&page_size=10"
```

### 3. Update Alert

```bash
curl -X PATCH "http://localhost:8000/alerts/alert_abc123" \
  -H "X-Org-Id: org_001" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "comment": "Investigating with user"
  }'
```

### 4. Get Endpoints with Risk Scores

```bash
curl -H "X-Org-Id: org_001" "http://localhost:8000/endpoints"
```

### 5. Get Compliance Status

```bash
curl -H "X-Org-Id: org_001" "http://localhost:8000/compliance"
```

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── database.py             # MongoDB connection
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── routers/
│   │   ├── logs.py             # Log ingestion endpoints
│   │   ├── alerts.py           # Alert management endpoints
│   │   ├── endpoints.py        # Endpoint risk endpoints
│   │   └── compliance.py       # Compliance endpoints
│   ├── services/
│   │   ├── anomaly_detection.py # ML anomaly detection
│   │   ├── rule_engine.py       # Rule-based detection
│   │   ├── risk_scoring.py      # Risk calculation
│   │   └── compliance.py        # Compliance assessment
│   └── utils/
│       └── auth.py             # Authentication utilities
├── scripts/
│   ├── seed_data.py            # Data seeding script
│   └── test_api.sh             # API test script
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

Configuration is managed through environment variables. Copy `.env.example` to `.env` and modify as needed:

```bash
cp .env.example .env
```

Key settings:
- `MONGODB_URL`: MongoDB connection string
- `ANOMALY_THRESHOLD`: Threshold for anomaly detection (0-1)
- `FAILED_LOGIN_THRESHOLD`: Number of failed logins to trigger alert
- `MIN_SAMPLES_FOR_TRAINING`: Minimum logs needed to train ML model

## 🗄️ Database Schema

### Collections

**logs**: Raw log events
- Indexed on: organisation_id, timestamp, host, event_type

**alerts**: Security alerts
- Indexed on: organisation_id, created_at, status, alert_id (unique)

**endpoints**: Endpoint information and risk metrics
- Indexed on: organisation_id + host (unique)

**ml_models**: Trained anomaly detection models
- Stores pickled Isolation Forest models per organisation

**compliance_cache**: Cached compliance data
- Stores compliance scores and control assessments

## 🤖 Machine Learning Details

### Anomaly Detection Pipeline

1. **Feature Extraction**: Converts log events to numeric features
   - Temporal: hour of day, day of week
   - Behavioral: event type, user, host hashes
   - Contextual: failed login counts, event frequencies
   - Content: success flags, error indicators

2. **Model Training**: Isolation Forest with contamination=0.1
   - Trained per organisation on last 7 days of logs
   - Requires minimum 100 samples
   - Automatically retrains when stale

3. **Prediction**: Scores each event
   - Score transformed to 0-1 range (higher = more anomalous)
   - Alerts created when score > threshold or prediction = anomaly

### Risk Scoring

Endpoint risk score (0-100) calculated from:
- Recent alert counts (7-day and 30-day windows)
- Critical alert counts (weighted higher)
- Anomaly detection counts
- Compliance issues

Risk levels: LOW (0-24), MEDIUM (25-49), HIGH (50-74), CRITICAL (75-100)

## 📋 Compliance Assessment

HIPAA security controls assessed:
- Access Control (unique user ID, emergency access)
- Audit Controls (logging coverage)
- Authentication (failed login monitoring)
- Monitoring (critical alert resolution)

Compliance score = (compliant × 100% + partial × 50%) / total controls

## 🛠️ Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests (to be implemented)
pytest tests/
```

### Code Quality

```bash
# Format code
black app/

# Lint code
pylint app/
```

## 🚢 Deployment

### Production Considerations

1. **Security**:
   - Implement proper authentication (JWT, OAuth2)
   - Use HTTPS/TLS
   - Enable MongoDB authentication
   - Restrict CORS origins

2. **Scalability**:
   - Use Redis for caching
   - Implement background tasks with Celery
   - Use load balancer for multiple API instances
   - Consider MongoDB replica sets

3. **Monitoring**:
   - Add logging (structlog, loguru)
   - Implement metrics (Prometheus)
   - Set up alerting
   - Use APM tools (DataDog, New Relic)

## 📝 License

Copyright © 2025 Cyber HealthGuard AI

## 🤝 Support

For issues and questions, please open an issue on the GitHub repository.

## 🎯 Roadmap

- [ ] User authentication with JWT
- [ ] Real-time alerts via WebSocket
- [ ] Advanced ML models (LSTM, Transformer)
- [ ] Integration with SOAR platforms
- [ ] Automated response actions
- [ ] Custom rule builder UI
- [ ] Multi-model ensemble detection
- [ ] Threat intelligence feed integration
