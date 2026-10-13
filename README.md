# AI Analyst for TradingView

A comprehensive AI-powered stock analysis system that integrates multiple analysis bots (Technical, Sentiment, ML, Fundamental) with Claude AI synthesis to generate trading signals and execute paper trades.

## 🌟 Features

- **Multi-Bot Analysis System**
  - Technical Analysis Bot: Chart patterns, indicators, trends
  - Sentiment Analysis Bot: Market sentiment from news
  - ML Prediction Bot: Machine learning price predictions
  - Fundamental Analysis Bot: Financial metrics analysis

- **Claude AI Synthesis**: Intelligent signal synthesis across all bots
- **Paper Trading Engine**: Simulate trades with real data
- **TradingView Integration**: Both webhook alerts and independent analysis
- **Web Dashboard**: Real-time portfolio and analysis visualization
- **Performance Tracking**: Win rate, profit factor, total return metrics

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- API Keys:
  - Anthropic Claude API key (from https://console.anthropic.com)
  - NewsAPI key (optional, from https://newsapi.org)

## 🚀 Installation

### 1. Clone or create project
```bash
cd /path/to/AI_Analyst
```

### 2. Create virtual environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your API keys
# Important: Add your ANTHROPIC_API_KEY from https://console.anthropic.com
```

### 5. Update watchlist (optional)
Edit `config.py` and modify the `WATCHLIST` variable with your desired stocks:
```python
WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
```

## 🎯 Running the System

### Start the Flask API server
```bash
python app.py
```

Server will run on `http://localhost:5000`

### Access the Dashboard
Open your browser and navigate to:
```
http://localhost:5000
```

## 📡 API Endpoints

### Analysis
- `GET /api/analyze/<symbol>` - Analyze a single stock
- `GET /api/analyze/all` - Analyze all watchlist stocks
- `GET /api/dashboard` - Get full dashboard data

### Portfolio & Trading
- `GET /api/portfolio` - Get current portfolio status
- `POST /api/trade` - Execute a paper trade
- `GET /api/trades/history` - Get trade history
- `GET /api/performance` - Get performance metrics

### TradingView Integration
- `POST /api/webhook/tradingview` - Receive TradingView alerts

## 🔗 TradingView Webhook Setup

For the complete current walkthrough, see `TRADINGVIEW_ALERT_WEBHOOK_GUIDE.md`.

No TradingView webhook access? Use `NO_PREMIUM_ALERT_SETUP.md` to run local alerts without a paid TradingView plan.

Want the app to find blue-chip buy/hold/sell candidates? Use `BLUE_CHIP_SIGNAL_GUIDE.md`.

Want to enter your real holdings and see guide prices? Use `REAL_PORTFOLIO_GUIDE.md`.

Want a clean browser table with analysis and source links? Use `RESEARCH_DASHBOARD_GUIDE.md`.

### 1. Create Alert in TradingView
- In TradingView, go to Alerts
- Create new alert on your indicator/strategy
- Set up the notification

### 2. Configure Webhook URL
In alert settings, use a public HTTPS URL. Do not use `localhost` inside TradingView:
```
Webhook URL: https://your-domain.com/api/webhook/tradingview
```

### 3. Alert Message Format (JSON)
```json
{
    "symbol": "{{ticker}}",
    "signal": "BUY",
    "confidence": 0.85,
    "secret": "your_webhook_secret_here"
}
```

Match `secret` to the `WEBHOOK_SECRET` value in your `.env` file.

## 📊 Analysis Bot Details

### Technical Analysis Bot
- Moving Averages (SMA 20, 50, 200)
- Relative Strength Index (RSI)
- MACD
- Bollinger Bands
- Average True Range (ATR)
- Volume Analysis

### Sentiment Analysis Bot
- News sentiment analysis
- Article polarity scoring
- Source reliability weighting
- Social sentiment indicators (extensible)

### ML Prediction Bot
- Random Forest regression
- Feature engineering from OHLCV data
- Price prediction for next trading day
- Confidence scoring
- Model auto-training

### Fundamental Analysis Bot
- P/E Ratio analysis
- Market Cap classification
- Dividend Yield evaluation
- Beta (volatility) assessment
- Return on Equity (ROE)
- Profit Margin analysis
- 52-week range positioning

## 🧠 Claude AI Synthesis

The AI synthesizer uses Claude's intelligence to:
1. Integrate signals from all 4 bots
2. Identify contradictions and consensus
3. Generate confidence scores
4. Provide price targets (1-week, 1-month)
5. Identify key risk factors
6. Recommend trading action

## 💰 Paper Trading Engine

Features:
- Virtual portfolio with real market prices
- Position tracking and P&L calculation
- Trade history with performance metrics
- Risk management (position sizing, stop loss, take profit)
- Performance analytics:
  - Win rate
  - Profit factor
  - Max drawdown
  - Total return

## 📈 Configuration

Edit `config.py` to customize:
- `WATCHLIST`: Stocks to monitor
- `INITIAL_CAPITAL`: Paper trading capital
- `TRADE_SIZE_PERCENT`: Position size (% of capital)
- `DATA_UPDATE_INTERVAL`: How often to refresh data
- `TECHNICAL_LOOKBACK_DAYS`: Historical data range
- `CONSENSUS_THRESHOLD`: % of bots that need to agree
- `STOP_LOSS_PERCENT`: Risk management setting
- `TAKE_PROFIT_PERCENT`: Profit target setting

## 🔒 Security Considerations

1. **API Keys**: Never commit `.env` file to version control
2. **Webhook Secret**: Set a strong secret and use it in TradingView
3. **CORS**: Configure trusted origins in production
4. **HTTPS**: Use HTTPS for production deployments
5. **Database**: Use production database (PostgreSQL/MySQL) for real trading

## 📊 Expected Output

### Dashboard shows:
- Portfolio value and positions
- Win rate and trade count
- Stock-by-stock analysis
- Buy/Sell/Neutral signals
- Confidence levels
- Trading opportunities

### Analysis includes:
- Technical signals with indicators
- Sentiment scores from news
- ML price predictions
- Fundamental strength assessment
- Claude AI synthesized recommendation

## 🚨 Risk Disclaimer

This system is for **EDUCATIONAL AND PAPER TRADING ONLY**. It should NOT be used for real trading without:
- Thorough backtesting
- Risk management implementation
- Broker integration testing
- Financial advisor consultation
- Legal compliance review

## 🛠️ Troubleshooting

### ImportError: No module named 'talib'
```bash
# On Windows
pip install TA-Lib

# Or use alternative
pip install ta
```

### API Key errors
- Verify API keys in `.env` file
- Check Anthropic console for valid API key
- Ensure keys have proper permissions

### Data fetch errors
- Check internet connection
- Verify stock symbols are correct
- Check Yahoo Finance availability

### Port already in use
```bash
# Change port in config.py
FLASK_PORT = 5001
```

## 📚 Data Sources

- **Stock Data**: Yahoo Finance (yfinance)
- **Fundamentals**: Yahoo Finance
- **News/Sentiment**: NewsAPI (optional)
- **Technical Indicators**: TA-Lib

## 🤝 Integration Examples

### Using as a Python Library
```python
from data_fetcher import DataFetcher
from technical_bot import TechnicalAnalysisBot

# Fetch data
df = DataFetcher.fetch_stock_data("AAPL", period="1y")

# Analyze
bot = TechnicalAnalysisBot()
result = bot.analyze(df, "AAPL")
print(result)
```

### Custom Alerts
```python
from sentiment_bot import SentimentAnalysisBot

bot = SentimentAnalysisBot()
sentiment = bot.analyze("TSLA")
```

## 📝 License

Educational use only. Use with proper risk management.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check logs in console output

---

**Happy Trading! 📈**

Remember: Past performance is not indicative of future results. Always trade responsibly!
