import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FundamentalAnalysisBot:
    """Analyze stocks using fundamental metrics"""

    def __init__(self):
        self.name = "Fundamental Analysis Bot"

    def analyze(self, stock_info):
        """Analyze fundamental metrics"""
        try:
            if not stock_info:
                return {
                    "confidence": 0,
                    "signal": "NEUTRAL",
                    "reason": "No stock info available"
                }

            symbol = stock_info.get("symbol")
            analysis = {
                "symbol": symbol,
                "timestamp": pd.Timestamp.now(),
                "metrics": {},
                "signals": []
            }

            # P/E Ratio Analysis
            pe_ratio = stock_info.get("pe_ratio")
            if pe_ratio and pe_ratio > 0:
                analysis["metrics"]["PE_Ratio"] = pe_ratio
                if pe_ratio < 15:
                    analysis["signals"].append({"metric": "P/E Ratio", "value": pe_ratio, "assessment": "Undervalued", "strength": 0.6})
                elif pe_ratio > 30:
                    analysis["signals"].append({"metric": "P/E Ratio", "value": pe_ratio, "assessment": "Overvalued", "strength": -0.6})

            # Market Cap Analysis
            market_cap = stock_info.get("market_cap")
            if market_cap:
                analysis["metrics"]["Market_Cap"] = market_cap
                if market_cap > 2e12:
                    analysis["signals"].append({"metric": "Market Cap", "assessment": "Large Cap (Stable)", "strength": 0.3})
                elif market_cap < 2e9:
                    analysis["signals"].append({"metric": "Market Cap", "assessment": "Small Cap (Volatile)", "strength": -0.3})

            # Dividend Yield
            dividend_yield = stock_info.get("dividend_yield")
            if dividend_yield and dividend_yield > 0:
                analysis["metrics"]["Dividend_Yield"] = dividend_yield
                if dividend_yield > 0.03:
                    analysis["signals"].append({"metric": "Dividend Yield", "value": dividend_yield, "assessment": "Good Income", "strength": 0.4})

            # Beta (Volatility)
            beta = stock_info.get("beta")
            if beta:
                analysis["metrics"]["Beta"] = beta
                if beta < 1:
                    analysis["signals"].append({"metric": "Beta", "value": beta, "assessment": "Less Volatile", "strength": 0.2})
                elif beta > 1.5:
                    analysis["signals"].append({"metric": "Beta", "value": beta, "assessment": "More Volatile", "strength": -0.2})

            # Return on Equity
            roe = stock_info.get("roe")
            if roe and roe > 0:
                analysis["metrics"]["ROE"] = roe
                if roe > 0.15:
                    analysis["signals"].append({"metric": "ROE", "value": roe, "assessment": "Strong", "strength": 0.5})
                elif roe < 0.05:
                    analysis["signals"].append({"metric": "ROE", "value": roe, "assessment": "Weak", "strength": -0.5})

            # Profit Margins
            profit_margins = stock_info.get("profit_margins")
            if profit_margins and profit_margins > 0:
                analysis["metrics"]["Profit_Margins"] = profit_margins
                if profit_margins > 0.15:
                    analysis["signals"].append({"metric": "Profit Margin", "value": profit_margins, "assessment": "Healthy", "strength": 0.4})
                elif profit_margins < 0.05:
                    analysis["signals"].append({"metric": "Profit Margin", "value": profit_margins, "assessment": "Low", "strength": -0.4})

            # 52-week range
            high_52w = stock_info.get("52_week_high")
            low_52w = stock_info.get("52_week_low")
            current_price = stock_info.get("current_price")

            if high_52w and low_52w and current_price:
                position_in_range = (current_price - low_52w) / (high_52w - low_52w)
                analysis["metrics"]["52W_Position"] = position_in_range

                if position_in_range > 0.8:
                    analysis["signals"].append({"metric": "52W Position", "assessment": "Near High", "strength": -0.3})
                elif position_in_range < 0.2:
                    analysis["signals"].append({"metric": "52W Position", "assessment": "Near Low", "strength": 0.5})

            # Calculate overall signal
            if analysis["signals"]:
                total_signal = sum(s.get("strength", 0) for s in analysis["signals"]) / len(analysis["signals"])
                analysis["confidence"] = min(abs(total_signal), 1.0)
                analysis["signal"] = "BUY" if total_signal > 0.2 else "SELL" if total_signal < -0.2 else "NEUTRAL"
            else:
                analysis["confidence"] = 0
                analysis["signal"] = "NEUTRAL"

            return analysis

        except Exception as e:
            logger.error(f"Error in fundamental analysis: {e}")
            return {
                "symbol": stock_info.get("symbol") if stock_info else "UNKNOWN",
                "confidence": 0,
                "signal": "NEUTRAL",
                "reason": f"Error: {e}"
            }
