import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    """Fetch market data from multiple sources"""

    @staticmethod
    def fetch_stock_data(symbol, period="1y", interval="1d"):
        """Fetch historical stock data"""
        try:
            data = yf.download(symbol, period=period, interval=interval, progress=False)
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    @staticmethod
    def fetch_intraday_data(symbol, interval="1h"):
        """Fetch intraday data for short-term analysis"""
        try:
            data = yf.download(symbol, period="5d", interval=interval, progress=False)
            return data
        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {e}")
            return None

    @staticmethod
    def fetch_stock_info(symbol):
        """Fetch company fundamentals"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                "symbol": symbol,
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "current_price": info.get("currentPrice"),
                "profit_margins": info.get("profitMargins"),
                "roe": info.get("returnOnEquity"),
            }
        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {e}")
            return None

    @staticmethod
    def fetch_multiple_stocks(symbols, period="1y"):
        """Fetch data for multiple stocks"""
        data_dict = {}
        for symbol in symbols:
            data_dict[symbol] = DataFetcher.fetch_stock_data(symbol, period=period)
        return data_dict

    @staticmethod
    def get_current_price(symbol):
        """Get current price for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            return ticker.info.get("currentPrice")
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
