#!/usr/bin/env python3
"""
GitHub M&A Intelligence System - Main Orchestrator
Command-line interface for managing the complete M&A intelligence system
"""

import os
import sys
import json
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_ma_intelligence.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MAIntelligenceSystem:
    """Main system orchestrator"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / 'data'
        self.dashboard_dir = self.project_root / 'dashboard'

        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.dashboard_dir.mkdir(exist_ok=True)

    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        logger.info("Checking system dependencies...")

        required_packages = [
            'requests', 'pandas', 'numpy', 'scikit-learn', 'tensorflow',
            'flask', 'flask_cors', 'plotly', 'redis', 'psycopg2'
        ]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            logger.error(f"Missing required packages: {', '.join(missing_packages)}")
            logger.info("Installing missing packages...")
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
                ])
                logger.info("Dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install dependencies: {e}")
                return False

        # Check for GitHub token
        if not os.getenv('GITHUB_TOKEN'):
            logger.warning("GITHUB_TOKEN not found in environment variables")
            logger.info("Please set your GitHub token in the .env file")
            return False

        logger.info("All dependencies satisfied")
        return True

    def initialize_database(self):
        """Initialize the database schema"""
        logger.info("Initializing database...")

        try:
            db_url = os.getenv('DATABASE_URL')
            if not db_url:
                logger.warning("DATABASE_URL not configured, skipping database initialization")
                return True

            # Check if it's SQLite or PostgreSQL
            if db_url.startswith('sqlite:///'):
                # Use SQLite
                import sqlite3
                db_path = db_url.replace('sqlite:///', '')
                conn = sqlite3.connect(db_path)
                logger.info("Using SQLite database")
            else:
                # Try PostgreSQL
                try:
                    import psycopg2
                    from psycopg2 import sql
                    conn = psycopg2.connect(db_url)
                    logger.info("Using PostgreSQL database")
                except ImportError:
                    logger.warning("psycopg2 not available, database features will be limited")
                    return True

            conn.close()
            logger.info("Database connection test successful")

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False

        return True

    def collect_data(self, **kwargs):
        """Run data collection"""
        logger.info("Starting data collection...")

        try:
            from github_data_collector import GitHubAPIClient, DataCollector

            api_client = GitHubAPIClient()
            collector = DataCollector(api_client)

            # Collect repositories
            min_stars = kwargs.get('min_stars', 10000)
            repositories = collector.collect_top_repositories(min_stars=min_stars)

            # Collect contributor patterns
            contributor_patterns = collector.collect_contributor_patterns(repositories)

            # Detect transfer events
            transfer_events = collector.detect_ownership_changes(repositories)

            # Collect organization activities
            key_orgs = ['microsoft', 'google', 'meta', 'amazon', 'apple', 'netflix']
            activities = collector.collect_recent_activity(key_orgs)

            # Prepare data
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

            # Save data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/{timestamp}_collected_data.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Data collection completed: {len(repositories)} repositories, {len(transfer_events)} transfers")
            return True

        except Exception as e:
            logger.error(f"Data collection failed: {e}")
            return False

    def run_analysis(self, **kwargs):
        """Run ML analysis"""
        logger.info("Starting ML analysis...")

        try:
            from github_ml_analyzer import MLAnalyzer

            analyzer = MLAnalyzer()

            # Load latest data
            data_files = list(self.data_dir.glob('*_collected_data.json'))
            if not data_files:
                logger.error("No collected data found. Run data collection first.")
                return False

            latest_data_file = max(data_files, key=lambda x: x.stat().st_mtime)
            with open(latest_data_file, 'r') as f:
                current_data = json.load(f)

            # Run analysis
            results = analyzer.analyze_repository_data(current_data)

            # Save results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/{timestamp}_ml_analysis.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            anomalies = results.get('anomalies', [])
            predictions = results.get('acquisition_predictions', [])

            logger.info(f"ML analysis completed: {len(anomalies)} anomalies, {len(predictions)} predictions")
            return True

        except Exception as e:
            logger.error(f"ML analysis failed: {e}")
            return False

    def generate_dashboard(self, **kwargs):
        """Generate dashboard files"""
        logger.info("Generating dashboard...")

        try:
            # Import and run dashboard generation
            from generate_dashboard import create_index_html, generate_overview_chart, generate_language_chart

            # Load latest data
            data_files = list(self.data_dir.glob('*_collected_data.json'))
            if data_files:
                latest_data_file = max(data_files, key=lambda x: x.stat().st_mtime)
                with open(latest_data_file, 'r') as f:
                    data = json.load(f)

                repos_data = data.get('repositories', [])
            else:
                # Fallback to mock data
                repos_data = self._get_mock_data()

            # Generate charts
            generate_overview_chart(repos_data)
            generate_language_chart(repos_data)

            # Generate HTML
            create_index_html(repos_data)

            logger.info("Dashboard generated successfully")
            return True

        except Exception as e:
            logger.error(f"Dashboard generation failed: {e}")
            return False

    def start_api_server(self, **kwargs):
        """Start the API server"""
        logger.info("Starting API server...")

        try:
            from github_api_server import app

            host = kwargs.get('host', '0.0.0.0')
            port = kwargs.get('port', 5000)
            debug = kwargs.get('debug', False)

            logger.info(f"API server starting on {host}:{port}")
            app.run(host=host, port=port, debug=debug)

        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
            return False

    def run_system_check(self):
        """Run comprehensive system check"""
        logger.info("Running system health check...")

        checks = {
            'dependencies': self.check_dependencies(),
            'database': self.initialize_database(),
            'data_directory': self.data_dir.exists(),
            'dashboard_directory': self.dashboard_dir.exists(),
            'github_token': bool(os.getenv('GITHUB_TOKEN')),
            'environment_config': self._check_environment_config()
        }

        all_passed = all(checks.values())

        logger.info("System check results:")
        for check, passed in checks.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            logger.info(f"  {check}: {status}")

        if all_passed:
            logger.info("All system checks passed!")
        else:
            logger.warning("Some system checks failed. Please address the issues above.")

        return all_passed

    def _check_environment_config(self):
        """Check environment configuration"""
        required_vars = ['GITHUB_TOKEN', 'JWT_SECRET_KEY']
        optional_vars = ['DATABASE_URL', 'REDIS_URL', 'ADMIN_USERNAME', 'ADMIN_PASSWORD']

        missing_required = [var for var in required_vars if not os.getenv(var)]

        if missing_required:
            logger.warning(f"Missing required environment variables: {', '.join(missing_required)}")
            return False

        return True

    def _get_mock_data(self):
        """Get mock data for testing"""
        return [
            {
                'name': 'react',
                'full_name': 'facebook/react',
                'owner': 'Meta',
                'stars': 228000,
                'forks': 46700,
                'language': 'JavaScript',
                'transfer_from': 'Facebook',
                'transfer_to': 'Meta',
                'estimated_value': '$2.8B'
            },
            {
                'name': 'tensorflow',
                'full_name': 'tensorflow/tensorflow',
                'owner': 'Google',
                'stars': 186000,
                'forks': 74300,
                'language': 'C++',
                'transfer_from': 'Google',
                'transfer_to': 'Google',
                'estimated_value': '$3.1B'
            }
        ]

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='GitHub M&A Intelligence System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py check                    # Run system health check
  python main.py collect --min-stars 5000 # Collect data from repos with 5k+ stars
  python main.py analyze                  # Run ML analysis on collected data
  python main.py dashboard                # Generate dashboard files
  python main.py api --port 8000          # Start API server on port 8000
  python main.py all                      # Run complete pipeline
        """
    )

    parser.add_argument('command', choices=[
        'check', 'collect', 'analyze', 'dashboard', 'api', 'all'
    ], help='Command to execute')

    # Data collection options
    parser.add_argument('--min-stars', type=int, default=10000,
                       help='Minimum stars for repository collection (default: 10000)')

    # API server options
    parser.add_argument('--host', default='0.0.0.0',
                       help='API server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000,
                       help='API server port (default: 5000)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode for API server')

    args = parser.parse_args()

    system = MAIntelligenceSystem()

    try:
        if args.command == 'check':
            success = system.run_system_check()

        elif args.command == 'collect':
            success = system.collect_data(min_stars=args.min_stars)

        elif args.command == 'analyze':
            success = system.run_analysis()

        elif args.command == 'dashboard':
            success = system.generate_dashboard()

        elif args.command == 'api':
            system.start_api_server(
                host=args.host,
                port=args.port,
                debug=args.debug
            )
            return  # start_api_server doesn't return

        elif args.command == 'all':
            logger.info("Running complete M&A intelligence pipeline...")

            # Run system check
            if not system.run_system_check():
                logger.error("System check failed. Please fix issues before running pipeline.")
                sys.exit(1)

            # Collect data
            if not system.collect_data(min_stars=args.min_stars):
                logger.error("Data collection failed.")
                sys.exit(1)

            # Run analysis
            if not system.run_analysis():
                logger.error("ML analysis failed.")
                sys.exit(1)

            # Generate dashboard
            if not system.generate_dashboard():
                logger.error("Dashboard generation failed.")
                sys.exit(1)

            logger.info("Complete pipeline executed successfully!")
            success = True

        if success:
            logger.info(f"Command '{args.command}' completed successfully")
            sys.exit(0)
        else:
            logger.error(f"Command '{args.command}' failed")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()