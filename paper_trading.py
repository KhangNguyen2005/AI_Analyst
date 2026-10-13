import pandas as pd
import logging
from datetime import datetime
from data_fetcher import DataFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaperTradingEngine:
    """Simulate paper trading for performance comparison"""

    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.current_cash = initial_capital
        self.positions = {}  # {symbol: {shares, entry_price, entry_date}}
        self.trades = []  # History of all trades
        self.portfolio_history = []  # Daily portfolio values
        self.performance = {
            "total_return": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "max_drawdown": 0,
            "profit_factor": 0
        }

    def get_portfolio_value(self):
        """Calculate current portfolio value"""
        total_value = self.current_cash

        for symbol, position in self.positions.items():
            current_price = DataFetcher.get_current_price(symbol)
            if current_price:
                total_value += position["shares"] * current_price

        return total_value

    def execute_trade(self, symbol, signal, confidence, trade_size_percent=0.1):
        """Execute a paper trade based on signal"""
        try:
            current_price = DataFetcher.get_current_price(symbol)
            if not current_price:
                logger.warning(f"Could not get price for {symbol}")
                return None

            portfolio_value = self.get_portfolio_value()
            trade_amount = portfolio_value * trade_size_percent * confidence

            trade = {
                "symbol": symbol,
                "timestamp": datetime.now(),
                "signal": signal,
                "confidence": confidence,
                "price": current_price,
                "status": "pending"
            }

            if signal == "BUY":
                # Calculate shares to buy
                shares = trade_amount / current_price

                if shares > 0 and self.current_cash >= trade_amount:
                    # Execute buy
                    self.positions[symbol] = {
                        "shares": self.positions.get(symbol, {}).get("shares", 0) + shares,
                        "entry_price": current_price,
                        "entry_date": datetime.now(),
                        "initial_investment": trade_amount
                    }
                    self.current_cash -= trade_amount
                    trade["status"] = "executed"
                    trade["shares"] = shares
                    trade["amount"] = trade_amount

                    logger.info(f"BUY: {shares:.2f} shares of {symbol} at ${current_price:.2f}")

            elif signal == "SELL":
                # Sell existing position
                if symbol in self.positions:
                    position = self.positions[symbol]
                    shares = position["shares"]
                    sale_amount = shares * current_price
                    profit = sale_amount - position["initial_investment"]
                    profit_percent = (profit / position["initial_investment"]) * 100

                    self.current_cash += sale_amount
                    trade["status"] = "executed"
                    trade["shares"] = shares
                    trade["sale_amount"] = sale_amount
                    trade["profit"] = profit
                    trade["profit_percent"] = profit_percent

                    # Track winning/losing trades
                    if profit > 0:
                        self.performance["winning_trades"] += 1
                    else:
                        self.performance["losing_trades"] += 1

                    del self.positions[symbol]
                    logger.info(f"SELL: {shares:.2f} shares of {symbol} at ${current_price:.2f}, Profit: ${profit:.2f} ({profit_percent:.2f}%)")

            self.trades.append(trade)
            return trade

        except Exception as e:
            logger.error(f"Error executing trade for {symbol}: {e}")
            return None

    def update_performance_metrics(self):
        """Update performance metrics"""
        try:
            total_trades = self.performance["winning_trades"] + self.performance["losing_trades"]

            if total_trades > 0:
                self.performance["win_rate"] = self.performance["winning_trades"] / total_trades

            portfolio_value = self.get_portfolio_value()
            total_return = (portfolio_value - self.initial_capital) / self.initial_capital

            self.performance["total_return"] = total_return

            # Calculate profit factor
            winning_amount = sum(t.get("profit", 0) for t in self.trades if t.get("profit", 0) > 0)
            losing_amount = abs(sum(t.get("profit", 0) for t in self.trades if t.get("profit", 0) < 0))

            if losing_amount > 0:
                self.performance["profit_factor"] = winning_amount / losing_amount
            else:
                self.performance["profit_factor"] = float('inf') if winning_amount > 0 else 1.0

            return self.performance

        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
            return self.performance

    def get_portfolio_summary(self):
        """Get current portfolio summary"""
        summary = {
            "total_value": self.get_portfolio_value(),
            "cash": self.current_cash,
            "positions": len(self.positions),
            "positions_detail": [],
            "performance": self.update_performance_metrics()
        }

        for symbol, position in self.positions.items():
            current_price = DataFetcher.get_current_price(symbol)
            if current_price:
                unrealized_profit = (current_price - position["entry_price"]) * position["shares"]
                unrealized_profit_percent = (unrealized_profit / position["initial_investment"]) * 100

                summary["positions_detail"].append({
                    "symbol": symbol,
                    "shares": position["shares"],
                    "entry_price": position["entry_price"],
                    "current_price": current_price,
                    "unrealized_profit": unrealized_profit,
                    "unrealized_profit_percent": unrealized_profit_percent,
                    "entry_date": position["entry_date"].isoformat()
                })

        return summary

    def get_trade_history(self):
        """Get trade history"""
        return pd.DataFrame(self.trades)

    def export_performance_report(self):
        """Export performance report"""
        report = {
            "summary": self.get_portfolio_summary(),
            "trades": [t for t in self.trades],
            "performance_metrics": self.performance
        }
        return report
