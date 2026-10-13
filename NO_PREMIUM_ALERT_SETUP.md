# No-Premium Alert Setup

TradingView webhooks require a paid TradingView plan and 2-factor authentication. If you do not have webhook access, use this local alert scanner instead.

The scanner runs inside AI Analyst, checks market data with `yfinance`, and triggers the same paper-trading flow that the TradingView webhook uses.

## Start AI Analyst

```powershell
python app.py
```

The app now starts two background jobs:

- Periodic AI analysis
- Local alert scanner

Local alert rules are saved in:

```text
local_alerts.json
```

The scan interval is controlled in `.env`:

```env
LOCAL_ALERT_SCAN_INTERVAL=60
LOCAL_ALERT_RULES_FILE=local_alerts.json
```

## Add Alerts From The CLI

Open a second terminal while `python app.py` is running.

### Price Alert

Buy AAPL when price is above 200:

```powershell
python cli.py alerts add-price --symbol AAPL --above 200 --signal BUY --confidence 0.75
```

Sell AAPL when price is below 180:

```powershell
python cli.py alerts add-price --symbol AAPL --below 180 --signal SELL --confidence 0.80
```

### RSI Alert

Buy when RSI is below 30:

```powershell
python cli.py alerts add-rsi --symbol AAPL --below 30 --signal BUY --confidence 0.70
```

Sell when RSI is above 70:

```powershell
python cli.py alerts add-rsi --symbol AAPL --above 70 --signal SELL --confidence 0.70
```

### SMA Crossover Alert

Buy when the 20-day SMA crosses above the 50-day SMA:

```powershell
python cli.py alerts add-sma-cross --symbol AAPL --direction above --signal BUY --short-window 20 --long-window 50 --confidence 0.80
```

Sell when the 20-day SMA crosses below the 50-day SMA:

```powershell
python cli.py alerts add-sma-cross --symbol AAPL --direction below --signal SELL --short-window 20 --long-window 50 --confidence 0.80
```

### AI Analysis Suggestion Alert

Use this when you want AI Analyst to run its full analysis and alert you when it has a strong BUY or SELL suggestion.

Alert on either BUY or SELL for Tesla with at least 65% confidence:

```powershell
python cli.py alerts add-analysis --symbol TSLA --signal AUTO --min-confidence 65
```

Alert on either BUY or SELL for Oracle with at least 65% confidence:

```powershell
python cli.py alerts add-analysis --symbol ORCL --signal AUTO --min-confidence 65
```

By default, analysis alerts only save the suggestion. They do not execute a paper trade. To also paper trade when the alert triggers, add:

```powershell
--execute-trade
```

Example:

```powershell
python cli.py alerts add-analysis --symbol TSLA --signal BUY --min-confidence 70 --execute-trade
```

## Manage Alerts

List alerts:

```powershell
python cli.py alerts list
```

Run a scan immediately:

```powershell
python cli.py alerts scan
```

Show recent alert suggestions:

```powershell
python cli.py alerts events
```

Delete an alert:

```powershell
python cli.py alerts delete ALERT_ID
```

## API Endpoints

List local alerts:

```text
GET /api/local-alerts
```

Create a local alert:

```text
POST /api/local-alerts
```

Manual scan:

```text
POST /api/local-alerts/scan
```

Delete an alert:

```text
DELETE /api/local-alerts/<alert_id>
```

## Example Raw API Request

```powershell
$body = @{
  symbol = "AAPL"
  type = "price_above"
  threshold = 200
  signal = "BUY"
  confidence = 0.75
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:5000/api/local-alerts" `
  -ContentType "application/json" `
  -Body $body
```

## Supported Rule Types

| Type | Meaning | Required fields |
| --- | --- | --- |
| `price_above` | Trigger when latest close is above a level | `symbol`, `threshold`, `signal` |
| `price_below` | Trigger when latest close is below a level | `symbol`, `threshold`, `signal` |
| `rsi_above` | Trigger when RSI is above a level | `symbol`, `threshold`, `signal` |
| `rsi_below` | Trigger when RSI is below a level | `symbol`, `threshold`, `signal` |
| `sma_cross_above` | Trigger when short SMA crosses above long SMA | `symbol`, `short_window`, `long_window`, `signal` |
| `sma_cross_below` | Trigger when short SMA crosses below long SMA | `symbol`, `short_window`, `long_window`, `signal` |
| `analysis_signal` | Trigger when AI Analyst recommends BUY or SELL above a confidence threshold | `symbol`, `signal`, `min_confidence` |

## Notes

- This does not need TradingView Premium or TradingView webhooks.
- It uses Yahoo Finance data through `yfinance`, so it is best for paper trading and alerts, not broker-grade execution.
- Use TradingView's free in-app alerts manually if you still want visual/chart notifications.
- Keep `python app.py` running for the scanner to work.
