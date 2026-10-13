import logging
from datetime import datetime

import pandas as pd

from data_fetcher import DataFetcher

logger = logging.getLogger(__name__)


class BlueChipScreener:
    """Rank large, established companies for buy/hold/sell review."""

    def __init__(self, symbols, buy_score=72, sell_score=45):
        self.symbols = symbols
        self.buy_score = buy_score
        self.sell_score = sell_score

    def scan(self, symbols=None, limit=None):
        results = []
        universe = symbols or self.symbols

        for symbol in universe:
            try:
                result = self.analyze_symbol(symbol)
                results.append(result)
            except Exception as e:
                logger.error(f"Error screening {symbol}: {e}")
                results.append({
                    "symbol": symbol,
                    "signal": "ERROR",
                    "score": 0,
                    "reason": str(e),
                })

        ranked = sorted(results, key=lambda item: item.get("score", 0), reverse=True)
        if limit:
            ranked = ranked[:limit]

        return {
            "timestamp": datetime.now().isoformat(),
            "buy_score": self.buy_score,
            "sell_score": self.sell_score,
            "count": len(ranked),
            "results": ranked,
        }

    def analyze_symbol(self, symbol):
        symbol = symbol.upper()
        df = DataFetcher.fetch_stock_data(symbol, period="1y", interval="1d")
        info = DataFetcher.fetch_stock_info(symbol) or {}

        if df is None or df.empty:
            raise ValueError("No price history returned")

        close = self._series(df, "Close")
        volume = self._series(df, "Volume")

        current_price = float(close.iloc[-1])
        previous_close = float(close.iloc[-2]) if len(close) > 1 else current_price
        sma_50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else None
        sma_200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None
        rsi = self._rsi(close).iloc[-1] if len(close) >= 15 else None
        avg_volume_30 = float(volume.rolling(30).mean().iloc[-1]) if len(volume) >= 30 else None

        market_cap = self._num(info.get("market_cap"))
        pe_ratio = self._num(info.get("pe_ratio"))
        dividend_yield = self._num(info.get("dividend_yield"))
        beta = self._num(info.get("beta"))
        profit_margins = self._num(info.get("profit_margins"))
        roe = self._num(info.get("roe"))
        high_52 = self._num(info.get("52_week_high")) or float(close.max())
        low_52 = self._num(info.get("52_week_low")) or float(close.min())

        score_parts = {
            "scale": self._scale_score(market_cap),
            "quality": self._quality_score(profit_margins, roe),
            "valuation": self._valuation_score(pe_ratio),
            "trend": self._trend_score(current_price, sma_50, sma_200),
            "risk": self._risk_score(beta, rsi),
            "shareholder_return": self._dividend_score(dividend_yield),
        }
        score = round(sum(score_parts.values()), 1)
        signal = self._signal(score, current_price, sma_200, rsi)

        reasons = self._reasons(score_parts, current_price, sma_50, sma_200, rsi, pe_ratio)
        return {
            "symbol": symbol,
            "name": info.get("name"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "signal": signal,
            "score": score,
            "score_parts": score_parts,
            "current_price": current_price,
            "daily_change_percent": round(((current_price - previous_close) / previous_close) * 100, 2) if previous_close else 0,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "rsi": round(float(rsi), 1) if rsi is not None and not pd.isna(rsi) else None,
            "market_cap": market_cap,
            "pe_ratio": pe_ratio,
            "dividend_yield": dividend_yield,
            "beta": beta,
            "profit_margins": profit_margins,
            "roe": roe,
            "52_week_position": self._range_position(current_price, low_52, high_52),
            "avg_volume_30": avg_volume_30,
            "reason": "; ".join(reasons),
        }

    def _signal(self, score, price, sma_200, rsi):
        if score >= self.buy_score and (rsi is None or rsi < 72):
            return "BUY"
        if score <= self.sell_score:
            return "SELL"
        if sma_200 and price < sma_200 * 0.94:
            return "SELL"
        return "HOLD"

    def _reasons(self, score_parts, price, sma_50, sma_200, rsi, pe_ratio):
        reasons = []
        if score_parts["scale"] >= 15:
            reasons.append("large established market cap")
        if score_parts["quality"] >= 18:
            reasons.append("strong profitability quality")
        if score_parts["valuation"] >= 14:
            reasons.append("valuation is reasonable versus blue-chip peers")
        if sma_50 and price > sma_50:
            reasons.append("price is above 50-day trend")
        if sma_200 and price > sma_200:
            reasons.append("price is above 200-day trend")
        if rsi is not None and not pd.isna(rsi):
            if rsi > 72:
                reasons.append("RSI is stretched")
            elif rsi < 35:
                reasons.append("RSI is near oversold")
        if pe_ratio and pe_ratio > 45:
            reasons.append("valuation is expensive")
        return reasons or ["mixed signal"]

    @staticmethod
    def _scale_score(market_cap):
        if not market_cap:
            return 5
        if market_cap >= 500_000_000_000:
            return 20
        if market_cap >= 200_000_000_000:
            return 17
        if market_cap >= 50_000_000_000:
            return 13
        return 7

    @staticmethod
    def _quality_score(profit_margins, roe):
        score = 0
        if profit_margins is not None:
            if profit_margins >= 0.25:
                score += 12
            elif profit_margins >= 0.15:
                score += 9
            elif profit_margins >= 0.08:
                score += 5
        if roe is not None:
            if roe >= 0.25:
                score += 13
            elif roe >= 0.15:
                score += 9
            elif roe >= 0.08:
                score += 5
        return min(score, 25)

    @staticmethod
    def _valuation_score(pe_ratio):
        if pe_ratio is None or pe_ratio <= 0:
            return 8
        if 12 <= pe_ratio <= 25:
            return 18
        if 25 < pe_ratio <= 35:
            return 14
        if 8 <= pe_ratio < 12:
            return 12
        if 35 < pe_ratio <= 50:
            return 8
        return 4

    @staticmethod
    def _trend_score(price, sma_50, sma_200):
        score = 0
        if sma_50 and price > sma_50:
            score += 8
        if sma_200 and price > sma_200:
            score += 10
        if sma_50 and sma_200 and sma_50 > sma_200:
            score += 7
        return score

    @staticmethod
    def _risk_score(beta, rsi):
        score = 10
        if beta is not None:
            if beta <= 1.2:
                score += 5
            elif beta > 1.8:
                score -= 5
        if rsi is not None and not pd.isna(rsi):
            if 40 <= rsi <= 65:
                score += 5
            elif rsi > 75:
                score -= 6
        return max(0, min(score, 20))

    @staticmethod
    def _dividend_score(dividend_yield):
        if dividend_yield is None:
            return 2
        if 0.01 <= dividend_yield <= 0.04:
            return 7
        if dividend_yield > 0.04:
            return 5
        return 3

    @staticmethod
    def _range_position(price, low, high):
        if not high or not low or high == low:
            return None
        return round(((price - low) / (high - low)) * 100, 1)

    @staticmethod
    def _series(df, column):
        series = df[column]
        if isinstance(series, pd.DataFrame):
            series = series.iloc[:, 0]
        return pd.to_numeric(series, errors="coerce").dropna()

    @staticmethod
    def _rsi(close, window=14):
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def _num(value):
        try:
            if value is None or pd.isna(value):
                return None
            return float(value)
        except (TypeError, ValueError):
            return None
