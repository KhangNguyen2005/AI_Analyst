import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import logging
import pickle
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLPredictionBot:
    """Machine Learning based price prediction bot"""

    def __init__(self):
        self.name = "ML Prediction Bot"
        self.scaler = MinMaxScaler()
        self.models = {}
        self.models_dir = "models"

        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)

    def create_features(self, df):
        """Create features for ML model"""
        features_df = pd.DataFrame(index=df.index)
        close = df["Close"].values

        # Price-based features
        features_df["SMA_10"] = df["Close"].rolling(window=10).mean()
        features_df["SMA_20"] = df["Close"].rolling(window=20).mean()
        features_df["SMA_50"] = df["Close"].rolling(window=50).mean()

        # Volatility
        features_df["Volatility"] = df["Close"].rolling(window=20).std()

        # Price momentum
        features_df["Momentum"] = df["Close"].diff(periods=10)

        # Rate of change
        features_df["ROC"] = ((df["Close"] - df["Close"].shift(10)) / df["Close"].shift(10)) * 100

        # Volume features
        volume_sma = df["Volume"].rolling(window=20).mean()
        features_df["Volume_SMA"] = volume_sma
        features_df["Volume_Ratio"] = (df["Volume"] / volume_sma).fillna(1.0)

        # High-Low range
        features_df["HL_Range"] = (df["High"] - df["Low"]) / df["Close"]

        # Previous day return
        features_df["Prev_Return"] = df["Close"].pct_change()

        # Drop NaN rows
        features_df = features_df.dropna()

        return features_df

    def prepare_training_data(self, df, lookback=20):
        """Prepare data for training"""
        features_df = self.create_features(df)

        X = features_df.iloc[:-1].values
        y = df["Close"].iloc[lookback:].values[:len(X)]

        # Predict future price (next day)
        y_future = df["Close"].shift(-1).iloc[lookback:-1].values[:len(X)]

        return X, y_future

    def train_model(self, df, symbol):
        """Train ML model for a stock"""
        try:
            X, y = self.prepare_training_data(df)

            if len(X) < 50:
                logger.warning(f"Insufficient data for training {symbol}")
                return None

            # Split data (80% train, 20% test)
            split_idx = int(len(X) * 0.8)
            X_train, y_train = X[:split_idx], y[:split_idx]

            # Train Random Forest model
            model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
            model.fit(X_train, y_train)

            # Save model
            model_path = os.path.join(self.models_dir, f"{symbol}_model.pkl")
            with open(model_path, "wb") as f:
                pickle.dump(model, f)

            self.models[symbol] = model
            logger.info(f"Model trained for {symbol}")
            return model

        except Exception as e:
            logger.error(f"Error training model for {symbol}: {e}")
            return None

    def predict(self, df, symbol):
        """Make price prediction for a stock"""
        try:
            # Train or load model
            if symbol not in self.models:
                model = self.train_model(df, symbol)
            else:
                model = self.models[symbol]

            if model is None:
                return {
                    "symbol": symbol,
                    "prediction": None,
                    "confidence": 0,
                    "signal": "NEUTRAL",
                    "reason": "Model not available"
                }

            # Prepare latest features
            features_df = self.create_features(df)
            if features_df.empty:
                return {
                    "symbol": symbol,
                    "prediction": None,
                    "confidence": 0,
                    "signal": "NEUTRAL",
                    "reason": "Insufficient data"
                }

            latest_features = features_df.iloc[-1:].values

            # Make prediction
            predicted_price = model.predict(latest_features)[0]
            current_price = df["Close"].iloc[-1]

            # Calculate expected return
            expected_return = (predicted_price - current_price) / current_price
            confidence = min(abs(expected_return) * 2, 1.0)  # Scale to 0-1

            # Generate signal
            if expected_return > 0.02:  # 2% upside
                signal = "BUY"
            elif expected_return < -0.02:  # 2% downside
                signal = "SELL"
            else:
                signal = "NEUTRAL"

            return {
                "symbol": symbol,
                "timestamp": pd.Timestamp.now(),
                "current_price": current_price,
                "predicted_price": predicted_price,
                "expected_return": expected_return,
                "confidence": confidence,
                "signal": signal
            }

        except Exception as e:
            logger.error(f"Error in ML prediction for {symbol}: {e}")
            return {
                "symbol": symbol,
                "confidence": 0,
                "signal": "NEUTRAL",
                "reason": f"Error: {e}"
            }

    def retrain_models(self, df_dict):
        """Retrain all models periodically"""
        for symbol, df in df_dict.items():
            if df is not None:
                self.train_model(df, symbol)
