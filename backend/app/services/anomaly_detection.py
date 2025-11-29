"""Anomaly detection service using ML"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pickle
import hashlib
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..config import get_settings
from ..models.schemas import LogEvent

settings = get_settings()

# Try to import sklearn - make it optional
SKLEARN_AVAILABLE = False
try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    print("⚠️  WARNING: scikit-learn not available. Anomaly detection will be disabled.")
    print("   To enable ML-based anomaly detection, install: pip install scikit-learn numpy")
    # Create dummy numpy for type hints
    np = None
    IsolationForest = None
    StandardScaler = None


class AnomalyDetector:
    """
    Anomaly detection service using Isolation Forest.
    Maintains per-organisation models for detecting anomalous behavior.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.models: Dict[str, IsolationForest] = {}
        self.scalers: Dict[str, StandardScaler] = {}

    def extract_features(self, log_event: LogEvent, historical_context: Optional[Dict] = None):
        """
        Extract numeric features from a log event for anomaly detection.

        Features include:
        - Hour of day (0-23)
        - Day of week (0-6)
        - Event type encoding
        - User hash
        - Host hash
        - Failed login count (from historical context)
        - Recent event count for this user
        - Recent event count for this host
        """
        # Return None if sklearn not available
        if not SKLEARN_AVAILABLE:
            return None

        features = []

        # Temporal features
        timestamp = log_event.timestamp
        features.append(timestamp.hour)  # Hour of day
        features.append(timestamp.weekday())  # Day of week

        # Event type encoding (simple hash)
        event_type_hash = int(hashlib.md5(log_event.event_type.encode()).hexdigest()[:8], 16) % 1000
        features.append(event_type_hash)

        # User and host encoding
        user_hash = int(hashlib.md5(log_event.user.encode()).hexdigest()[:8], 16) % 1000
        host_hash = int(hashlib.md5(log_event.host.encode()).hexdigest()[:8], 16) % 1000
        features.append(user_hash)
        features.append(host_hash)

        # Historical context features
        if historical_context:
            features.append(historical_context.get("failed_login_count", 0))
            features.append(historical_context.get("user_event_count_1h", 0))
            features.append(historical_context.get("host_event_count_1h", 0))
            features.append(historical_context.get("unique_hosts_for_user", 1))
            features.append(historical_context.get("unique_users_for_host", 1))
        else:
            features.extend([0, 0, 0, 1, 1])

        # Details-based features
        details = log_event.details or {}
        features.append(1 if details.get("success") is False else 0)
        features.append(1 if "failed" in str(details).lower() else 0)
        features.append(1 if "error" in str(details).lower() else 0)

        return np.array(features).reshape(1, -1)

    async def get_historical_context(self, log_event: LogEvent) -> Dict:
        """
        Get historical context for a log event to enhance feature extraction.
        """
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

        # Failed login count for this user in last hour
        failed_login_count = await self.db.logs.count_documents({
            "organisation_id": log_event.organisation_id,
            "user": log_event.user,
            "event_type": "login",
            "details.success": False,
            "timestamp": {"$gte": one_hour_ago}
        })

        # User event count in last hour
        user_event_count = await self.db.logs.count_documents({
            "organisation_id": log_event.organisation_id,
            "user": log_event.user,
            "timestamp": {"$gte": one_hour_ago}
        })

        # Host event count in last hour
        host_event_count = await self.db.logs.count_documents({
            "organisation_id": log_event.organisation_id,
            "host": log_event.host,
            "timestamp": {"$gte": one_hour_ago}
        })

        # Unique hosts for this user in last 24h
        unique_hosts = await self.db.logs.distinct(
            "host",
            {
                "organisation_id": log_event.organisation_id,
                "user": log_event.user,
                "timestamp": {"$gte": twenty_four_hours_ago}
            }
        )

        # Unique users for this host in last 24h
        unique_users = await self.db.logs.distinct(
            "user",
            {
                "organisation_id": log_event.organisation_id,
                "host": log_event.host,
                "timestamp": {"$gte": twenty_four_hours_ago}
            }
        )

        return {
            "failed_login_count": failed_login_count,
            "user_event_count_1h": user_event_count,
            "host_event_count_1h": host_event_count,
            "unique_hosts_for_user": len(unique_hosts),
            "unique_users_for_host": len(unique_users)
        }

    async def train_model(self, organisation_id: str) -> bool:
        """
        Train or retrain the anomaly detection model for an organisation.

        Returns:
            True if model was trained successfully, False otherwise
        """
        # Return False if sklearn not available
        if not SKLEARN_AVAILABLE:
            return False

        # Get historical logs for training
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        cursor = self.db.logs.find({
            "organisation_id": organisation_id,
            "timestamp": {"$gte": seven_days_ago}
        }).limit(10000)

        logs = await cursor.to_list(length=10000)

        if len(logs) < settings.min_samples_for_training:
            return False

        # Extract features from historical logs
        feature_list = []
        for log_dict in logs:
            # Convert dict to LogEvent
            log_event = LogEvent(**log_dict)
            # For training, use simpler features (no historical context to avoid complexity)
            features = self.extract_features(log_event, None)
            feature_list.append(features.flatten())

        X = np.array(feature_list)

        # Train scaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train Isolation Forest
        model = IsolationForest(
            contamination=0.1,  # Assume 10% of data might be anomalous
            random_state=42,
            n_estimators=100
        )
        model.fit(X_scaled)

        # Store model and scaler
        self.models[organisation_id] = model
        self.scalers[organisation_id] = scaler

        # Persist to database
        await self.save_model(organisation_id, model, scaler)

        return True

    async def save_model(self, organisation_id: str, model: IsolationForest, scaler: StandardScaler):
        """Save model and scaler to database"""
        model_bytes = pickle.dumps(model)
        scaler_bytes = pickle.dumps(scaler)

        await self.db.ml_models.update_one(
            {"organisation_id": organisation_id, "model_type": "anomaly_detection"},
            {
                "$set": {
                    "model": model_bytes,
                    "scaler": scaler_bytes,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    async def load_model(self, organisation_id: str) -> bool:
        """Load model and scaler from database"""
        doc = await self.db.ml_models.find_one({
            "organisation_id": organisation_id,
            "model_type": "anomaly_detection"
        })

        if not doc:
            return False

        try:
            self.models[organisation_id] = pickle.loads(doc["model"])
            self.scalers[organisation_id] = pickle.loads(doc["scaler"])
            return True
        except Exception:
            return False

    async def predict_anomaly(self, log_event: LogEvent) -> Tuple[bool, float]:
        """
        Predict if a log event is anomalous.

        Returns:
            Tuple of (is_anomaly: bool, anomaly_score: float)
        """
        # Return default if sklearn not available
        if not SKLEARN_AVAILABLE:
            return False, 0.0

        org_id = log_event.organisation_id

        # Load or train model if not in memory
        if org_id not in self.models:
            loaded = await self.load_model(org_id)
            if not loaded:
                trained = await self.train_model(org_id)
                if not trained:
                    # Not enough data to train
                    return False, 0.0

        # Get historical context
        historical_context = await self.get_historical_context(log_event)

        # Extract features
        features = self.extract_features(log_event, historical_context)

        # Scale features
        scaler = self.scalers[org_id]
        features_scaled = scaler.transform(features)

        # Predict
        model = self.models[org_id]
        prediction = model.predict(features_scaled)[0]  # -1 for anomaly, 1 for normal
        anomaly_score_raw = model.score_samples(features_scaled)[0]

        # Convert to 0-1 score (higher = more anomalous)
        # Isolation Forest scores are negative, more negative = more anomalous
        anomaly_score = 1 / (1 + np.exp(anomaly_score_raw))  # Sigmoid transformation

        is_anomaly = prediction == -1 or anomaly_score > settings.anomaly_threshold

        return is_anomaly, float(anomaly_score)

    async def retrain_all_models(self):
        """Retrain models for all organisations (background task)"""
        if not SKLEARN_AVAILABLE:
            print("⚠️  Skipping model retraining - scikit-learn not available")
            return

        organisations = await self.db.logs.distinct("organisation_id")

        for org_id in organisations:
            try:
                await self.train_model(org_id)
            except Exception as e:
                print(f"Failed to train model for {org_id}: {e}")
