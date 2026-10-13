# AI Analyst Configuration
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")  # Optional: for NewsAPI

# Trading Configuration
WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "ORCL", "INTC", "SOFI", "SPY", "QQQ", "^VIX","BTC-USD"]
INITIAL_CAPITAL = 100000  # Paper trading capital
TRADE_SIZE_PERCENT = 0.1  # Use 10% of capital per trade

# Blue-chip screening universe. Edit this list as your definition of
# "ideal blue chip" changes.
BLUE_CHIP_UNIVERSE = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO",
    "ORCL", "CRM", "ADBE", "IBM", "BRK-B", "JPM", "V", "MA", "BAC",
    "UNH", "JNJ", "LLY", "MRK", "ABBV", "PG", "COST", "WMT", "HD",
    "KO", "PEP", "MCD", "NKE", "XOM", "CVX", "CAT", "GE", "HON",
]
BLUE_CHIP_BUY_SCORE = float(os.getenv("BLUE_CHIP_BUY_SCORE", "72"))
BLUE_CHIP_SELL_SCORE = float(os.getenv("BLUE_CHIP_SELL_SCORE", "45"))

# Data Configuration
DATA_UPDATE_INTERVAL = 300  # Update data every 5 minutes
TECHNICAL_LOOKBACK_DAYS = 252
ML_LOOKBACK_DAYS = 1095

# Flask Configuration
FLASK_PORT = 5000
FLASK_DEBUG = True

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ai_analyst.db")

# TradingView Webhook
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-secret-key")

# Local alert scanner (TradingView webhook alternative)
LOCAL_ALERT_SCAN_INTERVAL = int(os.getenv("LOCAL_ALERT_SCAN_INTERVAL", "60"))
LOCAL_ALERT_RULES_FILE = os.getenv("LOCAL_ALERT_RULES_FILE", "local_alerts.json")
LOCAL_ALERT_EVENTS_FILE = os.getenv("LOCAL_ALERT_EVENTS_FILE", "local_alert_events.json")
REAL_PORTFOLIO_FILE = os.getenv("REAL_PORTFOLIO_FILE", "real_portfolio.json")

# Analysis Thresholds
SENTIMENT_THRESHOLD = 0.6  # Confidence threshold for sentiment
TECHNICAL_SIGNAL_STRENGTH = 0.7  # Strength threshold for technical signals
ML_CONFIDENCE_THRESHOLD = 0.65  # ML prediction confidence
CONSENSUS_THRESHOLD = 0.6  # % of bots that need to agree

# Risk Management
MAX_POSITION_SIZE = 0.25  # Max 25% of capital in single position
STOP_LOSS_PERCENT = 2.0  # 2% stop loss
TAKE_PROFIT_PERCENT = 5.0  # 5% take profit
