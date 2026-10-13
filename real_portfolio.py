import json
from datetime import datetime
from pathlib import Path


class RealPortfolioTracker:
    """Track user-entered real holdings separately from paper trading."""

    def __init__(self, portfolio_path="real_portfolio.json"):
        self.portfolio_path = Path(portfolio_path)
        self.holdings = self.load()

    def load(self):
        if not self.portfolio_path.exists():
            return {}

        try:
            with self.portfolio_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def save(self):
        with self.portfolio_path.open("w", encoding="utf-8") as f:
            json.dump(self.holdings, f, indent=2)

    def add_holding(self, symbol, shares, avg_cost, notes=""):
        symbol = symbol.upper().strip()
        if not symbol:
            raise ValueError("symbol is required")
        if shares <= 0:
            raise ValueError("shares must be greater than 0")
        if avg_cost <= 0:
            raise ValueError("avg_cost must be greater than 0")

        self.holdings[symbol] = {
            "symbol": symbol,
            "shares": float(shares),
            "avg_cost": float(avg_cost),
            "notes": notes,
            "updated_at": datetime.now().isoformat(),
        }
        self.save()
        return self.holdings[symbol]

    def remove_holding(self, symbol):
        symbol = symbol.upper().strip()
        removed = self.holdings.pop(symbol, None)
        if removed:
            self.save()
        return removed

    def list_holdings(self):
        return list(self.holdings.values())

    def summary(self, screener, level_calculator=None):
        positions = []
        total_cost = 0.0
        total_value = 0.0

        for holding in self.list_holdings():
            symbol = holding["symbol"]
            shares = float(holding["shares"])
            avg_cost = float(holding["avg_cost"])
            cost_basis = shares * avg_cost
            total_cost += cost_basis

            try:
                screen = screener.analyze_symbol(symbol)
                current_price = float(screen["current_price"])
                market_value = shares * current_price
                total_value += market_value
                pnl = market_value - cost_basis
                pnl_percent = (pnl / cost_basis) * 100 if cost_basis else 0
                guide = self._guide_prices(screen, avg_cost)
                trade_levels = level_calculator.calculate(symbol) if level_calculator else {}

                positions.append({
                    "symbol": symbol,
                    "shares": shares,
                    "avg_cost": avg_cost,
                    "current_price": current_price,
                    "market_value": market_value,
                    "cost_basis": cost_basis,
                    "unrealized_pnl": pnl,
                    "unrealized_pnl_percent": pnl_percent,
                    "signal": screen["signal"],
                    "score": screen["score"],
                    "rsi": screen.get("rsi"),
                    "pe_ratio": screen.get("pe_ratio"),
                    "suggested_action": self._suggested_action(screen, pnl_percent),
                    "guide_prices": guide,
                    "trade_levels": trade_levels,
                    "reason": screen.get("reason"),
                    "notes": holding.get("notes", ""),
                })
            except Exception as e:
                positions.append({
                    "symbol": symbol,
                    "shares": shares,
                    "avg_cost": avg_cost,
                    "cost_basis": cost_basis,
                    "error": str(e),
                    "notes": holding.get("notes", ""),
                })

        return {
            "timestamp": datetime.now().isoformat(),
            "total_cost": total_cost,
            "total_value": total_value,
            "unrealized_pnl": total_value - total_cost,
            "unrealized_pnl_percent": ((total_value - total_cost) / total_cost) * 100 if total_cost else 0,
            "positions": positions,
        }

    @staticmethod
    def _suggested_action(screen, pnl_percent):
        signal = screen.get("signal")
        rsi = screen.get("rsi")

        if signal == "BUY":
            if rsi is not None and rsi > 70:
                return "HOLD_WAIT_FOR_PULLBACK"
            return "HOLD_OR_CONSIDER_ADD"
        if signal == "SELL":
            return "REVIEW_SELL_OR_REDUCE"
        if pnl_percent <= -8:
            return "REVIEW_RISK"
        return "HOLD"

    @staticmethod
    def _guide_prices(screen, avg_cost):
        current = float(screen["current_price"])
        sma_50 = screen.get("sma_50")
        sma_200 = screen.get("sma_200")
        rsi = screen.get("rsi")

        preferred_buy_below = current
        if sma_50:
            preferred_buy_below = min(current, float(sma_50) * 1.02)
        if rsi is not None and rsi > 70 and sma_50:
            preferred_buy_below = float(sma_50)

        risk_sell_below = avg_cost * 0.92
        if sma_200:
            risk_sell_below = max(risk_sell_below, float(sma_200) * 0.97)

        profit_trim_above = current * 1.10
        if rsi is not None and rsi > 72:
            profit_trim_above = current

        return {
            "preferred_buy_below": round(preferred_buy_below, 2),
            "risk_sell_below": round(risk_sell_below, 2),
            "profit_trim_above": round(profit_trim_above, 2),
        }
