# Research Dashboard Guide

Use this when terminal tables feel too messy.

## Start The App

```powershell
cd C:\Users\nghkh\Downloads\AI_Analyst
python app.py
```

Open your browser:

```text
http://localhost:5000
```

## What You Will See

The browser dashboard shows a clean table with:

- symbol and company
- action
- blue-chip signal
- score
- current price
- buy-below level
- breakout-buy level
- stop/risk-sell level
- trim level
- take-profit level
- RSI
- P/E
- market cap
- analysis reason
- source links

## Source Links

Each row includes links for deeper research:

- Yahoo Finance
- TradingView chart
- SEC filings search
- Nasdaq page
- Google News search

The app still calculates prices and indicators from Yahoo Finance through `yfinance`. The source links are for manual verification and deeper context.

## API

You can also get the same table data as JSON:

```text
http://localhost:5000/api/research-table?symbols=TSLA,ORCL
```

For more symbols:

```text
http://localhost:5000/api/research-table?symbols=AAPL,MSFT,NVDA,TSLA,ORCL
```
