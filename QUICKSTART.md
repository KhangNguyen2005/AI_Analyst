# 🚀 Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
# Create .env file
cp .env.example .env

# Edit .env and add:
# - ANTHROPIC_API_KEY (from https://console.anthropic.com)
# - NEWS_API_KEY (optional, from https://newsapi.org)
```

### 3. Run Tests
```bash
python test_setup.py
```

### 4. Start the System
```bash
python app.py
```

### 5. Access Dashboard
Open browser: http://localhost:5000

---

## Using the System

### View Dashboard
- Real-time portfolio status
- Stock analysis with BUY/SELL signals
- Performance metrics
- Trading opportunities

### Analyze Specific Stock
```bash
curl http://localhost:5000/api/analyze/AAPL
```

### View Portfolio
```bash
curl http://localhost:5000/api/portfolio
```

### Execute Paper Trade
```bash
curl -X POST http://localhost:5000/api/trade \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "signal": "BUY",
    "confidence": 0.85
  }'
```

### Get Trade History
```bash
curl http://localhost:5000/api/trades/history
```

---

## Key Features Explained

### Signal Types
- **BUY**: Strong consensus to buy
- **SELL**: Strong consensus to sell  
- **NEUTRAL**: Mixed signals, no clear direction

### Confidence Score (0-100%)
- **80-100%**: Very strong signal
- **60-80%**: Strong signal
- **40-60%**: Moderate signal
- **<40%**: Weak signal

### Analysis Sources
1. **Technical**: Chart patterns, indicators
2. **Sentiment**: News & market sentiment
3. **ML**: Machine learning predictions
4. **Fundamental**: Company financials
5. **Claude AI**: Intelligent synthesis

---

## Integration with TradingView

### Send Alerts to AI Analyst
1. Create TradingView alert on your strategy
2. Set webhook URL: `http://your-server/api/webhook/tradingview`
3. Send JSON alert with symbol, signal, confidence
4. AI Analyst executes paper trade automatically

Example webhook message:
```json
{
    "symbol": "AAPL",
    "signal": "BUY",
    "confidence": 0.85
}
```

---

## Customization

### Change Watchlist
Edit `config.py`:
```python
WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
```

### Adjust Risk Settings
Edit `config.py`:
```python
TRADE_SIZE_PERCENT = 0.15  # Use 15% per trade
STOP_LOSS_PERCENT = 2.0    # 2% stop loss
TAKE_PROFIT_PERCENT = 5.0  # 5% profit target
```

### Update Thresholds
```python
CONSENSUS_THRESHOLD = 0.6  # 60% of bots must agree
ML_CONFIDENCE_THRESHOLD = 0.65
SENTIMENT_THRESHOLD = 0.6
```

---

## Monitoring

### Check System Health
- Dashboard auto-refreshes every 5 minutes
- API endpoints return real-time data
- Background analysis runs continuously

### View Logs
Console shows:
- Data fetch status
- Analysis results
- Trade execution
- Errors and warnings

---

## Paper Trading Performance

Track:
- **Total Return**: % gain/loss vs initial capital
- **Win Rate**: % of profitable trades
- **Profit Factor**: Gains / Losses ratio
- **Trade Count**: Number of executed trades

Example output:
```
Portfolio Value: $105,234.50
Total Return: +5.23%
Win Rate: 62%
Trades: 42
```

---

## Troubleshooting

### System won't start
1. Run `python test_setup.py`
2. Fix any failed tests
3. Check `.env` file configuration

### No analysis data
1. Verify API keys are valid
2. Check internet connection
3. Restart Flask server

### Incorrect signals
1. Check technical indicator settings in `technical_bot.py`
2. Verify ML model has enough training data
3. Adjust thresholds in `config.py`

---

## Next Steps

1. **Backtest Strategy**: Run analysis on historical data
2. **Optimize Parameters**: Find best settings for your stocks
3. **Add More Data Sources**: Integrate additional APIs
4. **Deploy to Cloud**: Run on AWS/Heroku for 24/7 monitoring
5. **Real Trading Integration**: Connect to broker API (with caution!)

---

## Important Notes

⚠️ **PAPER TRADING ONLY** - This system simulates trades with virtual money.

⚠️ **Not Financial Advice** - Do your own research before trading.

⚠️ **Risk Management** - Never risk money you can't afford to lose.

⚠️ **Test Thoroughly** - Backtest before any real trading.

---

For more info, see README.md
