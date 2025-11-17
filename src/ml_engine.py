"""
ML Engine Module - AI-Driven Recommendations
Uses machine learning for clustering, anomaly detection, and predictions
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
import logging
from pathlib import Path
import pickle

from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class MLEngine:
    """
    Machine Learning engine for application portfolio analysis.

    Features:
    - Application clustering (similar apps grouping)
    - Anomaly detection (outlier identification)
    - Predictive analytics (score trend prediction)
    - ML-enhanced recommendations
    """

    def __init__(self, model_path: str = None):
        """
        Initialize ML engine.

        Args:
            model_path: Path to save/load trained models
        """
        if model_path is None:
            model_path = str(Path(__file__).parent.parent / 'data' / 'ml_models')

        self.model_path = Path(model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)

        # Initialize models
        self.scaler = StandardScaler()
        self.clustering_model = None
        self.anomaly_detector = None
        self.trend_predictor = None

        # Feature columns for ML
        self.feature_columns = [
            'Business Value',
            'Tech Health',
            'Cost',
            'Usage',
            'Security',
            'Strategic Fit',
            'Redundancy'
        ]

    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Prepare features for ML models.

        Args:
            df: Input DataFrame

        Returns:
            Tuple of (scaled_features, original_df)
        """
        # Ensure all required columns exist
        for col in self.feature_columns:
            if col not in df.columns:
                logger.warning(f"Missing column {col}, filling with 0")
                df[col] = 0

        # Extract features
        X = df[self.feature_columns].copy()

        # Handle missing values
        X = X.fillna(X.mean())

        # Normalize cost (log scale)
        if 'Cost' in X.columns:
            X['Cost'] = np.log1p(X['Cost'])

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        return X_scaled, df

    def cluster_applications(
        self,
        df: pd.DataFrame,
        n_clusters: int = 5
    ) -> Dict[str, Any]:
        """
        Cluster applications into similar groups using KMeans.

        Args:
            df: Application data
            n_clusters: Number of clusters to create

        Returns:
            Dictionary with clustering results
        """
        logger.info(f"Clustering {len(df)} applications into {n_clusters} groups")

        # Prepare features
        X_scaled, df_original = self.prepare_features(df)

        # Train KMeans
        self.clustering_model = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10
        )

        cluster_labels = self.clustering_model.fit_predict(X_scaled)

        # Add cluster labels to dataframe
        df_clustered = df_original.copy()
        df_clustered['Cluster'] = cluster_labels

        # Analyze clusters
        clusters_analysis = []
        for i in range(n_clusters):
            cluster_apps = df_clustered[df_clustered['Cluster'] == i]

            cluster_info = {
                'cluster_id': int(i),
                'size': len(cluster_apps),
                'avg_business_value': float(cluster_apps['Business Value'].mean()),
                'avg_tech_health': float(cluster_apps['Tech Health'].mean()),
                'avg_cost': float(cluster_apps['Cost'].mean()),
                'avg_composite_score': float(cluster_apps['Composite Score'].mean()) if 'Composite Score' in cluster_apps.columns else None,
                'dominant_recommendation': cluster_apps['Action Recommendation'].mode()[0] if 'Action Recommendation' in cluster_apps.columns else None,
                'applications': cluster_apps['Application Name'].tolist()[:10]  # Top 10 apps
            }

            # Generate cluster label
            if cluster_info['avg_business_value'] > 7 and cluster_info['avg_tech_health'] > 7:
                cluster_info['label'] = 'Strategic Leaders'
                cluster_info['description'] = 'High-performing strategic applications'
            elif cluster_info['avg_business_value'] > 7 and cluster_info['avg_tech_health'] < 5:
                cluster_info['label'] = 'Technical Debt'
                cluster_info['description'] = 'High value but needs modernization'
            elif cluster_info['avg_business_value'] < 5 and cluster_info['avg_tech_health'] > 7:
                cluster_info['label'] = 'Solid but Underutilized'
                cluster_info['description'] = 'Good tech, limited business impact'
            elif cluster_info['avg_cost'] > cluster_apps['Cost'].median() * 2:
                cluster_info['label'] = 'High Cost Burden'
                cluster_info['description'] = 'Expensive applications requiring review'
            else:
                cluster_info['label'] = f'Group {i+1}'
                cluster_info['description'] = 'Standard application group'

            clusters_analysis.append(cluster_info)

        # Sort by cluster size
        clusters_analysis.sort(key=lambda x: x['size'], reverse=True)

        return {
            'n_clusters': n_clusters,
            'clusters': clusters_analysis,
            'clustered_data': df_clustered.to_dict('records')
        }

    def detect_anomalies(
        self,
        df: pd.DataFrame,
        contamination: float = 0.1
    ) -> Dict[str, Any]:
        """
        Detect anomalous applications using Isolation Forest.

        Args:
            df: Application data
            contamination: Expected proportion of outliers (0.1 = 10%)

        Returns:
            Dictionary with anomaly detection results
        """
        logger.info(f"Detecting anomalies in {len(df)} applications")

        # Prepare features
        X_scaled, df_original = self.prepare_features(df)

        # Train Isolation Forest
        self.anomaly_detector = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )

        predictions = self.anomaly_detector.fit_predict(X_scaled)
        anomaly_scores = self.anomaly_detector.score_samples(X_scaled)

        # Add anomaly info to dataframe
        df_anomalies = df_original.copy()
        df_anomalies['Is_Anomaly'] = (predictions == -1)
        df_anomalies['Anomaly_Score'] = anomaly_scores

        # Get anomalous applications
        anomalies = df_anomalies[df_anomalies['Is_Anomaly']].copy()
        anomalies = anomalies.sort_values('Anomaly_Score')

        # Analyze why each app is anomalous
        anomaly_list = []
        for _, app in anomalies.iterrows():
            reasons = []

            # Check each feature against population
            if app['Business Value'] > df_original['Business Value'].quantile(0.95):
                reasons.append('Exceptionally high business value')
            elif app['Business Value'] < df_original['Business Value'].quantile(0.05):
                reasons.append('Unusually low business value')

            if app['Tech Health'] > df_original['Tech Health'].quantile(0.95):
                reasons.append('Exceptional technical health')
            elif app['Tech Health'] < df_original['Tech Health'].quantile(0.05):
                reasons.append('Very poor technical health')

            if app['Cost'] > df_original['Cost'].quantile(0.95):
                reasons.append('Extremely high cost')
            elif app['Cost'] < df_original['Cost'].quantile(0.05):
                reasons.append('Unusually low cost')

            if 'Usage' in app and app['Usage'] > df_original['Usage'].quantile(0.95):
                reasons.append('Very high usage')
            elif 'Usage' in app and app['Usage'] < df_original['Usage'].quantile(0.05):
                reasons.append('Minimal usage')

            anomaly_list.append({
                'application_name': app['Application Name'],
                'anomaly_score': float(app['Anomaly_Score']),
                'business_value': float(app['Business Value']),
                'tech_health': float(app['Tech Health']),
                'cost': float(app['Cost']),
                'composite_score': float(app.get('Composite Score', 0)),
                'recommendation': app.get('Action Recommendation', 'N/A'),
                'reasons': reasons if reasons else ['Unusual combination of metrics'],
                'severity': 'High' if app['Anomaly_Score'] < anomalies['Anomaly_Score'].quantile(0.33) else 'Medium'
            })

        return {
            'total_applications': len(df),
            'anomalies_detected': len(anomalies),
            'contamination_rate': float(len(anomalies) / len(df)),
            'anomalies': anomaly_list
        }

    def predict_trends(
        self,
        historical_data: List[Dict[str, Any]],
        app_name: str
    ) -> Dict[str, Any]:
        """
        Predict future trends for an application based on historical data.

        Args:
            historical_data: List of historical snapshots
            app_name: Application name

        Returns:
            Trend prediction results
        """
        if len(historical_data) < 3:
            return {
                'application_name': app_name,
                'prediction': 'Insufficient historical data',
                'confidence': 0,
                'trend': 'unknown'
            }

        # Convert to DataFrame
        df_history = pd.DataFrame(historical_data)
        df_history = df_history.sort_values('assessment_timestamp')

        # Calculate trends
        scores = df_history['composite_score'].values
        timestamps = pd.to_datetime(df_history['assessment_timestamp'])

        # Simple linear regression for trend
        x = np.arange(len(scores))
        slope, intercept = np.polyfit(x, scores, 1)

        # Predict next score
        next_score = slope * len(scores) + intercept
        next_score = max(0, min(100, next_score))  # Clamp to 0-100

        # Determine trend
        if slope > 1:
            trend = 'improving'
            confidence = min(0.95, abs(slope) / 10)
        elif slope < -1:
            trend = 'declining'
            confidence = min(0.95, abs(slope) / 10)
        else:
            trend = 'stable'
            confidence = 0.6

        # Calculate volatility
        volatility = float(np.std(scores))

        return {
            'application_name': app_name,
            'current_score': float(scores[-1]),
            'predicted_next_score': float(next_score),
            'trend': trend,
            'trend_rate': float(slope),
            'confidence': float(confidence),
            'volatility': volatility,
            'data_points': len(scores),
            'recommendation': self._get_trend_recommendation(trend, scores[-1], next_score)
        }

    def _get_trend_recommendation(
        self,
        trend: str,
        current_score: float,
        predicted_score: float
    ) -> str:
        """Generate recommendation based on trend analysis"""
        if trend == 'declining' and current_score < 50:
            return 'URGENT: Declining application with low score - consider immediate action'
        elif trend == 'declining':
            return 'WARNING: Declining trend detected - investigate root causes'
        elif trend == 'improving' and predicted_score > 70:
            return 'POSITIVE: Continue current improvement initiatives'
        elif trend == 'stable' and current_score > 70:
            return 'MAINTAIN: Application is stable and healthy'
        elif trend == 'stable' and current_score < 50:
            return 'REVIEW: Stable but underperforming - needs assessment'
        else:
            return 'MONITOR: Track application closely'

    def get_ml_recommendations(
        self,
        df: pd.DataFrame,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Generate ML-enhanced recommendations.

        Args:
            df: Application data
            top_n: Number of top recommendations to return

        Returns:
            ML-based recommendations
        """
        recommendations = {
            'retirement_candidates': [],
            'investment_opportunities': [],
            'quick_wins': [],
            'consolidation_targets': []
        }

        # Prepare features
        X_scaled, df_original = self.prepare_features(df)

        # Retirement candidates: Low value, poor health, high cost
        df_scored = df_original.copy()
        df_scored['retirement_score'] = (
            (10 - df_scored['Business Value']) * 0.4 +
            (10 - df_scored['Tech Health']) * 0.3 +
            (df_scored['Cost'] / df_scored['Cost'].max()) * 10 * 0.3
        )

        retirement = df_scored.nlargest(top_n, 'retirement_score')
        for _, app in retirement.iterrows():
            recommendations['retirement_candidates'].append({
                'application_name': app['Application Name'],
                'score': float(app['retirement_score']),
                'current_composite': float(app.get('Composite Score', 0)),
                'annual_savings': float(app['Cost']),
                'reason': f"Low value ({app['Business Value']:.1f}), poor health ({app['Tech Health']:.1f}), costs ${app['Cost']:,.0f}/year"
            })

        # Investment opportunities: High value, good health, strategic
        df_scored['investment_score'] = (
            df_scored['Business Value'] * 0.4 +
            df_scored['Tech Health'] * 0.3 +
            df_scored.get('Strategic Fit', 5) * 0.3
        )

        investment = df_scored.nlargest(top_n, 'investment_score')
        for _, app in investment.iterrows():
            recommendations['investment_opportunities'].append({
                'application_name': app['Application Name'],
                'score': float(app['investment_score']),
                'current_composite': float(app.get('Composite Score', 0)),
                'reason': f"High value ({app['Business Value']:.1f}), good health ({app['Tech Health']:.1f})"
            })

        # Quick wins: Medium value, poor health, low cost to fix
        df_scored['quick_win_score'] = (
            df_scored['Business Value'] * 0.5 +
            (10 - df_scored['Tech Health']) * 0.3 +
            (1 - df_scored['Cost'] / df_scored['Cost'].max()) * 10 * 0.2
        )

        quick_wins = df_scored.nlargest(top_n, 'quick_win_score')
        for _, app in quick_wins.iterrows():
            recommendations['quick_wins'].append({
                'application_name': app['Application Name'],
                'score': float(app['quick_win_score']),
                'current_composite': float(app.get('Composite Score', 0)),
                'reason': f"Good value ({app['Business Value']:.1f}), improvable health ({app['Tech Health']:.1f})"
            })

        # Consolidation targets: Similar apps in same cluster
        if hasattr(self, 'clustering_model') and self.clustering_model is not None:
            cluster_labels = self.clustering_model.predict(X_scaled)
            df_scored['cluster'] = cluster_labels

            # Find clusters with multiple apps
            for cluster_id in range(self.clustering_model.n_clusters):
                cluster_apps = df_scored[df_scored['cluster'] == cluster_id]
                if len(cluster_apps) > 2:
                    # Sort by score, keep best one
                    cluster_apps_sorted = cluster_apps.sort_values('Composite Score', ascending=False)
                    for _, app in cluster_apps_sorted[1:top_n+1].iterrows():
                        recommendations['consolidation_targets'].append({
                            'application_name': app['Application Name'],
                            'cluster_id': int(cluster_id),
                            'similar_apps': cluster_apps_sorted.iloc[0]['Application Name'],
                            'reason': 'Similar functionality to better-performing application'
                        })

        return recommendations

    def save_models(self):
        """Save trained models to disk"""
        try:
            if self.clustering_model:
                with open(self.model_path / 'clustering_model.pkl', 'wb') as f:
                    pickle.dump(self.clustering_model, f)

            if self.anomaly_detector:
                with open(self.model_path / 'anomaly_detector.pkl', 'wb') as f:
                    pickle.dump(self.anomaly_detector, f)

            with open(self.model_path / 'scaler.pkl', 'wb') as f:
                pickle.dump(self.scaler, f)

            logger.info(f"Models saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save models: {e}")

    def load_models(self):
        """Load trained models from disk"""
        try:
            clustering_path = self.model_path / 'clustering_model.pkl'
            if clustering_path.exists():
                with open(clustering_path, 'rb') as f:
                    self.clustering_model = pickle.load(f)

            anomaly_path = self.model_path / 'anomaly_detector.pkl'
            if anomaly_path.exists():
                with open(anomaly_path, 'rb') as f:
                    self.anomaly_detector = pickle.load(f)

            scaler_path = self.model_path / 'scaler.pkl'
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)

            logger.info(f"Models loaded from {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            return False
