# Real Portfolio Guide

This lets you enter your real holdings so AI Analyst can show current price, unrealized P&L, blue-chip signal, and guide prices.

It does not connect to your broker and it does not place real trades.

## Start The App

```powershell
cd C:\Users\nghkh\Downloads\AI_Analyst
python app.py
```

Open a second PowerShell window:

```powershell
cd C:\Users\nghkh\Downloads\AI_Analyst
```

## Add Your Holdings

Example:

```powershell
python cli.py real add --symbol TSLA --shares 5 --avg-cost 250
python cli.py real add --symbol ORCL --shares 10 --avg-cost 150
```

You can update a holding by running the same command again with new shares or cost.

## View Your Portfolio

```powershell
python cli.py real show
```

You will see:

```text
Symbol  Shares  Avg Cost  Current  P&L      P&L %   Signal  Action                Guide Prices
TSLA    5       $250.00   $445.00  $975.00  78.00%  HOLD    HOLD                  Buy <= ...; Risk sell < ...; Trim >= ...
ORCL    10      $150.00   $193.84  $438.40  29.23%  BUY     HOLD_OR_CONSIDER_ADD  Buy <= ...; Risk sell < ...; Trim >= ...
```

## Remove A Holding

```powershell
python cli.py real remove --symbol TSLA
```

## What The Guide Prices Mean

| Field | Meaning |
| --- | --- |
| `Buy <=` | A preferred add/buy zone based on current trend and 50-day moving average |
| `Risk sell <` | A risk-control level based on cost basis and/or 200-day moving average |
| `Trim >=` | A profit-taking or reduce-exposure level, especially when momentum is stretched |

These are rule-based guide levels, not guaranteed profitable prices.

## Get Exact Buy/Sell Guide Levels Without Entering Holdings

Use this when you want concrete levels for any symbols:

```powershell
python cli.py levels --symbols TSLA,ORCL
```

Output includes:

| Field | Meaning |
| --- | --- |
| `Buy <=` | Preferred pullback/add price |
| `Breakout Buy >=` | Momentum entry if price breaks resistance |
| `Stop/Risk Sell <` | Risk-control sell level |
| `Trim >=` | First reduce/profit-taking area |
| `Take Profit >=` | Higher profit target |

These are calculated from recent price action, moving averages, RSI, support/resistance, and ATR volatility.

## Data File

Your holdings are saved locally in:

```text
real_portfolio.json
```

Do not put account numbers, login details, or sensitive broker information in this file.
