import talib
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechnicalAnalysisBot:
    """Analyze stocks using technical indicators"""

    def __init__(self):
        self.name = "Technical Analysis Bot"
        self.signals = {}

    def analyze(self, df, symbol):
        """Comprehensive technical analysis"""
        try:
            if df is None or len(df) < 50:
                return {"symbol": symbol, "confidence": 0, "signal": "NEUTRAL", "reason": "Insufficient data"}

            # Extract values and ensure no NaNs for talib
            close = np.asarray(df["Close"].dropna().values, dtype=np.float64)
            high = np.asarray(df["High"].dropna().values, dtype=np.float64)
            low = np.asarray(df["Low"].dropna().values, dtype=np.float64)
            volume = np.asarray(df["Volume"].dropna().values, dtype=np.float64)
            
            # Ensure minimum length after cleaning
            if len(close) < 50:
                return {"symbol": symbol, "confidence": 0, "signal": "NEUTRAL", "reason": "Insufficient clean data"}

            analysis = {
                "symbol": symbol,
                "timestamp": pd.Timestamp.now(),
                "indicators": {},
                "signals": []
            }

            # Moving Averages
            sma_20 = talib.SMA(close, timeperiod=20)
            sma_50 = talib.SMA(close, timeperiod=50)
            sma_200 = talib.SMA(close, timeperiod=200)

            analysis["indicators"]["SMA_20"] = sma_20[-1]
            analysis["indicators"]["SMA_50"] = sma_50[-1]
            analysis["indicators"]["SMA_200"] = sma_200[-1]
            analysis["indicators"]["Price"] = close[-1]

            # Trend Analysis
            if sma_20[-1] > sma_50[-1] > sma_200[-1]:
                analysis["signals"].append({"indicator": "Golden Cross", "strength": 1.0})
            elif sma_20[-1] < sma_50[-1] < sma_200[-1]:
                analysis["signals"].append({"indicator": "Death Cross", "strength": -1.0})

            # RSI (Relative Strength Index)
            rsi = talib.RSI(close, timeperiod=14)
            analysis["indicators"]["RSI"] = rsi[-1]

            if rsi[-1] < 30:
                analysis["signals"].append({"indicator": "RSI Oversold", "strength": 0.8})
            elif rsi[-1] > 70:
                analysis["signals"].append({"indicator": "RSI Overbought", "strength": -0.8})

            # MACD
            macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
            analysis["indicators"]["MACD"] = macd[-1]
            analysis["indicators"]["MACD_Signal"] = macd_signal[-1]
            analysis["indicators"]["MACD_Histogram"] = macd_hist[-1]

            if macd[-1] > macd_signal[-1] and macd[-2] <= macd_signal[-2]:
                analysis["signals"].append({"indicator": "MACD Bullish Crossover", "strength": 0.9})
            elif macd[-1] < macd_signal[-1] and macd[-2] >= macd_signal[-2]:
                analysis["signals"].append({"indicator": "MACD Bearish Crossover", "strength": -0.9})

            # Bollinger Bands
            upper_bb, middle_bb, lower_bb = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
            analysis["indicators"]["BB_Upper"] = upper_bb[-1]
            analysis["indicators"]["BB_Lower"] = lower_bb[-1]

            if close[-1] < lower_bb[-1]:
                analysis["signals"].append({"indicator": "Bollinger Band Breakout (Lower)", "strength": 0.7})
            elif close[-1] > upper_bb[-1]:
                analysis["signals"].append({"indicator": "Bollinger Band Breakout (Upper)", "strength": -0.7})

            # ATR (Average True Range) - Volatility
            atr = talib.ATR(high, low, close, timeperiod=14)
            analysis["indicators"]["ATR"] = atr[-1]

            # Volume Analysis
            avg_volume = talib.SMA(volume, timeperiod=20)
            volume_signal = volume[-1] / avg_volume[-1] if avg_volume[-1] > 0 else 1

            if volume_signal > 1.5:
                analysis["signals"].append({"indicator": "High Volume", "strength": 0.5})

            # Calculate overall signal
            total_signal = sum(s["strength"] for s in analysis["signals"]) / len(analysis["signals"]) if analysis["signals"] else 0
            analysis["confidence"] = min(abs(total_signal), 1.0)
            analysis["signal"] = "BUY" if total_signal > 0.3 else "SELL" if total_signal < -0.3 else "NEUTRAL"

            return analysis

        except Exception as e:
            logger.error(f"Error in technical analysis for {symbol}: {e}")
            return {"symbol": symbol, "confidence": 0, "signal": "NEUTRAL", "reason": f"Error: {e}"}
