#!/usr/bin/env python3
"""
GitHub M&A Intelligence Machine Learning Module
Anomaly detection, pattern recognition, and acquisition probability scoring
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import joblib
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MLFeatures:
    """Machine learning features for repository analysis"""
    repo_id: int
    stars_growth_rate: float
    contributor_diversity: float
    commit_frequency: float
    cross_company_contributions: float
    language_consistency: float
    organization_size: int
    recent_activity_score: float
    network_centrality: float
    license_changes: int
    topic_changes: int

@dataclass
class AnomalyScore:
    """Anomaly detection results"""
    repo_name: str
    anomaly_score: float
    confidence: float
    anomaly_type: str
    risk_level: str
    indicators: List[str]

@dataclass
class AcquisitionPrediction:
    """Acquisition probability prediction"""
    company: str
    acquisition_probability: float
    confidence_score: float
    predicted_acquirer: str
    timeline_estimate: str
    key_signals: List[str]

class FeatureEngineer:
    """Feature engineering for ML models"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}

    def extract_temporal_features(self, repo_data: Dict, historical_data: List[Dict]) -> Dict[str, float]:
        """Extract temporal features from repository data"""
        features = {}

        if not historical_data:
            return {
                'stars_growth_rate': 0.0,
                'commit_frequency': 0.0,
                'recent_activity_score': 0.0
            }

        # Calculate stars growth rate
        current_stars = repo_data.get('stars', 0)
        historical_stars = [h.get('stars', 0) for h in historical_data[-30:]]  # Last 30 days

        if historical_stars and len(historical_stars) > 1:
            avg_historical_stars = np.mean(historical_stars)
            if avg_historical_stars > 0:
                features['stars_growth_rate'] = (current_stars - avg_historical_stars) / avg_historical_stars
            else:
                features['stars_growth_rate'] = 0.0
        else:
            features['stars_growth_rate'] = 0.0

        # Calculate commit frequency
        commit_dates = []
        for h in historical_data[-90:]:  # Last 90 days
            if 'commits' in h:
                commit_dates.extend([c.get('date') for c in h['commits'] if c.get('date')])

        if commit_dates:
            commit_dates = [datetime.fromisoformat(d.replace('Z', '+00:00')) for d in commit_dates if d]
            if len(commit_dates) > 1:
                time_diffs = np.diff(sorted(commit_dates))
                avg_commit_frequency = np.mean([td.total_seconds() / 3600 for td in time_diffs])  # Hours between commits
                features['commit_frequency'] = 1.0 / max(avg_commit_frequency, 1.0)  # Commits per hour
            else:
                features['commit_frequency'] = 0.0
        else:
            features['commit_frequency'] = 0.0

        # Recent activity score
        recent_commits = len([h for h in historical_data[-7:] if h.get('commits')])  # Last 7 days
        features['recent_activity_score'] = min(recent_commits / 7.0, 1.0)

        return features

    def extract_contributor_features(self, contributors: List[Dict]) -> Dict[str, float]:
        """Extract contributor-based features"""
        if not contributors:
            return {
                'contributor_diversity': 0.0,
                'cross_company_contributions': 0.0,
                'organization_size': 0
            }

        features = {}

        # Contributor diversity (unique companies)
        companies = [c.get('company') for c in contributors if c.get('company')]
        unique_companies = len(set(companies))
        features['contributor_diversity'] = unique_companies / len(contributors)

        # Cross-company contributions
        big_tech_companies = {'Google', 'Microsoft', 'Meta', 'Amazon', 'Apple', 'Netflix', 'Tesla'}
        cross_company_contribs = sum(1 for c in contributors
                                   if c.get('company') and c.get('company') in big_tech_companies)
        features['cross_company_contributions'] = cross_company_contribs / len(contributors)

        # Organization size indicator
        features['organization_size'] = len(contributors)

        return features

    def extract_repository_features(self, repo_data: Dict) -> Dict[str, float]:
        """Extract repository-specific features"""
        features = {}

        # Language consistency (would need historical data)
        features['language_consistency'] = 1.0  # Placeholder

        # Network centrality (stars + forks + watchers)
        stars = repo_data.get('stars', 0)
        forks = repo_data.get('forks', 0)
        watchers = repo_data.get('watchers', 0)
        features['network_centrality'] = np.log1p(stars + forks + watchers)

        # License and topic changes (would need historical comparison)
        features['license_changes'] = 0
        features['topic_changes'] = 0

        return features

    def create_feature_vector(self, repo_data: Dict, contributors: List[Dict],
                            historical_data: List[Dict]) -> MLFeatures:
        """Create complete feature vector for ML model"""
        temporal_features = self.extract_temporal_features(repo_data, historical_data)
        contributor_features = self.extract_contributor_features(contributors)
        repo_features = self.extract_repository_features(repo_data)

        return MLFeatures(
            repo_id=repo_data.get('id', 0),
            stars_growth_rate=temporal_features['stars_growth_rate'],
            contributor_diversity=contributor_features['contributor_diversity'],
            commit_frequency=temporal_features['commit_frequency'],
            cross_company_contributions=contributor_features['cross_company_contributions'],
            language_consistency=repo_features['language_consistency'],
            organization_size=contributor_features['organization_size'],
            recent_activity_score=temporal_features['recent_activity_score'],
            network_centrality=repo_features['network_centrality'],
            license_changes=repo_features['license_changes'],
            topic_changes=repo_features['topic_changes']
        )

class AnomalyDetector:
    """Anomaly detection for repository activity"""

    def __init__(self):
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False

    def train_baseline_model(self, historical_features: List[MLFeatures]):
        """Train anomaly detection model on historical data"""
        if not historical_features:
            logger.warning("No historical data available for training")
            return

        # Convert features to DataFrame
        feature_dicts = [vars(f) for f in historical_features]
        df = pd.DataFrame(feature_dicts)

        # Select numerical features
        numerical_features = [
            'stars_growth_rate', 'contributor_diversity', 'commit_frequency',
            'cross_company_contributions', 'language_consistency', 'organization_size',
            'recent_activity_score', 'network_centrality', 'license_changes', 'topic_changes'
        ]

        X = df[numerical_features].fillna(0)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.isolation_forest.fit(X_scaled)
        self.is_trained = True

        logger.info(f"Trained anomaly detection model on {len(historical_features)} samples")

    def detect_anomalies(self, current_features: List[MLFeatures]) -> List[AnomalyScore]:
        """Detect anomalies in current repository data"""
        if not self.is_trained:
            logger.warning("Model not trained, cannot detect anomalies")
            return []

        anomaly_scores = []

        for features in current_features:
            # Convert to feature vector
            feature_dict = vars(features)
            feature_values = [
                feature_dict['stars_growth_rate'],
                feature_dict['contributor_diversity'],
                feature_dict['commit_frequency'],
                feature_dict['cross_company_contributions'],
                feature_dict['language_consistency'],
                feature_dict['organization_size'],
                feature_dict['recent_activity_score'],
                feature_dict['network_centrality'],
                feature_dict['license_changes'],
                feature_dict['topic_changes']
            ]

            # Scale features
            X_scaled = self.scaler.transform([feature_values])

            # Get anomaly score (-1 for anomalies, 1 for normal)
            anomaly_score = self.isolation_forest.decision_function(X_scaled)[0]
            prediction = self.isolation_forest.predict(X_scaled)[0]

            # Convert to positive anomaly score (higher = more anomalous)
            normalized_score = (anomaly_score + 1) / 2  # Convert from [-1,1] to [0,1]

            # Determine anomaly type and risk level
            anomaly_type, risk_level, indicators = self._classify_anomaly(features, normalized_score)

            anomaly_scores.append(AnomalyScore(
                repo_name=f"repo_{features.repo_id}",
                anomaly_score=normalized_score,
                confidence=abs(anomaly_score),
                anomaly_type=anomaly_type,
                risk_level=risk_level,
                indicators=indicators
            ))

        return anomaly_scores

    def _classify_anomaly(self, features: MLFeatures, score: float) -> Tuple[str, str, List[str]]:
        """Classify the type of anomaly detected"""
        indicators = []

        if score > 0.7:
            risk_level = "HIGH"
        elif score > 0.5:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Analyze feature contributions
        if features.stars_growth_rate > 2.0:
            indicators.append("Unusual stars growth rate")
        if features.cross_company_contributions > 0.3:
            indicators.append("High cross-company contributions")
        if features.commit_frequency > 10.0:
            indicators.append("Abnormally high commit frequency")
        if features.recent_activity_score > 0.8:
            indicators.append("Sudden increase in recent activity")

        if not indicators:
            indicators.append("General activity pattern deviation")

        # Determine anomaly type
        if features.cross_company_contributions > 0.3:
            anomaly_type = "Cross-company collaboration"
        elif features.stars_growth_rate > 2.0:
            anomaly_type = "Rapid growth anomaly"
        elif features.commit_frequency > 10.0:
            anomaly_type = "Activity spike"
        else:
            anomaly_type = "General pattern deviation"

        return anomaly_type, risk_level, indicators

class AcquisitionPredictor:
    """Machine learning model for predicting acquisition probability"""

    def __init__(self):
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight='balanced'
        )
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.is_trained = False

    def train_model(self, training_data: List[Dict]):
        """Train acquisition prediction model"""
        if not training_data:
            logger.warning("No training data available")
            return

        # Convert to DataFrame
        df = pd.DataFrame(training_data)

        # Features for prediction
        feature_columns = [
            'stars', 'forks', 'contributors_count', 'commit_frequency',
            'company_age_years', 'big_tech_contributors', 'funding_rounds'
        ]

        # Create synthetic labels for demonstration
        # In real implementation, this would use historical acquisition data
        df['acquisition_likelihood'] = np.random.choice([0, 1], size=len(df), p=[0.8, 0.2])

        X = df[feature_columns].fillna(0)
        y = df['acquisition_likelihood']

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.classifier.fit(X_scaled, y)
        self.is_trained = True

        logger.info(f"Trained acquisition prediction model on {len(training_data)} samples")

    def predict_acquisition_probability(self, company_data: Dict) -> AcquisitionPrediction:
        """Predict acquisition probability for a company"""
        if not self.is_trained:
            return AcquisitionPrediction(
                company=company_data.get('name', 'Unknown'),
                acquisition_probability=0.0,
                confidence_score=0.0,
                predicted_acquirer="Unknown",
                timeline_estimate="Unknown",
                key_signals=[]
            )

        # Extract features
        features = [
            company_data.get('stars', 0),
            company_data.get('forks', 0),
            company_data.get('contributors_count', 0),
            company_data.get('commit_frequency', 0),
            company_data.get('company_age_years', 0),
            company_data.get('big_tech_contributors', 0),
            company_data.get('funding_rounds', 0)
        ]

        # Scale features
        X_scaled = self.scaler.transform([features])

        # Get prediction
        probability = self.classifier.predict_proba(X_scaled)[0][1]
        prediction = self.classifier.predict(X_scaled)[0]

        # Determine predicted acquirer based on company profile
        predicted_acquirer = self._predict_acquirer(company_data)

        # Estimate timeline
        timeline = self._estimate_timeline(probability, company_data)

        # Key signals
        signals = self._identify_key_signals(company_data, probability)

        return AcquisitionPrediction(
            company=company_data.get('name', 'Unknown'),
            acquisition_probability=probability,
            confidence_score=max(probability, 1-probability),
            predicted_acquirer=predicted_acquirer,
            timeline_estimate=timeline,
            key_signals=signals
        )

    def _predict_acquirer(self, company_data: Dict) -> str:
        """Predict most likely acquirer based on company characteristics"""
        industry = company_data.get('industry', 'Unknown')
        tech_stack = company_data.get('tech_stack', [])

        if 'AI' in tech_stack or 'Machine Learning' in tech_stack:
            return "Google or Microsoft"
        elif 'JavaScript' in tech_stack or 'Frontend' in tech_stack:
            return "Meta or Vercel"
        elif 'Cloud' in tech_stack or 'Infrastructure' in tech_stack:
            return "Amazon or Microsoft"
        else:
            return "Big Tech (Various)"

    def _estimate_timeline(self, probability: float, company_data: Dict) -> str:
        """Estimate acquisition timeline"""
        if probability > 0.8:
            return "0-6 months"
        elif probability > 0.6:
            return "6-12 months"
        elif probability > 0.4:
            return "1-2 years"
        else:
            return "2+ years"

    def _identify_key_signals(self, company_data: Dict, probability: float) -> List[str]:
        """Identify key signals for acquisition"""
        signals = []

        if probability > 0.7:
            signals.append("High acquisition probability")
        if company_data.get('big_tech_contributors', 0) > 5:
            signals.append("Big tech contributor involvement")
        if company_data.get('funding_rounds', 0) > 3:
            signals.append("Multiple funding rounds")
        if company_data.get('stars', 0) > 50000:
            signals.append("High repository popularity")

        return signals if signals else ["Monitoring for acquisition signals"]

class MLAnalyzer:
    """Main ML analysis orchestrator"""

    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.anomaly_detector = AnomalyDetector()
        self.acquisition_predictor = AcquisitionPredictor()
        self.historical_data = []

    def load_historical_data(self, data_path: str = 'data'):
        """Load historical data for training"""
        if not os.path.exists(data_path):
            logger.warning(f"Historical data path {data_path} does not exist")
            return

        historical_features = []

        # Load historical JSON files
        for filename in os.listdir(data_path):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(data_path, filename), 'r') as f:
                        data = json.load(f)

                    if 'repositories' in data:
                        for repo in data['repositories']:
                            # Create synthetic historical data for demonstration
                            historical_features.append(self._create_synthetic_features(repo))

                except Exception as e:
                    logger.error(f"Error loading {filename}: {e}")

        if historical_features:
            self.anomaly_detector.train_baseline_model(historical_features)
            self.acquisition_predictor.train_model(historical_features)

        logger.info(f"Loaded historical data for {len(historical_features)} repositories")

    def _create_synthetic_features(self, repo_data: Dict) -> MLFeatures:
        """Create synthetic features for demonstration"""
        return MLFeatures(
            repo_id=repo_data.get('id', 0),
            stars_growth_rate=np.random.normal(0, 0.5),
            contributor_diversity=np.random.uniform(0, 1),
            commit_frequency=np.random.exponential(2),
            cross_company_contributions=np.random.uniform(0, 0.3),
            language_consistency=np.random.uniform(0.8, 1.0),
            organization_size=np.random.randint(10, 1000),
            recent_activity_score=np.random.uniform(0, 1),
            network_centrality=np.log1p(repo_data.get('stars', 0)),
            license_changes=np.random.randint(0, 3),
            topic_changes=np.random.randint(0, 5)
        )

    def analyze_repository_data(self, current_data: Dict) -> Dict[str, Any]:
        """Perform complete ML analysis on repository data"""
        results = {
            'anomalies': [],
            'acquisition_predictions': [],
            'risk_assessment': {},
            'timestamp': datetime.now().isoformat()
        }

        if 'repositories' not in current_data:
            logger.warning("No repository data found for analysis")
            return results

        # Extract features for all repositories
        current_features = []
        for repo in current_data['repositories'][:20]:  # Limit for processing
            contributors = current_data.get('contributor_patterns', {}).get(repo['full_name'], [])
            historical_repo_data = []  # Would load from database in real implementation

            features = self.feature_engineer.create_feature_vector(repo, contributors, historical_repo_data)
            current_features.append(features)

        # Detect anomalies
        if self.anomaly_detector.is_trained:
            anomalies = self.anomaly_detector.detect_anomalies(current_features)
            results['anomalies'] = [vars(a) for a in anomalies]

            # Risk assessment
            high_risk_anomalies = [a for a in anomalies if a.risk_level == 'HIGH']
            results['risk_assessment'] = {
                'total_anomalies': len(anomalies),
                'high_risk_count': len(high_risk_anomalies),
                'overall_risk_level': 'HIGH' if len(high_risk_anomalies) > 3 else 'MEDIUM' if len(high_risk_anomalies) > 1 else 'LOW'
            }

        # Predict acquisitions
        if self.acquisition_predictor.is_trained:
            predictions = []
            for repo in current_data['repositories'][:10]:
                # Create company data for prediction
                company_data = {
                    'name': repo['name'],
                    'stars': repo['stars'],
                    'forks': repo['forks'],
                    'contributors_count': len(current_data.get('contributor_patterns', {}).get(repo['full_name'], [])),
                    'commit_frequency': np.random.exponential(2),  # Synthetic
                    'company_age_years': np.random.uniform(1, 10),  # Synthetic
                    'big_tech_contributors': np.random.randint(0, 20),  # Synthetic
                    'funding_rounds': np.random.randint(0, 5),  # Synthetic
                    'industry': 'Technology',
                    'tech_stack': [repo['language']] if repo['language'] else []
                }

                prediction = self.acquisition_predictor.predict_acquisition_probability(company_data)
                predictions.append(vars(prediction))

            results['acquisition_predictions'] = predictions

        logger.info(f"ML analysis completed: {len(results['anomalies'])} anomalies, {len(results['acquisition_predictions'])} predictions")
        return results

def main():
    """Main ML analysis function"""
    logger.info("Starting GitHub M&A Intelligence ML analysis")

    analyzer = MLAnalyzer()

    # Load historical data for training
    analyzer.load_historical_data()

    # Load current data for analysis
    try:
        # Find most recent data file
        data_files = [f for f in os.listdir('data') if f.endswith('.json')]
        if not data_files:
            logger.error("No data files found for analysis")
            return

        latest_file = max(data_files, key=lambda x: os.path.getctime(os.path.join('data', x)))
        with open(os.path.join('data', latest_file), 'r') as f:
            current_data = json.load(f)

        # Perform analysis
        results = analyzer.analyze_repository_data(current_data)

        # Save results
        output_file = f"data/ml_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"ML analysis results saved to {output_file}")

    except Exception as e:
        logger.error(f"ML analysis failed: {e}")
        raise

if __name__ == '__main__':
    main()