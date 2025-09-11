#!/usr/bin/env python3
"""
GitHub M&A Intelligence REST API
Provides endpoints for accessing intelligence data and analysis results
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import redis
from dotenv import load_dotenv
import schedule
import time
import threading

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
jwt = JWTManager(app)

# Redis for caching
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Import our modules
from github_data_collector import GitHubAPIClient, DataCollector
from github_ml_analyzer import MLAnalyzer

class APIError(Exception):
    """Custom API error class"""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify({'error': error.message})
    response.status_code = error.status_code
    return response

@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def handle_internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

class IntelligenceAPI:
    """Main API class for GitHub M&A Intelligence"""

    def __init__(self):
        self.api_client = GitHubAPIClient()
        self.collector = DataCollector(self.api_client)
        self.analyzer = MLAnalyzer()
        self.data_cache_timeout = 300  # 5 minutes
        self.analysis_cache_timeout = 600  # 10 minutes

    def get_cached_data(self, key):
        """Get data from Redis cache"""
        try:
            data = redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None

    def set_cached_data(self, key, data, timeout=None):
        """Set data in Redis cache"""
        try:
            timeout = timeout or self.data_cache_timeout
            redis_client.setex(key, timeout, json.dumps(data))
        except Exception as e:
            logger.error(f"Cache write error: {e}")

    def collect_fresh_data(self):
        """Collect fresh data from GitHub API"""
        logger.info("Collecting fresh data from GitHub API")

        try:
            # Collect repositories
            repositories = self.collector.collect_top_repositories(min_stars=10000)

            # Collect contributor patterns
            contributor_patterns = self.collector.collect_contributor_patterns(repositories)

            # Detect transfer events
            transfer_events = self.collector.detect_ownership_changes(repositories)

            # Collect organization activities
            key_orgs = ['microsoft', 'google', 'meta', 'amazon', 'apple', 'netflix']
            activities = self.collector.collect_recent_activity(key_orgs)

            # Prepare data structure
            data = {
                'timestamp': datetime.now().isoformat(),
                'repositories': [vars(repo) for repo in repositories],
                'contributor_patterns': {k: [vars(c) for c in v] for k, v in contributor_patterns.items()},
                'transfer_events': [vars(event) for event in transfer_events],
                'organization_activities': activities,
                'metadata': {
                    'total_repositories': len(repositories),
                    'total_contributors_analyzed': sum(len(c) for c in contributor_patterns.values()),
                    'transfer_events_detected': len(transfer_events),
                    'organizations_monitored': len(activities)
                }
            }

            # Cache the data
            self.set_cached_data('current_data', data)

            # Save to file for persistence
            os.makedirs('data', exist_ok=True)
            filename = f"data/{datetime.now().strftime('%Y%m%d_%H%M%S')}_api_data.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Fresh data collected and cached: {len(repositories)} repositories")
            return data

        except Exception as e:
            logger.error(f"Data collection failed: {e}")
            raise APIError("Failed to collect data from GitHub API", 500)

    def perform_ml_analysis(self, data):
        """Perform ML analysis on the data"""
        logger.info("Performing ML analysis")

        try:
            # Analyze the data
            results = self.analyzer.analyze_repository_data(data)

            # Cache the results
            self.set_cached_data('latest_analysis', results, self.analysis_cache_timeout)

            # Save to file
            os.makedirs('data', exist_ok=True)
            filename = f"data/{datetime.now().strftime('%Y%m%d_%H%M%S')}_ml_analysis.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            logger.info("ML analysis completed and cached")
            return results

        except Exception as e:
            logger.error(f"ML analysis failed: {e}")
            raise APIError("Failed to perform ML analysis", 500)

# Initialize API instance
intelligence_api = IntelligenceAPI()

# Routes
@app.route('/')
def index():
    """Serve the main dashboard"""
    return send_from_directory('dashboard', 'index.html')

@app.route('/dashboard/<path:filename>')
def dashboard_files(filename):
    """Serve dashboard static files"""
    return send_from_directory('dashboard', filename)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/data/current')
def get_current_data():
    """Get current repository and contributor data"""
    try:
        # Try to get from cache first
        cached_data = intelligence_api.get_cached_data('current_data')

        if cached_data:
            return jsonify(cached_data)

        # If not in cache, collect fresh data
        data = intelligence_api.collect_fresh_data()
        return jsonify(data)

    except Exception as e:
        logger.error(f"Failed to get current data: {e}")
        raise APIError("Failed to retrieve current data", 500)

@app.route('/api/analysis/latest')
def get_latest_analysis():
    """Get latest ML analysis results"""
    try:
        # Try to get from cache first
        cached_analysis = intelligence_api.get_cached_data('latest_analysis')

        if cached_analysis:
            return jsonify(cached_analysis)

        # If not in cache, get current data and analyze
        current_data = intelligence_api.get_cached_data('current_data')
        if not current_data:
            current_data = intelligence_api.collect_fresh_data()

        analysis = intelligence_api.perform_ml_analysis(current_data)
        return jsonify(analysis)

    except Exception as e:
        logger.error(f"Failed to get analysis: {e}")
        raise APIError("Failed to retrieve analysis results", 500)

@app.route('/api/repositories')
def get_repositories():
    """Get repository data with optional filtering"""
    try:
        data = intelligence_api.get_cached_data('current_data')
        if not data:
            data = intelligence_api.collect_fresh_data()

        repositories = data.get('repositories', [])

        # Apply filters
        language = request.args.get('language')
        min_stars = request.args.get('min_stars', type=int)
        limit = request.args.get('limit', 50, type=int)

        if language:
            repositories = [r for r in repositories if r.get('language') == language]

        if min_stars:
            repositories = [r for r in repositories if r.get('stars', 0) >= min_stars]

        repositories = repositories[:limit]

        return jsonify({
            'repositories': repositories,
            'count': len(repositories),
            'filters': {
                'language': language,
                'min_stars': min_stars,
                'limit': limit
            }
        })

    except Exception as e:
        logger.error(f"Failed to get repositories: {e}")
        raise APIError("Failed to retrieve repositories", 500)

@app.route('/api/anomalies')
def get_anomalies():
    """Get detected anomalies"""
    try:
        analysis = intelligence_api.get_cached_data('latest_analysis')
        if not analysis:
            current_data = intelligence_api.get_cached_data('current_data')
            if not current_data:
                current_data = intelligence_api.collect_fresh_data()
            analysis = intelligence_api.perform_ml_analysis(current_data)

        anomalies = analysis.get('anomalies', [])
        risk_level = request.args.get('risk_level')

        if risk_level:
            anomalies = [a for a in anomalies if a.get('risk_level') == risk_level.upper()]

        return jsonify({
            'anomalies': anomalies,
            'count': len(anomalies),
            'risk_levels': list(set(a.get('risk_level') for a in anomalies))
        })

    except Exception as e:
        logger.error(f"Failed to get anomalies: {e}")
        raise APIError("Failed to retrieve anomalies", 500)

@app.route('/api/predictions')
def get_predictions():
    """Get acquisition predictions"""
    try:
        analysis = intelligence_api.get_cached_data('latest_analysis')
        if not analysis:
            current_data = intelligence_api.get_cached_data('current_data')
            if not current_data:
                current_data = intelligence_api.collect_fresh_data()
            analysis = intelligence_api.perform_ml_analysis(current_data)

        predictions = analysis.get('acquisition_predictions', [])
        min_probability = request.args.get('min_probability', 0.0, type=float)

        if min_probability > 0:
            predictions = [p for p in predictions if p.get('acquisition_probability', 0) >= min_probability]

        return jsonify({
            'predictions': predictions,
            'count': len(predictions),
            'min_probability': min_probability
        })

    except Exception as e:
        logger.error(f"Failed to get predictions: {e}")
        raise APIError("Failed to retrieve predictions", 500)

@app.route('/api/transfers')
def get_transfers():
    """Get repository transfer events"""
    try:
        data = intelligence_api.get_cached_data('current_data')
        if not data:
            data = intelligence_api.collect_fresh_data()

        transfers = data.get('transfer_events', [])
        confidence_min = request.args.get('confidence_min', 0.0, type=float)

        if confidence_min > 0:
            transfers = [t for t in transfers if t.get('confidence_score', 0) >= confidence_min]

        return jsonify({
            'transfers': transfers,
            'count': len(transfers),
            'confidence_min': confidence_min
        })

    except Exception as e:
        logger.error(f"Failed to get transfers: {e}")
        raise APIError("Failed to retrieve transfer events", 500)

@app.route('/api/organizations/<org>/activity')
def get_organization_activity(org):
    """Get activity for a specific organization"""
    try:
        data = intelligence_api.get_cached_data('current_data')
        if not data:
            data = intelligence_api.collect_fresh_data()

        activities = data.get('organization_activities', {}).get(org, [])

        return jsonify({
            'organization': org,
            'activities': activities,
            'count': len(activities)
        })

    except Exception as e:
        logger.error(f"Failed to get organization activity: {e}")
        raise APIError(f"Failed to retrieve activity for {org}", 500)

@app.route('/api/refresh', methods=['POST'])
@jwt_required()
def refresh_data():
    """Force refresh of all data (requires authentication)"""
    try:
        logger.info("Manual data refresh requested")

        # Collect fresh data
        data = intelligence_api.collect_fresh_data()

        # Perform fresh analysis
        analysis = intelligence_api.perform_ml_analysis(data)

        return jsonify({
            'status': 'success',
            'message': 'Data refreshed successfully',
            'repositories_collected': len(data.get('repositories', [])),
            'anomalies_detected': len(analysis.get('anomalies', [])),
            'predictions_generated': len(analysis.get('acquisition_predictions', [])),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Manual refresh failed: {e}")
        raise APIError("Failed to refresh data", 500)

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    try:
        data = intelligence_api.get_cached_data('current_data')
        analysis = intelligence_api.get_cached_data('latest_analysis')

        stats = {
            'repositories_monitored': len(data.get('repositories', [])) if data else 0,
            'contributors_analyzed': data.get('metadata', {}).get('total_contributors_analyzed', 0) if data else 0,
            'anomalies_detected': len(analysis.get('anomalies', [])) if analysis else 0,
            'high_risk_anomalies': len([a for a in analysis.get('anomalies', []) if a.get('risk_level') == 'HIGH']) if analysis else 0,
            'acquisition_predictions': len(analysis.get('acquisition_predictions', [])) if analysis else 0,
            'transfer_events': len(data.get('transfer_events', [])) if data else 0,
            'last_update': data.get('timestamp') if data else None,
            'cache_status': 'healthy' if redis_client.ping() else 'unhealthy'
        }

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise APIError("Failed to retrieve statistics", 500)

# Authentication routes (for admin functions)
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Simple authentication for admin functions"""
    data = request.get_json()

    # Simple authentication (replace with proper auth in production)
    username = data.get('username')
    password = data.get('password')

    if username == os.getenv('ADMIN_USERNAME', 'admin') and password == os.getenv('ADMIN_PASSWORD', 'password'):
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token})

    return jsonify({'error': 'Invalid credentials'}), 401

def scheduled_data_collection():
    """Scheduled data collection function"""
    while True:
        try:
            logger.info("Running scheduled data collection")
            intelligence_api.collect_fresh_data()

            # Also run ML analysis
            current_data = intelligence_api.get_cached_data('current_data')
            if current_data:
                intelligence_api.perform_ml_analysis(current_data)

        except Exception as e:
            logger.error(f"Scheduled collection failed: {e}")

        # Wait 30 minutes before next collection
        time.sleep(30 * 60)

def start_background_tasks():
    """Start background tasks"""
    # Start scheduled data collection in a separate thread
    collection_thread = threading.Thread(target=scheduled_data_collection, daemon=True)
    collection_thread.start()

    logger.info("Background tasks started")

if __name__ == '__main__':
    # Start background tasks
    start_background_tasks()

    # Run the Flask app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    logger.info(f"Starting GitHub M&A Intelligence API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)