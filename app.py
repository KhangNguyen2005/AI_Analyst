from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import logging
import threading
import time
from datetime import datetime
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

from config import *
from data_fetcher import DataFetcher
from technical_bot import TechnicalAnalysisBot
from sentiment_bot import SentimentAnalysisBot
from ml_bot import MLPredictionBot
from fundamental_bot import FundamentalAnalysisBot
from ai_synthesizer import AIAnalysisSynthesizer
from paper_trading import PaperTradingEngine
from local_alerts import LocalAlertEngine
from blue_chip_screener import BlueChipScreener
from real_portfolio import RealPortfolioTracker
from trade_levels import TradeLevelCalculator

load_dotenv()

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bots and trading engine
technical_bot = TechnicalAnalysisBot()
sentiment_bot = SentimentAnalysisBot(os.getenv("NEWS_API_KEY"))
ml_bot = MLPredictionBot()
fundamental_bot = FundamentalAnalysisBot()
ai_synthesizer = AIAnalysisSynthesizer(os.getenv("GEMINI_API_KEY"))
trading_engine = PaperTradingEngine(INITIAL_CAPITAL)
local_alert_engine = LocalAlertEngine(LOCAL_ALERT_RULES_FILE, LOCAL_ALERT_EVENTS_FILE)
blue_chip_screener = BlueChipScreener(BLUE_CHIP_UNIVERSE, BLUE_CHIP_BUY_SCORE, BLUE_CHIP_SELL_SCORE)
real_portfolio_tracker = RealPortfolioTracker(REAL_PORTFOLIO_FILE)
trade_level_calculator = TradeLevelCalculator(blue_chip_screener)

# Global state
analysis_cache = {}
data_fetcher = DataFetcher()

# ============ Routes ============

@app.route("/", methods=["GET"])
def home():
    """Home page"""
    return render_template("dashboard.html")

@app.route("/api/watchlist", methods=["GET"])
def get_watchlist():
    """Get current watchlist"""
    return jsonify({"watchlist": WATCHLIST})

@app.route("/api/analyze/<symbol>", methods=["GET"])
def analyze_stock(symbol):
    """Analyze a single stock"""
    try:
        return jsonify(run_stock_analysis(symbol))

    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/analyze/all", methods=["GET"])
def analyze_all_watchlist():
    """Analyze all stocks in watchlist"""
    results = {}
    for symbol in WATCHLIST:
        try:
            results[symbol] = run_stock_analysis(symbol)
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            results[symbol] = {"error": str(e)}

    return jsonify(results)

@app.route("/api/portfolio", methods=["GET"])
def get_portfolio():
    """Get current portfolio status"""
    return jsonify(trading_engine.get_portfolio_summary())

@app.route("/api/trade", methods=["POST"])
def execute_trade():
    """Execute a paper trade"""
    try:
        data = request.json
        symbol = data.get("symbol", "").upper()
        signal = data.get("signal", "").upper()
        confidence = float(data.get("confidence", 0.5))

        if signal not in ["BUY", "SELL"]:
            return jsonify({"error": "Signal must be BUY or SELL"}), 400

        trade = trading_engine.execute_trade(symbol, signal, confidence, TRADE_SIZE_PERCENT)

        return jsonify({
            "trade": trade,
            "portfolio": trading_engine.get_portfolio_summary()
        })

    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/trades/history", methods=["GET"])
def get_trade_history():
    """Get trade history"""
    try:
        history = trading_engine.get_trade_history()
        return jsonify({
            "trades": history.to_dict('records'),
            "count": len(history)
        })
    except Exception as e:
        logger.error(f"Error fetching trade history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/performance", methods=["GET"])
def get_performance():
    """Get performance metrics"""
    return jsonify(trading_engine.update_performance_metrics())

@app.route("/api/webhook/tradingview", methods=["POST"])
def tradingview_webhook():
    """Receive alerts from TradingView"""
    try:
        data = request.get_json(silent=True) or {}

        # Verify webhook secret. TradingView webhook messages are easiest to
        # secure by placing a shared secret in the JSON body.
        provided_secret = request.headers.get("X-Webhook-Secret") or data.get("secret")
        if WEBHOOK_SECRET and provided_secret != WEBHOOK_SECRET:
            return jsonify({"error": "Unauthorized"}), 401

        symbol = data.get("symbol", "").upper()
        signal = data.get("signal", "").upper()
        confidence = float(data.get("confidence", 0.5))

        logger.info(f"TradingView Alert: {symbol} {signal} (confidence: {confidence})")

        # Execute trade based on webhook
        trade = trading_engine.execute_trade(symbol, signal, confidence, TRADE_SIZE_PERCENT)

        return jsonify({
            "status": "received",
            "trade": trade,
            "portfolio": trading_engine.get_portfolio_summary()
        })

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/local-alerts", methods=["GET"])
def get_local_alerts():
    """List local alert rules"""
    return jsonify({"alerts": local_alert_engine.list_rules()})

@app.route("/api/local-alerts", methods=["POST"])
def create_local_alert():
    """Create a local alert rule"""
    try:
        rule = local_alert_engine.add_rule(request.get_json(silent=True) or {})
        return jsonify({"alert": rule}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/local-alerts/<rule_id>", methods=["DELETE"])
def delete_local_alert(rule_id):
    """Delete a local alert rule"""
    if local_alert_engine.delete_rule(rule_id):
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Alert not found"}), 404

@app.route("/api/local-alerts/<rule_id>", methods=["PATCH"])
def update_local_alert(rule_id):
    """Enable or disable a local alert rule"""
    data = request.get_json(silent=True) or {}
    if "enabled" not in data:
        return jsonify({"error": "enabled is required"}), 400

    rule = local_alert_engine.set_enabled(rule_id, data["enabled"])
    if rule:
        return jsonify({"alert": rule})
    return jsonify({"error": "Alert not found"}), 404

@app.route("/api/local-alerts/scan", methods=["POST"])
def scan_local_alerts():
    """Run local alert scan immediately"""
    events = local_alert_engine.scan(execute_local_alert_trade, run_stock_analysis)
    return jsonify({"events": events, "count": len(events)})

@app.route("/api/local-alerts/events", methods=["GET"])
def get_local_alert_events():
    """List recent local alert events"""
    limit = int(request.args.get("limit", 25))
    return jsonify({"events": local_alert_engine.list_events(limit)})

@app.route("/api/blue-chips/scan", methods=["GET"])
def scan_blue_chips():
    """Scan blue-chip universe for buy/hold/sell candidates"""
    symbols_arg = request.args.get("symbols", "")
    symbols = [s.strip().upper() for s in symbols_arg.split(",") if s.strip()] or None
    limit = request.args.get("limit")
    limit = int(limit) if limit else None
    return jsonify(blue_chip_screener.scan(symbols=symbols, limit=limit))

@app.route("/api/trade-levels", methods=["GET"])
def get_trade_levels():
    """Get concrete buy/sell guide levels for symbols"""
    symbols_arg = request.args.get("symbols", "")
    symbols = [s.strip().upper() for s in symbols_arg.split(",") if s.strip()]
    if not symbols:
        return jsonify({"error": "symbols query param is required, e.g. TSLA,ORCL"}), 400
    return jsonify(trade_level_calculator.calculate_many(symbols))

@app.route("/api/research-table", methods=["GET"])
def get_research_table():
    """Get merged trade levels, blue-chip analysis, and research links."""
    symbols_arg = request.args.get("symbols", "TSLA,ORCL")
    symbols = [s.strip().upper() for s in symbols_arg.split(",") if s.strip()]
    if not symbols:
        return jsonify({"error": "symbols query param is required"}), 400

    level_rows = trade_level_calculator.calculate_many(symbols)["results"]
    screen_rows = blue_chip_screener.scan(symbols=symbols)["results"]
    screens_by_symbol = {row.get("symbol"): row for row in screen_rows}

    rows = []
    for levels in level_rows:
        symbol = levels.get("symbol")
        screen = screens_by_symbol.get(symbol, {})
        rows.append({
            "symbol": symbol,
            "company": screen.get("name"),
            "action": levels.get("action"),
            "signal": levels.get("signal") or screen.get("signal"),
            "score": levels.get("score") or screen.get("score"),
            "current_price": levels.get("current_price") or screen.get("current_price"),
            "preferred_buy": levels.get("preferred_buy"),
            "breakout_buy": levels.get("breakout_buy"),
            "stop_loss": levels.get("stop_loss"),
            "trim_sell": levels.get("trim_sell"),
            "take_profit": levels.get("take_profit"),
            "rsi": levels.get("rsi") or screen.get("rsi"),
            "atr": levels.get("atr"),
            "sma_20": levels.get("sma_20"),
            "sma_50": levels.get("sma_50"),
            "sma_200": levels.get("sma_200"),
            "pe_ratio": screen.get("pe_ratio"),
            "market_cap": screen.get("market_cap"),
            "sector": screen.get("sector"),
            "reason": levels.get("reason") or screen.get("reason"),
            "deeper_reason": screen.get("reason"),
            "sources": research_links(symbol),
            "error": levels.get("error") or screen.get("error"),
        })

    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "data_source": "Yahoo Finance via yfinance for market/fundamental data; linked external pages for manual verification.",
        "results": rows,
    })

@app.route("/api/real-portfolio", methods=["GET"])
def get_real_portfolio():
    """Get user-entered real portfolio with current guide prices"""
    return jsonify(real_portfolio_tracker.summary(blue_chip_screener, trade_level_calculator))

@app.route("/api/real-portfolio/holdings", methods=["POST"])
def add_real_holding():
    """Add or update a real portfolio holding"""
    try:
        data = request.get_json(silent=True) or {}
        holding = real_portfolio_tracker.add_holding(
            data.get("symbol", ""),
            float(data.get("shares", 0)),
            float(data.get("avg_cost", 0)),
            data.get("notes", ""),
        )
        return jsonify({"holding": holding}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/real-portfolio/holdings/<symbol>", methods=["DELETE"])
def remove_real_holding(symbol):
    """Remove a real portfolio holding"""
    removed = real_portfolio_tracker.remove_holding(symbol)
    if removed:
        return jsonify({"status": "deleted", "holding": removed})
    return jsonify({"error": "Holding not found"}), 404

@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    """Get dashboard data"""
    try:
        # Analyze watchlist
        results = {}
        for symbol in WATCHLIST:
            try:
                results[symbol] = run_stock_analysis(symbol)
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")

        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "portfolio": trading_engine.get_portfolio_summary(),
            "analysis": results,
            "opportunities": ai_synthesizer.identify_opportunities(results)
        }

        return jsonify(dashboard)

    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        return jsonify({"error": str(e)}), 500

# ============ Background Tasks ============

def run_stock_analysis(symbol):
    """Run full analysis and return a plain dictionary."""
    symbol = symbol.upper()

    df = data_fetcher.fetch_stock_data(symbol, period="1y")
    stock_info = data_fetcher.fetch_stock_info(symbol)

    if df is None or df.empty:
        raise ValueError(f"Could not fetch data for {symbol}")

    technical = technical_bot.analyze(df, symbol)
    sentiment = sentiment_bot.analyze(symbol)
    ml_pred = ml_bot.predict(df, symbol)
    fundamental = fundamental_bot.analyze(stock_info)

    price_info = {
        "current_price": df["Close"].iloc[-1],
        "previous_close": df["Close"].iloc[-2],
        "52_week_high": df["Close"].max(),
        "52_week_low": df["Close"].min()
    }

    synthesized = ai_synthesizer.synthesize_analysis(
        symbol, technical, sentiment, ml_pred, fundamental, price_info
    )

    analysis_cache[symbol] = {
        "timestamp": datetime.now().isoformat(),
        "technical": technical,
        "sentiment": sentiment,
        "ml_prediction": ml_pred,
        "fundamental": fundamental,
        "synthesized": synthesized
    }

    return analysis_cache[symbol]

def research_links(symbol):
    """Build external research links for manual verification."""
    encoded = quote_plus(symbol)
    return [
        {
            "label": "Yahoo",
            "url": f"https://finance.yahoo.com/quote/{encoded}",
        },
        {
            "label": "TradingView",
            "url": f"https://www.tradingview.com/chart/?symbol={encoded}",
        },
        {
            "label": "SEC",
            "url": f"https://www.sec.gov/edgar/search/#/q={encoded}",
        },
        {
            "label": "Nasdaq",
            "url": f"https://www.nasdaq.com/market-activity/stocks/{encoded.lower()}",
        },
        {
            "label": "News",
            "url": f"https://news.google.com/search?q={encoded}%20stock",
        },
    ]

def periodic_analysis():
    """Run periodic analysis"""
    while True:
        try:
            logger.info("Running periodic analysis...")
            for symbol in WATCHLIST:
                run_stock_analysis(symbol)
            time.sleep(DATA_UPDATE_INTERVAL)
        except Exception as e:
            logger.error(f"Error in periodic analysis: {e}")
            time.sleep(60)

def execute_local_alert_trade(symbol, signal, confidence):
    """Execute a paper trade from a local alert."""
    return trading_engine.execute_trade(symbol, signal, confidence, TRADE_SIZE_PERCENT)

def local_alert_monitor():
    """Scan local alerts on a timer."""
    while True:
        try:
            events = local_alert_engine.scan(execute_local_alert_trade, run_stock_analysis)
            if events:
                logger.info(f"Local alert scan triggered {len(events)} event(s)")
            time.sleep(LOCAL_ALERT_SCAN_INTERVAL)
        except Exception as e:
            logger.error(f"Error in local alert monitor: {e}")
            time.sleep(60)

# ============ Main ============

if __name__ == "__main__":
    # Start background analysis thread
    analysis_thread = threading.Thread(target=periodic_analysis, daemon=True)
    analysis_thread.start()

    local_alert_thread = threading.Thread(target=local_alert_monitor, daemon=True)
    local_alert_thread.start()

    logger.info(f"Starting AI Analyst on port {FLASK_PORT}")
    app.run(debug=FLASK_DEBUG, port=FLASK_PORT, threaded=True)
