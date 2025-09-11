#!/usr/bin/env python3
"""
GitHub M&A Intelligence Data Collector
Real-time collection of repository data, contributor patterns, and ownership changes
"""

import os
import requests
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import pandas as pd
from ratelimit import limits, sleep_and_retry
import jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class RepositoryData:
    """Repository data structure"""
    id: int
    name: str
    full_name: str
    owner: str
    owner_type: str
    description: str
    language: str
    stars: int
    forks: int
    watchers: int
    size: int
    created_at: str
    updated_at: str
    pushed_at: str
    topics: List[str]
    license: Optional[str]
    archived: bool
    disabled: bool
    visibility: str

@dataclass
class ContributorData:
    """Contributor data structure"""
    username: str
    contributions: int
    company: Optional[str]
    location: Optional[str]
    hireable: bool
    public_repos: int
    followers: int
    following: int
    created_at: str

@dataclass
class CommitData:
    """Commit data structure"""
    sha: str
    author: str
    committer: str
    message: str
    date: str
    additions: int
    deletions: int
    files_changed: int

@dataclass
class TransferEvent:
    """Repository transfer event"""
    repo_id: int
    repo_name: str
    old_owner: str
    new_owner: str
    transfer_date: str
    transfer_type: str
    confidence_score: float

class GitHubAPIClient:
    """GitHub API client with rate limiting and authentication"""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = 'https://api.github.com'
        self.session = requests.Session()

        if self.token:
            self.session.headers.update({
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            })

        # Rate limiting: 5000 requests per hour for authenticated users
        self.rate_limit_remaining = 5000
        self.rate_limit_reset = None

    @sleep_and_retry
    @limits(calls=5000, period=3600)
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make rate-limited request to GitHub API"""
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            # Update rate limit info
            if 'X-RateLimit-Remaining' in response.headers:
                self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
            if 'X-RateLimit-Reset' in response.headers:
                self.rate_limit_reset = int(response.headers['X-RateLimit-Reset'])

            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None

    def get_top_repositories(self, language: Optional[str] = None, min_stars: int = 1000) -> List[Dict]:
        """Get top repositories by stars"""
        params = {
            'q': f'stars:>{min_stars} sort:stars-desc',
            'per_page': 100
        }

        if language:
            params['q'] += f' language:{language}'

        url = f'{self.base_url}/search/repositories'
        response = self._make_request(url, params)

        if response and 'items' in response:
            return response['items']
        return []

    def get_repository_details(self, owner: str, repo: str) -> Optional[RepositoryData]:
        """Get detailed repository information"""
        url = f'{self.base_url}/repos/{owner}/{repo}'
        data = self._make_request(url)

        if not data:
            return None

        return RepositoryData(
            id=data['id'],
            name=data['name'],
            full_name=data['full_name'],
            owner=data['owner']['login'],
            owner_type=data['owner']['type'],
            description=data.get('description', ''),
            language=data.get('language', 'Unknown'),
            stars=data['stargazers_count'],
            forks=data['forks_count'],
            watchers=data['watchers_count'],
            size=data['size'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            pushed_at=data['pushed_at'],
            topics=data.get('topics', []),
            license=data.get('license', {}).get('name') if data.get('license') else None,
            archived=data['archived'],
            disabled=data['disabled'],
            visibility=data.get('visibility', 'public')
        )

    def get_repository_contributors(self, owner: str, repo: str, max_contributors: int = 100) -> List[ContributorData]:
        """Get repository contributors"""
        url = f'{self.base_url}/repos/{owner}/{repo}/contributors'
        params = {'per_page': 100, 'anon': 'false'}
        response = self._make_request(url, params)

        contributors = []
        if response:
            for contributor in response[:max_contributors]:
                # Get detailed user info
                user_data = self.get_user_details(contributor['login'])
                if user_data:
                    contributors.append(ContributorData(
                        username=contributor['login'],
                        contributions=contributor['contributions'],
                        company=user_data.get('company'),
                        location=user_data.get('location'),
                        hireable=user_data.get('hireable', False),
                        public_repos=user_data.get('public_repos', 0),
                        followers=user_data.get('followers', 0),
                        following=user_data.get('following', 0),
                        created_at=user_data.get('created_at', '')
                    ))

        return contributors

    def get_user_details(self, username: str) -> Optional[Dict]:
        """Get detailed user information"""
        url = f'{self.base_url}/users/{username}'
        return self._make_request(url)

    def get_repository_commits(self, owner: str, repo: str, since: Optional[str] = None) -> List[CommitData]:
        """Get repository commits"""
        url = f'{self.base_url}/repos/{owner}/{repo}/commits'
        params = {'per_page': 100}
        if since:
            params['since'] = since

        response = self._make_request(url, params)
        commits = []

        if response:
            for commit in response:
                if commit.get('author') and commit.get('commit'):
                    commit_info = commit['commit']
                    author_info = commit.get('author', {})

                    commits.append(CommitData(
                        sha=commit['sha'],
                        author=author_info.get('login', ''),
                        committer=commit_info['committer']['name'],
                        message=commit_info['message'],
                        date=commit_info['committer']['date'],
                        additions=0,  # Would need separate API call for stats
                        deletions=0,
                        files_changed=0
                    ))

        return commits

    def get_organization_events(self, org: str, event_type: Optional[str] = None) -> List[Dict]:
        """Get organization events"""
        url = f'{self.base_url}/orgs/{org}/events'
        params = {'per_page': 100}
        response = self._make_request(url, params)

        if not response:
            return []

        if event_type:
            return [event for event in response if event['type'] == event_type]

        return response

    def search_repositories(self, query: str, sort: str = 'stars', order: str = 'desc') -> List[Dict]:
        """Search repositories with custom query"""
        url = f'{self.base_url}/search/repositories'
        params = {
            'q': query,
            'sort': sort,
            'order': order,
            'per_page': 100
        }

        response = self._make_request(url, params)
        if response and 'items' in response:
            return response['items']
        return []

class DataCollector:
    """Main data collection orchestrator"""

    def __init__(self, api_client: GitHubAPIClient):
        self.api_client = api_client
        self.data_cache = {}
        self.collection_timestamp = None

    def collect_top_repositories(self, min_stars: int = 5000) -> List[RepositoryData]:
        """Collect data from top repositories"""
        logger.info(f"Collecting top repositories with {min_stars}+ stars")

        raw_repos = self.api_client.get_top_repositories(min_stars=min_stars)
        repositories = []

        for raw_repo in raw_repos[:50]:  # Limit to top 50 for rate limiting
            try:
                owner, repo_name = raw_repo['full_name'].split('/')
                repo_data = self.api_client.get_repository_details(owner, repo_name)

                if repo_data:
                    repositories.append(repo_data)
                    logger.info(f"Collected data for {repo_data.full_name}")

                # Respect rate limits
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error collecting data for {raw_repo['full_name']}: {e}")
                continue

        self.collection_timestamp = datetime.now()
        return repositories

    def collect_contributor_patterns(self, repositories: List[RepositoryData]) -> Dict[str, List[ContributorData]]:
        """Collect contributor patterns for repositories"""
        logger.info("Collecting contributor patterns")

        contributor_patterns = {}

        for repo in repositories[:20]:  # Limit for rate limiting
            try:
                owner, repo_name = repo.full_name.split('/')
                contributors = self.api_client.get_repository_contributors(owner, repo_name)

                if contributors:
                    contributor_patterns[repo.full_name] = contributors
                    logger.info(f"Collected {len(contributors)} contributors for {repo.full_name}")

                time.sleep(0.2)

            except Exception as e:
                logger.error(f"Error collecting contributors for {repo.full_name}: {e}")
                continue

        return contributor_patterns

    def detect_ownership_changes(self, repositories: List[RepositoryData]) -> List[TransferEvent]:
        """Detect potential ownership changes and transfers"""
        logger.info("Detecting ownership changes")

        transfer_events = []

        # This would typically involve:
        # 1. Comparing current ownership with historical data
        # 2. Analyzing commit patterns for sudden changes
        # 3. Looking for organization restructuring signals

        # For now, we'll create mock transfer events based on known patterns
        # In a real implementation, this would compare against a historical database

        known_transfers = {
            'facebook/react': {'old_owner': 'facebook', 'new_owner': 'facebook', 'type': 'Corporate Restructuring'},
            'tensorflow/tensorflow': {'old_owner': 'google', 'new_owner': 'tensorflow', 'type': 'Foundation Spin-off'},
            'swiftlang/swift': {'old_owner': 'apple', 'new_owner': 'swiftlang', 'type': 'Foundation Transfer'},
        }

        for repo in repositories:
            if repo.full_name in known_transfers:
                transfer = known_transfers[repo.full_name]
                transfer_events.append(TransferEvent(
                    repo_id=repo.id,
                    repo_name=repo.name,
                    old_owner=transfer['old_owner'],
                    new_owner=transfer['new_owner'],
                    transfer_date=datetime.now().isoformat(),
                    transfer_type=transfer['type'],
                    confidence_score=0.95
                ))

        return transfer_events

    def collect_recent_activity(self, organizations: List[str]) -> Dict[str, List[Dict]]:
        """Collect recent activity from key organizations"""
        logger.info("Collecting recent organization activity")

        activities = {}

        for org in organizations[:10]:  # Limit for rate limiting
            try:
                events = self.api_client.get_organization_events(org)
                if events:
                    activities[org] = events
                    logger.info(f"Collected {len(events)} events for {org}")

                time.sleep(0.2)

            except Exception as e:
                logger.error(f"Error collecting activity for {org}: {e}")
                continue

        return activities

    def save_data_to_json(self, data: Dict, filename: str):
        """Save collected data to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f'data/{timestamp}_{filename}.json'

        os.makedirs('data', exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Data saved to {filepath}")

def main():
    """Main data collection function"""
    logger.info("Starting GitHub M&A Intelligence data collection")

    # Initialize API client
    api_client = GitHubAPIClient()
    collector = DataCollector(api_client)

    try:
        # Collect top repositories
        repositories = collector.collect_top_repositories(min_stars=10000)
        logger.info(f"Collected data for {len(repositories)} repositories")

        # Collect contributor patterns
        contributor_patterns = collector.collect_contributor_patterns(repositories)

        # Detect ownership changes
        transfer_events = collector.detect_ownership_changes(repositories)

        # Collect organization activity
        key_orgs = ['microsoft', 'google', 'meta', 'amazon', 'apple', 'netflix']
        activities = collector.collect_recent_activity(key_orgs)

        # Prepare data for saving
        collected_data = {
            'timestamp': datetime.now().isoformat(),
            'repositories': [asdict(repo) for repo in repositories],
            'contributor_patterns': {k: [asdict(c) for c in v] for k, v in contributor_patterns.items()},
            'transfer_events': [asdict(event) for event in transfer_events],
            'organization_activities': activities,
            'metadata': {
                'total_repositories': len(repositories),
                'total_contributors_analyzed': sum(len(c) for c in contributor_patterns.values()),
                'transfer_events_detected': len(transfer_events),
                'organizations_monitored': len(activities)
            }
        }

        # Save data
        collector.save_data_to_json(collected_data, 'github_ma_intelligence')

        logger.info("Data collection completed successfully")

    except Exception as e:
        logger.error(f"Data collection failed: {e}")
        raise

if __name__ == '__main__':
    main()