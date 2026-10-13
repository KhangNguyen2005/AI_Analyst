#!/usr/bin/env python3
"""
CLI tool for AI Analyst
Usage: python cli.py <command> [options]
"""

import click
import requests
import json
from config import *

try:
    from tabulate import tabulate
except ImportError:
    def tabulate(rows, headers):
        all_rows = [headers] + rows
        widths = [max(len(str(row[i])) for row in all_rows) for i in range(len(headers))]
        formatted = []
        for index, row in enumerate(all_rows):
            formatted.append("  ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))))
            if index == 0:
                formatted.append("  ".join("-" * width for width in widths))
        return "\n".join(formatted)

BASE_URL = f"http://localhost:{FLASK_PORT}"

@click.group()
def cli():
    """AI Analyst CLI"""
    pass

@cli.command()
@click.option('--symbol', '-s', help='Stock symbol to analyze')
@click.option('--all', 'analyze_all', is_flag=True, help='Analyze all watchlist stocks')
def analyze(symbol, analyze_all):
    """Analyze stocks"""
    try:
        if analyze_all:
            click.echo("📊 Analyzing watchlist...")
            response = requests.get(f"{BASE_URL}/api/analyze/all")
            data = response.json()

            for sym, analysis in data.items():
                if 'error' not in analysis:
                    synth = analysis.get('synthesized', {})
                    click.echo(f"\n{sym}:")
                    click.echo(f"  Signal: {synth.get('signal')} ({synth.get('confidence', 0)}% confidence)")
                    click.echo(f"  Reasoning: {synth.get('reasoning', 'N/A')}")

        elif symbol:
            click.echo(f"📊 Analyzing {symbol.upper()}...")
            response = requests.get(f"{BASE_URL}/api/analyze/{symbol}")
            data = response.json()

            if 'error' in data:
                click.secho(f"Error: {data['error']}", fg='red')
            else:
                synth = data.get('synthesized', {})
                click.secho(f"\n{symbol.upper()} Analysis:", fg='cyan', bold=True)
                click.echo(f"Signal: {synth.get('signal')}")
                click.echo(f"Confidence: {synth.get('confidence', 0)}%")
                click.echo(f"Reasoning: {synth.get('reasoning', 'N/A')}")

                if 'key_factors' in synth:
                    click.echo("Key Factors:")
                    for factor in synth['key_factors']:
                        click.echo(f"  • {factor}")

                if 'risk_factors' in synth:
                    click.echo("Risk Factors:")
                    for risk in synth['risk_factors']:
                        click.echo(f"  ⚠ {risk}")

        else:
            click.secho("Error: Specify --symbol or --all", fg='red')

    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@cli.command()
def portfolio():
    """Show portfolio status"""
    try:
        click.echo("💼 Portfolio Status")
        response = requests.get(f"{BASE_URL}/api/portfolio")
        data = response.json()

        click.echo(f"Total Value: ${data.get('total_value', 0):.2f}")
        click.echo(f"Cash: ${data.get('cash', 0):.2f}")
        click.echo(f"Positions: {data.get('positions', 0)}")

        if data.get('positions_detail'):
            click.echo("\nOpen Positions:")
            positions = []
            for pos in data['positions_detail']:
                positions.append([
                    pos['symbol'],
                    f"{pos['shares']:.2f}",
                    f"${pos['entry_price']:.2f}",
                    f"${pos['current_price']:.2f}",
                    f"${pos['unrealized_profit']:.2f}",
                    f"{pos['unrealized_profit_percent']:.2f}%"
                ])

            click.echo(tabulate(positions, headers=['Symbol', 'Shares', 'Entry', 'Current', 'P&L', 'Return']))

    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@cli.command()
def performance():
    """Show performance metrics"""
    try:
        click.echo("📈 Performance Metrics")
        response = requests.get(f"{BASE_URL}/api/performance")
        data = response.json()

        metrics = [
            ['Total Return', f"{data.get('total_return', 0)*100:.2f}%"],
            ['Win Rate', f"{data.get('win_rate', 0)*100:.2f}%"],
            ['Winning Trades', str(data.get('winning_trades', 0))],
            ['Losing Trades', str(data.get('losing_trades', 0))],
            ['Profit Factor', f"{data.get('profit_factor', 0):.2f}"],
        ]

        click.echo(tabulate(metrics, headers=['Metric', 'Value']))

    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@cli.command()
def trades():
    """Show trade history"""
    try:
        click.echo("📝 Trade History")
        response = requests.get(f"{BASE_URL}/api/trades/history")
        data = response.json()

        if data.get('trades'):
            trades_list = []
            for trade in data['trades'][-10:]:  # Show last 10 trades
                trades_list.append([
                    trade.get('symbol'),
                    trade.get('signal'),
                    f"{trade.get('confidence', 0):.2f}",
                    f"${trade.get('price', 0):.2f}",
                    trade.get('status'),
                    f"${trade.get('profit', 0):.2f}" if 'profit' in trade else 'N/A'
                ])

            click.echo(tabulate(trades_list, headers=['Symbol', 'Signal', 'Confidence', 'Price', 'Status', 'P&L']))
            click.echo(f"\nTotal trades: {data.get('count', 0)}")
        else:
            click.echo("No trades yet")

    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@cli.command("levels")
@click.option("--symbols", "-s", required=True, help="Comma-separated symbols, e.g. TSLA,ORCL")
def trade_levels(symbols):
    """Show exact buy/sell guide levels"""
    try:
        response = requests.get(f"{BASE_URL}/api/trade-levels", params={"symbols": symbols})
        data = response.json()

        if "error" in data:
            click.secho(data["error"], fg='red')
            return

        rows = []
        for item in data.get("results", []):
            if item.get("action") == "ERROR":
                rows.append([
                    item.get("symbol"),
                    "ERROR",
                    "",
                    "",
                    "",
                    "",
                    "",
                    item.get("error"),
                ])
                continue

            rows.append([
                item.get("symbol"),
                item.get("action"),
                f"${item.get('current_price', 0):.2f}",
                f"${item.get('preferred_buy', 0):.2f}",
                f"${item.get('breakout_buy', 0):.2f}",
                f"${item.get('stop_loss', 0):.2f}",
                f"${item.get('trim_sell', 0):.2f}",
                f"${item.get('take_profit', 0):.2f}",
                f"{item.get('rsi', 0):.1f}",
                item.get("reason", ""),
            ])

        click.echo(tabulate(rows, headers=[
            "Symbol", "Action", "Current", "Buy <=", "Breakout Buy >=",
            "Stop/Risk Sell <", "Trim >=", "Take Profit >=", "RSI", "Reason"
        ]))
    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@cli.command()
@click.option('--symbol', '-s', required=True, help='Stock symbol')
@click.option('--signal', '-sig', required=True, type=click.Choice(['BUY', 'SELL']), help='Trade signal')
@click.option('--confidence', '-c', default=0.7, type=float, help='Confidence level (0-1)')
def trade(symbol, signal, confidence):
    """Execute a paper trade"""
    try:
        click.echo(f"📌 Executing {signal} trade for {symbol}...")

        payload = {
            'symbol': symbol.upper(),
            'signal': signal,
            'confidence': confidence
        }

        response = requests.post(f"{BASE_URL}/api/trade", json=payload)
        data = response.json()

        if 'trade' in data and data['trade']['status'] == 'executed':
            click.secho(f"✓ Trade executed successfully!", fg='green')
            click.echo(f"Symbol: {data['trade']['symbol']}")
            click.echo(f"Signal: {data['trade']['signal']}")

            portfolio_data = data.get('portfolio', {})
            click.echo(f"\nNew Portfolio Value: ${portfolio_data.get('total_value', 0):.2f}")
            click.echo(f"Cash: ${portfolio_data.get('cash', 0):.2f}")
        else:
            click.secho(f"✗ Trade not executed", fg='red')
            if 'error' in data:
                click.echo(f"Error: {data['error']}")

    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@cli.group()
def alerts():
    """Manage local alerts without TradingView webhooks"""
    pass

@alerts.command("list")
def list_alerts():
    """List local alert rules"""
    try:
        response = requests.get(f"{BASE_URL}/api/local-alerts")
        data = response.json()
        alert_rows = []

        for alert in data.get("alerts", []):
            trigger = alert.get("threshold", "")
            if alert.get("type") == "analysis_signal":
                trigger = f">= {alert.get('min_confidence', 65)}%"
            if alert.get("type", "").startswith("sma_cross"):
                trigger = f"{alert.get('short_window', 20)}/{alert.get('long_window', 50)}"

            alert_rows.append([
                alert.get("id"),
                alert.get("symbol"),
                alert.get("type"),
                trigger,
                alert.get("signal"),
                alert.get("enabled"),
                alert.get("last_triggered_at") or "",
            ])

        if alert_rows:
            click.echo(tabulate(alert_rows, headers=[
                "ID", "Symbol", "Type", "Trigger", "Signal", "Enabled", "Last Triggered"
            ]))
        else:
            click.echo("No local alerts configured")
    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@alerts.command("add-price")
@click.option("--symbol", "-s", required=True, help="Stock symbol")
@click.option("--above", type=float, help="Trigger when price is above this value")
@click.option("--below", type=float, help="Trigger when price is below this value")
@click.option("--signal", required=True, type=click.Choice(["BUY", "SELL"]), help="Signal to send")
@click.option("--confidence", default=0.7, type=float, help="Confidence level 0-1")
def add_price_alert(symbol, above, below, signal, confidence):
    """Add a local price alert"""
    if (above is None and below is None) or (above is not None and below is not None):
        click.secho("Use exactly one of --above or --below", fg='red')
        return

    rule = {
        "symbol": symbol,
        "type": "price_above" if above is not None else "price_below",
        "threshold": above if above is not None else below,
        "signal": signal,
        "confidence": confidence,
    }
    _create_alert(rule)

@alerts.command("add-rsi")
@click.option("--symbol", "-s", required=True, help="Stock symbol")
@click.option("--above", type=float, help="Trigger when RSI is above this value")
@click.option("--below", type=float, help="Trigger when RSI is below this value")
@click.option("--signal", required=True, type=click.Choice(["BUY", "SELL"]), help="Signal to send")
@click.option("--confidence", default=0.7, type=float, help="Confidence level 0-1")
@click.option("--window", default=14, type=int, help="RSI window")
def add_rsi_alert(symbol, above, below, signal, confidence, window):
    """Add a local RSI alert"""
    if (above is None and below is None) or (above is not None and below is not None):
        click.secho("Use exactly one of --above or --below", fg='red')
        return

    rule = {
        "symbol": symbol,
        "type": "rsi_above" if above is not None else "rsi_below",
        "threshold": above if above is not None else below,
        "rsi_window": window,
        "signal": signal,
        "confidence": confidence,
    }
    _create_alert(rule)

@alerts.command("add-sma-cross")
@click.option("--symbol", "-s", required=True, help="Stock symbol")
@click.option("--direction", required=True, type=click.Choice(["above", "below"]), help="Short SMA crosses above/below long SMA")
@click.option("--signal", required=True, type=click.Choice(["BUY", "SELL"]), help="Signal to send")
@click.option("--confidence", default=0.7, type=float, help="Confidence level 0-1")
@click.option("--short-window", default=20, type=int, help="Short SMA window")
@click.option("--long-window", default=50, type=int, help="Long SMA window")
def add_sma_cross_alert(symbol, direction, signal, confidence, short_window, long_window):
    """Add a local SMA crossover alert"""
    rule = {
        "symbol": symbol,
        "type": "sma_cross_above" if direction == "above" else "sma_cross_below",
        "short_window": short_window,
        "long_window": long_window,
        "signal": signal,
        "confidence": confidence,
    }
    _create_alert(rule)

@alerts.command("add-analysis")
@click.option("--symbol", "-s", required=True, help="Stock symbol")
@click.option("--signal", default="AUTO", type=click.Choice(["AUTO", "BUY", "SELL"]), help="Which AI signal should trigger")
@click.option("--min-confidence", default=65, type=float, help="Minimum AI confidence percent")
@click.option("--execute-trade/--no-execute-trade", default=False, help="Execute paper trade when triggered")
@click.option("--cooldown-minutes", default=240, type=int, help="Minutes before the same alert can trigger again")
def add_analysis_alert(symbol, signal, min_confidence, execute_trade, cooldown_minutes):
    """Alert from the app's synthesized AI analysis"""
    rule = {
        "symbol": symbol,
        "type": "analysis_signal",
        "signal": signal,
        "min_confidence": min_confidence,
        "execute_trade": execute_trade,
        "cooldown_minutes": cooldown_minutes,
    }
    _create_alert(rule)

@alerts.command("delete")
@click.argument("alert_id")
def delete_alert(alert_id):
    """Delete a local alert rule"""
    try:
        response = requests.delete(f"{BASE_URL}/api/local-alerts/{alert_id}")
        data = response.json()
        if response.status_code == 200:
            click.secho("Alert deleted", fg='green')
        else:
            click.secho(data.get("error", "Delete failed"), fg='red')
    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@alerts.command("scan")
def scan_alerts():
    """Run a local alert scan now"""
    try:
        response = requests.post(f"{BASE_URL}/api/local-alerts/scan")
        data = response.json()
        click.echo(f"Triggered events: {data.get('count', 0)}")
        for event in data.get("events", []):
            click.echo(f"{event['symbol']} {event['signal']} via {event['type']}")
    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@alerts.command("events")
@click.option("--limit", default=10, type=int, help="Number of recent events")
def alert_events(limit):
    """Show recent local alert events"""
    try:
        response = requests.get(f"{BASE_URL}/api/local-alerts/events", params={"limit": limit})
        data = response.json()
        rows = []

        for event in data.get("events", []):
            details = event.get("details", {})
            rows.append([
                event.get("triggered_at"),
                event.get("symbol"),
                event.get("signal"),
                f"{event.get('confidence', 0) * 100:.1f}%",
                event.get("type"),
                details.get("action_summary") or details.get("reasoning") or "",
            ])

        if rows:
            click.echo(tabulate(rows, headers=[
                "Triggered", "Symbol", "Signal", "Confidence", "Type", "Summary"
            ]))
        else:
            click.echo("No alert events yet")
    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@cli.group()
def bluechips():
    """Find blue-chip buy/hold/sell candidates"""
    pass

@bluechips.command("scan")
@click.option("--symbols", help="Comma-separated symbols, e.g. TSLA,ORCL")
@click.option("--limit", default=15, type=int, help="Number of ranked results to show")
@click.option("--signal", type=click.Choice(["ALL", "BUY", "HOLD", "SELL"]), default="ALL", help="Filter by signal")
def scan_bluechips(symbols, limit, signal):
    """Scan blue-chip stocks and rank recommendations"""
    try:
        params = {"limit": limit}
        if symbols:
            params["symbols"] = symbols

        response = requests.get(f"{BASE_URL}/api/blue-chips/scan", params=params)
        data = response.json()
        rows = []

        for item in data.get("results", []):
            if signal != "ALL" and item.get("signal") != signal:
                continue
            rows.append([
                item.get("symbol"),
                item.get("signal"),
                item.get("score"),
                f"${item.get('current_price', 0):.2f}",
                f"{item.get('rsi', 0):.1f}" if item.get("rsi") is not None else "N/A",
                f"{item.get('pe_ratio', 0):.1f}" if item.get("pe_ratio") is not None else "N/A",
                _format_market_cap(item.get("market_cap")),
                item.get("reason", ""),
            ])

        if rows:
            click.echo(tabulate(rows, headers=[
                "Symbol", "Signal", "Score", "Price", "RSI", "P/E", "Market Cap", "Reason"
            ]))
        else:
            click.echo("No blue-chip results matched your filter")
    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@bluechips.command("watch")
@click.option("--symbols", default="TSLA,ORCL", help="Comma-separated symbols to watch with AI analysis alerts")
@click.option("--min-confidence", default=65, type=float, help="Minimum AI confidence percent")
def watch_bluechips(symbols, min_confidence):
    """Create AI suggestion alerts for selected blue-chip symbols"""
    for symbol in [s.strip().upper() for s in symbols.split(",") if s.strip()]:
        _create_alert({
            "symbol": symbol,
            "type": "analysis_signal",
            "signal": "AUTO",
            "min_confidence": min_confidence,
            "execute_trade": False,
            "cooldown_minutes": 240,
        })

def _format_market_cap(value):
    if value is None:
        return "N/A"
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    return f"${value / 1_000_000:.1f}M"

@cli.group()
def real():
    """Track your real portfolio holdings"""
    pass

@real.command("add")
@click.option("--symbol", "-s", required=True, help="Stock symbol")
@click.option("--shares", required=True, type=float, help="Number of shares owned")
@click.option("--avg-cost", required=True, type=float, help="Average cost per share")
@click.option("--notes", default="", help="Optional note")
def add_real_holding(symbol, shares, avg_cost, notes):
    """Add or update a real holding"""
    try:
        response = requests.post(f"{BASE_URL}/api/real-portfolio/holdings", json={
            "symbol": symbol,
            "shares": shares,
            "avg_cost": avg_cost,
            "notes": notes,
        })
        data = response.json()
        if response.status_code == 201:
            holding = data["holding"]
            click.secho("Holding saved", fg='green')
            click.echo(f"{holding['symbol']}: {holding['shares']} shares @ ${holding['avg_cost']:.2f}")
        else:
            click.secho(data.get("error", "Save failed"), fg='red')
    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@real.command("remove")
@click.option("--symbol", "-s", required=True, help="Stock symbol")
def remove_real_holding(symbol):
    """Remove a real holding"""
    try:
        response = requests.delete(f"{BASE_URL}/api/real-portfolio/holdings/{symbol}")
        data = response.json()
        if response.status_code == 200:
            click.secho("Holding removed", fg='green')
        else:
            click.secho(data.get("error", "Remove failed"), fg='red')
    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@real.command("show")
def show_real_portfolio():
    """Show real portfolio with current guide prices"""
    try:
        response = requests.get(f"{BASE_URL}/api/real-portfolio")
        data = response.json()
        rows = []

        for pos in data.get("positions", []):
            if "error" in pos:
                rows.append([
                    pos.get("symbol"),
                    pos.get("shares"),
                    f"${pos.get('avg_cost', 0):.2f}",
                    "ERROR",
                    "",
                    "",
                    "",
                    "",
                    pos.get("error"),
                ])
                continue

            guide = pos.get("guide_prices", {})
            levels = pos.get("trade_levels", {})
            rows.append([
                pos.get("symbol"),
                f"{pos.get('shares', 0):.4g}",
                f"${pos.get('avg_cost', 0):.2f}",
                f"${pos.get('current_price', 0):.2f}",
                f"${pos.get('unrealized_pnl', 0):.2f}",
                f"{pos.get('unrealized_pnl_percent', 0):.2f}%",
                pos.get("signal"),
                pos.get("suggested_action"),
                f"Buy <= ${levels.get('preferred_buy', guide.get('preferred_buy_below', 0)):.2f}; Stop < ${levels.get('stop_loss', guide.get('risk_sell_below', 0)):.2f}; Trim >= ${levels.get('trim_sell', guide.get('profit_trim_above', 0)):.2f}; TP >= ${levels.get('take_profit', 0):.2f}",
            ])

        if rows:
            click.echo(tabulate(rows, headers=[
                "Symbol", "Shares", "Avg Cost", "Current", "P&L", "P&L %", "Signal", "Action", "Guide Prices"
            ]))
            click.echo("")
            click.echo(f"Total value: ${data.get('total_value', 0):.2f}")
            click.echo(f"Total P&L: ${data.get('unrealized_pnl', 0):.2f} ({data.get('unrealized_pnl_percent', 0):.2f}%)")
        else:
            click.echo("No real holdings entered yet")
    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

def _create_alert(rule):
    try:
        response = requests.post(f"{BASE_URL}/api/local-alerts", json=rule)
        data = response.json()
        if response.status_code == 201:
            alert = data["alert"]
            click.secho("Alert created", fg='green')
            click.echo(f"ID: {alert['id']}")
            click.echo(f"{alert['symbol']} {alert['type']} -> {alert['signal']}")
        else:
            click.secho(data.get("error", "Create failed"), fg='red')
    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@cli.command()
@click.option('--symbol', '-s', help='Specific stock symbol')
def dashboard(symbol):
    """Show dashboard data"""
    try:
        click.echo("📊 Dashboard")
        response = requests.get(f"{BASE_URL}/api/dashboard")
        data = response.json()

        # Portfolio
        portfolio = data.get('portfolio', {})
        click.secho("\n💼 Portfolio", bold=True, fg='cyan')
        click.echo(f"Total Value: ${portfolio.get('total_value', 0):.2f}")
        click.echo(f"Cash: ${portfolio.get('cash', 0):.2f}")
        click.echo(f"Return: {portfolio.get('performance', {}).get('total_return', 0)*100:.2f}%")

        # Analysis
        click.secho("\n📈 Stock Analysis", bold=True, fg='cyan')
        analysis = data.get('analysis', {})

        for sym, result in analysis.items():
            if 'error' not in result:
                synth = result.get('synthesized', {})
                signal = synth.get('signal', 'N/A')
                confidence = synth.get('confidence', 0)

                signal_color = 'green' if signal == 'BUY' else 'red' if signal == 'SELL' else 'yellow'
                click.secho(f"  {sym}: ", nl=False, fg='white', bold=True)
                click.secho(f"{signal}", fg=signal_color, bold=True, nl=False)
                click.echo(f" ({confidence}%)")

    except Exception as e:
        click.secho(f"Error: {e}", fg='red')

@cli.command()
def status():
    """Check system status"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            click.secho("✓ System running", fg='green')
            click.echo(f"Endpoint: {BASE_URL}")
        else:
            click.secho("✗ System not responding", fg='red')
    except Exception as e:
        click.secho(f"✗ Cannot connect: {e}", fg='red')

if __name__ == '__main__':
    cli()
