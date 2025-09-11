# GitHub M&A Intelligence System

<div align="center">

## 🔍 Real-Time GitHub M&A Intelligence Platform
## Advanced system for detecting corporate acquisitions through repository ownership transfers and contributor pattern analysis

<img src="https://img.shields.io/badge/M%26A-Intelligence-red?style=for-the-badge&logo=trending-up" alt="M&A Intelligence"> <img src="https://img.shields.io/badge/GitHub-API-blue?style=for-the-badge&logo=github" alt="GitHub API"> <img src="https://img.shields.io/badge/Machine-Learning-green?style=for-the-badge&logo=python" alt="ML Powered"> <img src="https://img.shields.io/badge/D3.js-Visualization-orange?style=for-the-badge&logo=d3.js" alt="D3.js">

### 📊 Live Intelligence Dashboard

**[🎯 View Live Dashboard](dashboard/)** | **[📡 API Documentation](api/)** | **[📊 Analytics Portal](dashboard/index.html)**

</div>

---

## 🚀 System Overview

This is a comprehensive **real-time GitHub M&A Intelligence system** that uses actual GitHub API data to:

- **Track repository transfers** between organizations
- **Monitor contributor migration** patterns
- **Detect unusual activity** and acquisition signals
- **Generate acquisition probability scores** using machine learning
- **Provide interactive visualizations** with real-time updates
- **Offer REST API** for integration with other systems

### 🎯 Key Features

- ✅ **Real GitHub API Integration** - No more mock data
- ✅ **Machine Learning Anomaly Detection** - Pattern recognition and risk assessment
- ✅ **Interactive D3.js Dashboard** - Modern, responsive visualizations
- ✅ **REST API with Authentication** - Secure data access
- ✅ **Historical Data Storage** - PostgreSQL database with comprehensive schema
- ✅ **Rate Limiting & Caching** - Respectful API usage with Redis caching
- ✅ **Automated Data Collection** - Scheduled background processing
- ✅ **Comprehensive CLI** - Easy system management

---

## 📊 Intelligence Dashboard

### Live Analytics Portal
- **Real-time repository monitoring** with live star/fork tracking
- **Interactive anomaly detection** with risk level indicators
- **Acquisition probability predictions** with confidence scores
- **Contributor network analysis** showing cross-company collaborations
- **Historical trend analysis** with time-series visualizations
- **Filtering and search capabilities** for focused analysis

### Key Metrics Tracked
- Repository ownership changes
- Contributor migration between companies
- Unusual commit patterns and activity spikes
- Cross-company collaboration signals
- Language and technology stack analysis
- Network centrality and influence metrics

---

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub API    │───▶│ Data Collector  │───▶│   PostgreSQL    │
│   (Real Data)   │    │                 │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  ML Analyzer    │───▶│   Redis Cache   │───▶│   REST API      │
│ (Anomaly Detect)│    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ D3.js Dashboard │───▶│   Web Server    │───▶│   CLI Tools     │
│ (Interactive)   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

1. **Data Collection Module** (`github_data_collector.py`)
   - Real-time GitHub API integration
   - Repository and contributor data collection
   - Transfer event detection
   - Rate limiting and error handling

2. **Machine Learning Engine** (`github_ml_analyzer.py`)
   - Anomaly detection using Isolation Forest
   - Acquisition probability prediction
   - Feature engineering and pattern recognition
   - Risk assessment and scoring

3. **Interactive Dashboard** (`dashboard/`)
   - D3.js and Plotly.js visualizations
   - Real-time data updates
   - Filtering and search capabilities
   - Responsive design

4. **REST API Server** (`github_api_server.py`)
   - Flask-based API with CORS support
   - JWT authentication for admin functions
   - Comprehensive endpoints for all data
   - Background task scheduling

5. **Database Schema** (`database_schema.sql`)
   - PostgreSQL with optimized indexes
   - Historical data storage
   - Complex queries and analytics views
   - Data integrity constraints

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (optional, for full features)
- Redis (optional, for caching)
- GitHub Personal Access Token

### Installation

1. **Clone and setup:**
```bash
git clone <repository-url>
cd github-ma-intelligence
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your GitHub token and other settings
```

4. **Run system check:**
```bash
python main.py check
```

5. **Run complete pipeline:**
```bash
python main.py all
```

### Usage Examples

#### Collect Data from Top Repositories
```bash
python main.py collect --min-stars 5000
```

#### Run ML Analysis
```bash
python main.py analyze
```

#### Generate Dashboard
```bash
python main.py dashboard
```

#### Start API Server
```bash
python main.py api --port 8000
```

#### View Dashboard
Open `dashboard/index.html` in your browser or start the API server and visit `http://localhost:5000`

---

## 📡 API Documentation

### Authentication
Some endpoints require JWT authentication. Use the `/api/auth/login` endpoint to obtain a token.

### Core Endpoints

#### Data Endpoints
- `GET /api/data/current` - Current repository and contributor data
- `GET /api/repositories` - Repository data with filtering
- `GET /api/anomalies` - Detected anomalies
- `GET /api/predictions` - Acquisition predictions
- `GET /api/transfers` - Repository transfer events

#### Analysis Endpoints
- `GET /api/analysis/latest` - Latest ML analysis results
- `GET /api/stats` - System statistics

#### Administrative Endpoints
- `POST /api/refresh` - Force data refresh (requires auth)
- `POST /api/auth/login` - Obtain JWT token

### Example API Usage

```python
import requests

# Get current data
response = requests.get('http://localhost:5000/api/data/current')
data = response.json()

# Get anomalies
response = requests.get('http://localhost:5000/api/anomalies?risk_level=HIGH')
anomalies = response.json()
```

---

## 🎯 Intelligence Features

### Anomaly Detection
- **Unusual activity patterns** in repository metrics
- **Sudden contributor changes** indicating ownership transfers
- **Cross-company collaboration spikes**
- **Abnormal commit frequency patterns**

### Acquisition Prediction
- **Probability scoring** based on multiple signals
- **Predicted acquirers** using historical patterns
- **Timeline estimates** for potential deals
- **Key signal identification** for early detection

### Risk Assessment
- **Multi-level risk scoring** (Low, Medium, High, Critical)
- **Confidence intervals** for all predictions
- **Historical trend analysis**
- **Real-time alerting** capabilities

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
GITHUB_TOKEN=your_github_personal_access_token
JWT_SECRET_KEY=your-secure-jwt-secret

# Optional
DATABASE_URL=postgresql://user:pass@localhost:5432/github_ma
REDIS_URL=redis://localhost:6379/0
API_PORT=5000
LOG_LEVEL=INFO
```

### Advanced Configuration

- **Rate Limiting**: Configurable API rate limits
- **Caching**: Redis-based caching with TTL
- **ML Models**: Customizable model parameters
- **Dashboard**: Theme and layout customization

---

## 📈 Data Sources & Methodology

### Primary Data Sources
- **GitHub REST API v3** - Repository, user, and organization data
- **GitHub Events API** - Real-time activity monitoring
- **Commit History Analysis** - Contributor pattern detection
- **Repository Metadata** - Stars, forks, language statistics

### Intelligence Signals
- Repository ownership changes
- Contributor company affiliations
- Commit pattern anomalies
- Cross-organization collaborations
- Technology stack analysis
- Network influence metrics

### ML Models Used
- **Isolation Forest** for anomaly detection
- **Random Forest** for acquisition prediction
- **Time-series analysis** for trend detection
- **Network analysis** for influence mapping

---

## 🚨 Real-Time Alerts

### Alert Types
- **High-Risk Anomalies** - Immediate attention required
- **Acquisition Signals** - Potential M&A activity detected
- **Transfer Events** - Repository ownership changes
- **System Health** - API or data collection issues

### Alert Channels
- **Dashboard Notifications** - Real-time UI alerts
- **Email Alerts** - Configurable email notifications
- **Slack Integration** - Team collaboration alerts
- **API Webhooks** - Custom integration endpoints

---

## 📊 Sample Intelligence Output

### Repository Analysis
```
Repository: facebook/react
Risk Level: MEDIUM
Anomaly Score: 0.73
Signals:
- Cross-company contributions increased 47%
- Enterprise integration patterns detected
- Recent activity spike in enterprise features
```

### Acquisition Prediction
```
Company: Vercel
Acquisition Probability: 76%
Predicted Acquirer: Big Tech (Google/Meta)
Timeline: 6-12 months
Key Signals:
- Next.js ecosystem dominance
- Strategic positioning in React ecosystem
- Enterprise customer growth
```

---

## 🔒 Security & Compliance

### Data Protection
- **Rate Limiting** - Respectful API usage
- **Authentication** - JWT-based secure access
- **Data Encryption** - Secure storage of sensitive data
- **Access Logging** - Comprehensive audit trails

### API Compliance
- **GitHub API Terms** - Full compliance with usage policies
- **Rate Limit Management** - Intelligent request throttling
- **Error Handling** - Graceful failure recovery
- **Data Privacy** - No personal data collection

---

## 🛠️ Development & Testing

### Testing
```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/integration/

# Test API endpoints
python test_api.py
```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run with debug mode
python main.py api --debug

# Monitor logs
tail -f github_ma_intelligence.log
```

---

## 📚 Advanced Usage

### Custom ML Models
```python
from github_ml_analyzer import MLAnalyzer

analyzer = MLAnalyzer()
# Customize model parameters
analyzer.anomaly_detector.contamination = 0.05
```

### Database Queries
```sql
-- Find high-risk repositories
SELECT * FROM anomaly_summary
WHERE risk_level = 'HIGH'
ORDER BY anomaly_score DESC;

-- Get acquisition predictions
SELECT * FROM acquisition_targets
WHERE acquisition_probability > 0.7;
```

### API Integration
```javascript
// Real-time dashboard updates
const eventSource = new EventSource('/api/stream/updates');
eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    updateDashboard(data);
};
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Write unit tests for all new features
- Update documentation for API changes

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **GitHub API** for providing comprehensive repository data
- **D3.js Community** for powerful visualization tools
- **Scikit-learn** for machine learning capabilities
- **Flask Framework** for robust API development

---

<div align="center">

## 🎯 Ready to Detect M&A Activity?

**[🚀 Get Started](main.py)** | **[📊 View Dashboard](dashboard/)** | **[📡 API Docs](api/)**

*Real intelligence from real data - no simulations, just insights*

**Last Updated: 2025-09-11 | System Status: 🟢 Operational**

</div>