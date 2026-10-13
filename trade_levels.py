import logging
from datetime import datetime

import pandas as pd

from blue_chip_screener import BlueChipScreener
from data_fetcher import DataFetcher
from config import STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT

logger = logging.getLogger(__name__)


class TradeLevelCalculator:
    """Calculate concrete buy/sell guide levels from price action and trend."""

    def __init__(self, screener=None):
        self.screener = screener

    def calculate_many(self, symbols):
        rows = []
        for symbol in symbols:
            try:
                rows.append(self.calculate(symbol))
            except Exception as e:
                logger.error(f"Error calculating trade levels for {symbol}: {e}")
                rows.append({
                    "symbol": symbol.upper(),
                    "action": "ERROR",
                    "error": str(e),
                })

        return {
            "timestamp": datetime.now().isoformat(),
            "count": len(rows),
            "results": rows,
        }

    def calculate(self, symbol):
        symbol = symbol.upper()
        df = DataFetcher.fetch_stock_data(symbol, period="1y", interval="1d")
        if df is None or df.empty:
            raise ValueError("No price history returned")

        close = self._series(df, "Close")
        high = self._series(df, "High")
        low = self._series(df, "Low")

        if len(close) < 50:
            raise ValueError("At least 50 daily candles are required")

        current = float(close.iloc[-1])
        sma_20 = float(close.rolling(20).mean().iloc[-1])
        sma_50 = float(close.rolling(50).mean().iloc[-1])
        sma_200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None
        rsi = float(self._rsi(close).iloc[-1])
        atr = float(self._atr(high, low, close).iloc[-1])
        support_20 = float(low.tail(20).min())
        resistance_20 = float(high.tail(20).max())
        support_50 = float(low.tail(50).min())
        resistance_50 = float(high.tail(50).max())

        screen = self.screener.analyze_symbol(symbol) if self.screener else {}
        signal = screen.get("signal", "N/A")
        score = screen.get("score")

        preferred_buy = self._preferred_buy(current, sma_20, sma_50, sma_200, rsi, atr, support_20)
        breakout_buy = resistance_20 * 1.005
        stop_loss = self._stop_loss(current, preferred_buy, sma_50, sma_200, atr, support_20, support_50)
        trim_sell = self._trim_sell(current, resistance_20, resistance_50, atr, rsi)
        take_profit = self._take_profit(current, trim_sell, atr)
        action = self._action(signal, current, preferred_buy, breakout_buy, stop_loss, rsi, sma_50, sma_200)

        return {
            "symbol": symbol,
            "action": action,
            "signal": signal,
            "score": score,
            "current_price": round(current, 2),
            "preferred_buy": round(preferred_buy, 2),
            "breakout_buy": round(breakout_buy, 2),
            "stop_loss": round(stop_loss, 2),
            "trim_sell": round(trim_sell, 2),
            "take_profit": round(take_profit, 2),
            "sma_20": round(sma_20, 2),
            "sma_50": round(sma_50, 2),
            "sma_200": round(sma_200, 2) if sma_200 else None,
            "rsi": round(rsi, 1),
            "atr": round(atr, 2),
            "support_20": round(support_20, 2),
            "resistance_20": round(resistance_20, 2),
            "reason": self._reason(action, signal, rsi, current, preferred_buy, breakout_buy, stop_loss),
        }

    @staticmethod
    def _preferred_buy(current, sma_20, sma_50, sma_200, rsi, atr, support_20):
        """
        Calculate optimal buy level based on volatility, trend, and RSI.
        Uses volatility-adjusted percentages rather than fixed ATR multiples.
        """
        # Calculate ATR as percentage of price for volatility normalization
        atr_percent = (atr / current) * 100
        
        # Base buy target is typically 0.5-1.5% below current, adjusted for volatility
        if sma_200 and current < sma_200:
            # Below long-term trend: more aggressive entry
            buy_dip = max(current - (atr_percent * 0.8 / 100 * current), sma_50 * 0.98)
            return min(buy_dip, support_20)
        
        if rsi >= 72:
            # Overbought: wait for pullback of 1.5-2.5%
            pullback = current - (atr_percent * 1.5 / 100 * current)
            return max(pullback, sma_50 * 0.98)
        
        if rsi <= 35:
            # Oversold: aggressive entry at 0.5-1% above support
            return min(current, support_20 + (atr_percent * 0.5 / 100 * current))
        
        if current > sma_20:
            # In uptrend: buy on 1-1.5% dip from current
            dip = current - (atr_percent * 1.0 / 100 * current)
            return max(dip, sma_20 * 0.98)
        
        # Default: buy between current and SMA20
        return min(current, sma_20 * 0.99)

    @staticmethod
    def _stop_loss(current, preferred_buy, sma_50, sma_200, atr, support_20, support_50):
        """
        Calculate stop loss using percentage-based approach from config,
        adjusted by market structure and trend.
        """
        # Base stop loss: STOP_LOSS_PERCENT below buy price
        base_stop = preferred_buy * (1 - STOP_LOSS_PERCENT / 100)
        
        # Never stop below the lower structure (support_50)
        structural_stop = support_50 * 0.98
        
        # If in strong downtrend, tighten stop to support_20
        if preferred_buy < support_20:
            technical_stop = support_20 * 0.97
        else:
            technical_stop = max(base_stop, support_20 * 0.96)
        
        # If price is above 200-day, use 200-day as hard floor
        if sma_200 and current > sma_200:
            technical_stop = max(technical_stop, sma_200 * 0.96)
        
        # Final stop is the maximum of technical levels (safest)
        return max(technical_stop, structural_stop)

    @staticmethod
    def _trim_sell(current, resistance_20, resistance_50, atr, rsi):
        """
        Calculate partial profit-taking (trim) level.
        More conservative than take_profit.
        Targets 2-3.5% above buy for partial exits.
        """
        # Calculate ATR as percentage for volatility
        atr_percent = (atr / current) * 100
        
        # If overbought, take profit quickly at 2% above current
        if rsi >= 75:
            return current * 1.02
        
        # If price is at resistance, partial take at resistance
        if current >= resistance_20:
            # Don't go much above resistance, only 1-1.5%
            return resistance_20 * 1.01
        
        # Normal condition: 2-2.5% above current
        trim_level = current * (1 + (atr_percent * 0.8 / 100))
        
        # Cap at resistance + 1%
        return min(trim_level, resistance_20 * 1.01)

    @staticmethod
    def _take_profit(current, trim_sell, atr):
        """
        Calculate full exit profit target using config percentage.
        Realistic risk/reward with 2:1 or 3:1 ratio depending on volatility.
        """
        # Base take profit from config: typically 5%
        base_tp = current * (1 + TAKE_PROFIT_PERCENT / 100)
        
        # Calculate ATR as percentage for volatility adjustment
        atr_percent = (atr / current) * 100
        
        # In low volatility (ATR < 1.5%), can aim for full 5%+
        if atr_percent < 1.5:
            return base_tp * 1.1  # 5.5% target in quiet markets
        
        # In normal volatility (1.5-3%), use base config percentage
        elif atr_percent < 3.0:
            return base_tp
        
        # In high volatility (>3%), reduce target to 3.5-4.5%
        else:
            return current * (1 + (TAKE_PROFIT_PERCENT * 0.75 / 100))

    @staticmethod
    def _action(signal, current, preferred_buy, breakout_buy, stop_loss, rsi, sma_50, sma_200):
        if signal == "SELL" and sma_200 and current < sma_200 * 0.97:
            return "AVOID_OR_SELL"
        if sma_200 and current < sma_200 * 0.97:
            return "WAIT_TREND_WEAK"
        if current <= stop_loss:
            return "SELL_RISK_BREAK"
        if rsi >= 75:
            return "WAIT_OR_TRIM"
        if signal == "BUY" and current <= preferred_buy * 1.01:
            return "BUY_ZONE"
        if signal == "BUY" and current >= breakout_buy:
            return "BREAKOUT_BUY"
        if current < sma_50:
            return "WAIT"
        return "HOLD_WAIT_FOR_LEVEL"

    @staticmethod
    def _reason(action, signal, rsi, current, preferred_buy, breakout_buy, stop_loss):
        if action == "BUY_ZONE":
            return f"{signal} setup; price is near calculated buy level {preferred_buy:.2f}"
        if action == "BREAKOUT_BUY":
            return f"{signal} setup; price cleared breakout level {breakout_buy:.2f}"
        if action == "WAIT_OR_TRIM":
            return f"RSI is stretched at {rsi:.1f}; avoid chasing"
        if action == "WAIT_TREND_WEAK":
            return f"Below long-term trend; wait for buy <= {preferred_buy:.2f} or breakout >= {breakout_buy:.2f}"
        if action in {"AVOID_OR_SELL", "SELL_RISK_BREAK"}:
            return f"Price is weak or near risk level {stop_loss:.2f}"
        return f"Wait for buy <= {preferred_buy:.2f} or breakout >= {breakout_buy:.2f}"

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
    def _atr(high, low, close, window=14):
        previous_close = close.shift(1)
        true_range = pd.concat(
            [
                high - low,
                (high - previous_close).abs(),
                (low - previous_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        return true_range.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
