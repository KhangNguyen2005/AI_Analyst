# Blue-Chip Signal Guide

Goal: gather data on established blue-chip stocks, rank them, and suggest when to BUY, HOLD, or SELL.

This scanner uses Yahoo Finance data through `yfinance`. Treat the output as a research assistant for paper trading and review, not as guaranteed investment advice.

## Start The App

```powershell
cd C:\Users\nghkh\Downloads\AI_Analyst
python app.py
```

## Scan The Default Blue-Chip List

In a second PowerShell window:

```powershell
cd C:\Users\nghkh\Downloads\AI_Analyst
python cli.py bluechips scan
```

Show only BUY candidates:

```powershell
python cli.py bluechips scan --signal BUY --limit 20
```

## Scan Tesla And Oracle

```powershell
python cli.py bluechips scan --symbols TSLA,ORCL
```

## Get Exact Buy And Sell Guide Prices

```powershell
python cli.py levels --symbols TSLA,ORCL
```

This prints exact calculated levels for:

- preferred buy price
- breakout buy price
- stop/risk sell price
- trim price
- take-profit price

## Create AI Suggestion Alerts For Tesla And Oracle

This creates local alerts that run AI Analyst's full analysis and save a suggestion when the signal is BUY or SELL with at least 65% confidence.

```powershell
python cli.py bluechips watch --symbols TSLA,ORCL --min-confidence 65
```

View alert rules:

```powershell
python cli.py alerts list
```

Run alerts immediately:

```powershell
python cli.py alerts scan
```

View triggered suggestions:

```powershell
python cli.py alerts events
```

## What The Screener Scores

The blue-chip scanner scores each stock from these buckets:

| Bucket | What it checks |
| --- | --- |
| Scale | Large market capitalization |
| Quality | Profit margins and return on equity |
| Valuation | P/E ratio range |
| Trend | Price versus 50-day and 200-day moving averages |
| Risk | Beta and RSI |
| Shareholder return | Dividend yield |

Signals:

| Signal | Meaning |
| --- | --- |
| BUY | High score, trend support, and not badly overbought |
| HOLD | Mixed or decent setup, but not strong enough for BUY |
| SELL | Weak score or bearish long-term trend |

## Change The Blue-Chip Universe

Edit `BLUE_CHIP_UNIVERSE` in `config.py`.

Default examples include:

```text
AAPL, MSFT, NVDA, GOOGL, AMZN, META, TSLA, AVGO, ORCL, CRM,
BRK-B, JPM, V, MA, UNH, JNJ, PG, COST, WMT, HD, KO, PEP,
XOM, CVX, CAT
```

## API

Scan the default universe:

```text
GET /api/blue-chips/scan
```

Scan selected symbols:

```text
GET /api/blue-chips/scan?symbols=TSLA,ORCL
```

Limit results:

```text
GET /api/blue-chips/scan?limit=10
```
