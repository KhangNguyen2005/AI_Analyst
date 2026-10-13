"""
Beta Calculator Module

This module provides utilities for calculating stock beta values,
which measure a stock's volatility relative to the market.

Beta interpretation:
- Beta = 1: Stock moves with market
- Beta > 1: Stock is more volatile than market
- Beta < 1: Stock is less volatile than market
- Beta < 0: Stock moves opposite to market
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


def calculate_beta(stock_prices, market_prices):
    """
    Calculate beta of a stock relative to market.
    
    Beta measures systematic risk - how much a stock's price changes
    relative to market movements.
    
    Parameters:
    -----------
    stock_prices : list, array, or pd.Series
        Historical stock prices (in chronological order)
    market_prices : list, array, or pd.Series
        Historical market index prices (in chronological order)
    
    Returns:
    --------
    float
        Beta value
        
    Example:
    --------
    >>> stock_prices = [100, 102, 101, 105, 108]
    >>> market_prices = [1000, 1005, 1003, 1010, 1020]
    >>> beta = calculate_beta(stock_prices, market_prices)
    >>> print(f"Beta: {beta:.2f}")
    """
    # Convert to numpy arrays for calculation
    stock_prices = np.array(stock_prices, dtype=float)
    market_prices = np.array(market_prices, dtype=float)
    
    # Validate input
    if len(stock_prices) != len(market_prices):
        raise ValueError("Stock and market prices must have same length")
    
    if len(stock_prices) < 3:
        raise ValueError(f"Need at least 3 data points to calculate beta (you have {len(stock_prices)})")
    
    
    # Calculate returns (percentage change)
    stock_returns = np.diff(stock_prices) / stock_prices[:-1]
    market_returns = np.diff(market_prices) / market_prices[:-1]
    
    # Calculate covariance and variance
    covariance = np.cov(stock_returns, market_returns)[0][1]
    market_variance = np.var(market_returns, ddof=1)  # Use sample variance
    
    # Calculate beta
    if market_variance == 0:
        raise ValueError("Market variance is zero - cannot calculate beta")
    
    beta = covariance / market_variance
    
    return beta


def calculate_beta_from_dataframe(df, stock_col, market_col):
    """
    Calculate beta from a pandas DataFrame.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing price data
    stock_col : str
        Column name for stock prices
    market_col : str
        Column name for market prices
    
    Returns:
    --------
    float
        Beta value
        
    Example:
    --------
    >>> df = pd.DataFrame({
    ...     'stock': [100, 102, 101, 105],
    ...     'market': [1000, 1005, 1003, 1010]
    ... })
    >>> beta = calculate_beta_from_dataframe(df, 'stock', 'market')
    """
    return calculate_beta(df[stock_col].values, df[market_col].values)


def calculate_beta_with_stats(stock_prices, market_prices):
    """
    Calculate beta and return additional statistics.
    
    Parameters:
    -----------
    stock_prices : list, array, or pd.Series
        Historical stock prices (in chronological order)
    market_prices : list, array, or pd.Series
        Historical market index prices (in chronological order)
    
    Returns:
    --------
    dict
        Dictionary containing:
        - 'beta': Beta value
        - 'alpha': Alpha (excess return)
        - 'correlation': Correlation between stock and market
        - 'stock_volatility': Stock's standard deviation of returns
        - 'market_volatility': Market's standard deviation of returns
        - 'r_squared': R-squared (coefficient of determination)
        
    Example:
    --------
    >>> stock_prices = [100, 102, 101, 105, 108]
    >>> market_prices = [1000, 1005, 1003, 1010, 1020]
    >>> stats = calculate_beta_with_stats(stock_prices, market_prices)
    >>> print(f"Beta: {stats['beta']:.2f}")
    >>> print(f"Correlation: {stats['correlation']:.2f}")
    """
    # Convert to numpy arrays
    stock_prices = np.array(stock_prices, dtype=float)
    market_prices = np.array(market_prices, dtype=float)
    
    # Calculate returns
    stock_returns = np.diff(stock_prices) / stock_prices[:-1]
    market_returns = np.diff(market_prices) / market_prices[:-1]
    
    # Calculate statistics
    covariance_matrix = np.cov(stock_returns, market_returns)
    covariance = covariance_matrix[0][1]
    market_variance = np.var(market_returns, ddof=1)
    
    beta = covariance / market_variance
    
    # Calculate correlation
    correlation = np.corrcoef(stock_returns, market_returns)[0][1]
    
    # Calculate volatilities
    stock_volatility = np.std(stock_returns, ddof=1)
    market_volatility = np.std(market_returns, ddof=1)
    
    # Calculate R-squared (correlation squared)
    r_squared = correlation ** 2
    
    # Calculate alpha (simplified - assumes risk-free rate of 0)
    mean_stock_return = np.mean(stock_returns)
    mean_market_return = np.mean(market_returns)
    alpha = mean_stock_return - (beta * mean_market_return)
    
    return {
        'beta': beta,
        'alpha': alpha,
        'correlation': correlation,
        'stock_volatility': stock_volatility,
        'market_volatility': market_volatility,
        'r_squared': r_squared
    }


def interactive_mode():
    """
    Interactive mode for calculating beta with user input.
    """
    print("\n" + "="*60)
    print("Beta Calculator - Interactive Mode")
    print("="*60 + "\n")
    
    # Check if yfinance is available
    if YFINANCE_AVAILABLE:
        print("Options:")
        print("1. Fetch stock data automatically (requires internet)")
        print("2. Enter prices manually")
        choice = input("\nSelect option (1 or 2): ").strip()
        
        if choice == "1":
            return interactive_fetch_data()
    
    return interactive_manual_input()


def interactive_fetch_data():
    """
    Interactive mode to fetch stock data automatically.
    """
    print("\n" + "-"*60)
    print("Automatic Stock Data Fetcher")
    print("-"*60 + "\n")
    
    try:
        # Get date range - two options
        print("Date range options:")
        print("1. Days back from today (e.g., 30 days)")
        print("2. Specific dates (e.g., 2026-05-15 to 2026-05-17)")
        date_choice = input("\nSelect option (1 or 2): ").strip()
        
        if date_choice == "2":
            # Specific dates
            start_date = input("Start date (YYYY-MM-DD): ").strip()
            end_date = input("End date (YYYY-MM-DD): ").strip()
            
            # Validate date format
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
        else:
            # Days back (default option 1)
            print("\nDate range for analysis:")
            print("(Fetches calendar days - trading days may be fewer due to weekends)")
            days_back = input("How many days back? (default: 30): ").strip()
            days_back = int(days_back) if days_back else 30
            
            # Ensure at least enough calendar days to get 3 trading days
            # (3 trading days needs ~5 calendar days due to weekends)
            if days_back < 5:
                days_back = 7  # Guarantees at least 3-5 trading days
            
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        print(f"\nDate range: {start_date} to {end_date}")
        
        # Get stock tickers
        print("\nEnter stock tickers (comma-separated)")
        print("Example: TSLA, AAPL, GOOGL, INTC")
        tickers_input = input("Stock tickers: ").strip().upper()
        stock_tickers = [t.strip() for t in tickers_input.split(',')]
        
        if not stock_tickers or stock_tickers == ['']:
            print("❌ No tickers entered!")
            return
        
        # Get market index
        market = input("\nMarket index ticker (default: SPY): ").strip().upper() or "SPY"
        
        print("\n" + "-"*60)
        
        # Fetch and calculate
        results = calculate_beta_multiple_stocks(stock_tickers, market, start_date, end_date)
        
        # Display results
        print("\n" + "="*60)
        print("Beta Analysis Results")
        print("="*60 + "\n")
        print(f"Market Index: {market}")
        print(f"Period: {start_date} to {end_date}\n")
        
        for ticker, stats in results.items():
            if stats is None:
                print(f"\n❌ {ticker}: Failed to calculate")
            else:
                print(f"\n📊 {ticker}:")
                print(f"  Beta: {stats['beta']:.4f}", end="")
                
                # Interpretation
                if stats['beta'] > 1.2:
                    print(" (Very High Volatility)")
                elif stats['beta'] > 1:
                    print(" (High Volatility)")
                elif stats['beta'] > 0.8:
                    print(" (Moderate Volatility)")
                else:
                    print(" (Low Volatility)")
                
                print(f"  Alpha: {stats['alpha']:.4f}")
                print(f"  Correlation: {stats['correlation']:.4f}")
                print(f"  Stock Volatility: {stats['stock_volatility']:.4f}")
                print(f"  Market Volatility: {stats['market_volatility']:.4f}")
                print(f"  R-squared: {stats['r_squared']:.4f}")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTrying manual input instead...")
        interactive_manual_input()


def interactive_manual_input():
    """
    Interactive mode for manual price entry.
    """
    print("\n" + "-"*60)
    print("Manual Price Entry")
    print("-"*60 + "\n")
    
    while True:
        try:
            # Get stock prices
            print("Enter stock prices (comma-separated values)")
            print("Example: 100, 102, 101, 105, 108")
            stock_input = input("Stock prices: ").strip()
            stock_prices = [float(x.strip()) for x in stock_input.split(',')]
            
            # Get market prices
            print("\nEnter market index prices (comma-separated values)")
            print("Example: 1000, 1005, 1003, 1010, 1020")
            market_input = input("Market prices: ").strip()
            market_prices = [float(x.strip()) for x in market_input.split(',')]
            
            # Validate
            if len(stock_prices) != len(market_prices):
                print("\n❌ Error: Stock and market prices must have the same number of values!")
                continue
            
            if len(stock_prices) < 2:
                print("\n❌ Error: Need at least 2 data points!")
                continue
            
            # Calculate
            print("\n" + "-"*60)
            beta = calculate_beta(stock_prices, market_prices)
            stats = calculate_beta_with_stats(stock_prices, market_prices)
            
            # Display results
            print("\n✓ Results:")
            print(f"  Beta: {beta:.4f}")
            print(f"\nDetailed Statistics:")
            print(f"  Alpha: {stats['alpha']:.4f}")
            print(f"  Correlation: {stats['correlation']:.4f}")
            print(f"  Stock Volatility: {stats['stock_volatility']:.4f}")
            print(f"  Market Volatility: {stats['market_volatility']:.4f}")
            print(f"  R-squared: {stats['r_squared']:.4f}")
            print("-"*60)
            
            # Ask if user wants to continue
            another = input("\nCalculate another? (yes/no): ").strip().lower()
            if another not in ['yes', 'y']:
                print("\nGoodbye! 👋\n")
                break
            print()
            
        except ValueError as e:
            print(f"\n❌ Error: Invalid input - {e}")
            print("Please enter numbers separated by commas.\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def fetch_stock_data(ticker, start_date, end_date):
    """
    Fetch historical stock prices from Yahoo Finance.
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol (e.g., 'TSLA', 'AAPL', 'SPY')
    start_date : str
        Start date in format 'YYYY-MM-DD'
    end_date : str
        End date in format 'YYYY-MM-DD'
    
    Returns:
    --------
    list
        List of closing prices
        
    Raises:
    -------
    Exception
        If yfinance is not installed or data cannot be fetched
    """
    if not YFINANCE_AVAILABLE:
        raise ImportError(
            "yfinance is required for automatic data fetching.\n"
            "Install it with: pip install yfinance"
        )
    
    try:
        print(f"  Fetching {ticker}...", end=" ", flush=True)
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if data.empty:
            raise ValueError(f"No data found for ticker {ticker}")
        
        # Handle both Series (single stock) and DataFrame (multiple columns)
        if isinstance(data, pd.Series):
            prices = data.values
        else:
            prices = data['Close'].values
        
        # Convert to list and ensure no NaN values
        prices = [float(p) for p in prices if not np.isnan(p)]
        
        if len(prices) < 2:
            raise ValueError(f"Insufficient data for {ticker} - only {len(prices)} prices")
        
        print(f"✓ ({len(prices)} days)")
        return prices
    except Exception as e:
        raise Exception(f"Failed to fetch data for {ticker}: {e}")


def calculate_beta_multiple_stocks(stock_tickers, market_ticker, start_date, end_date):
    """
    Calculate beta for multiple stocks against a market index.
    
    Parameters:
    -----------
    stock_tickers : list
        List of stock ticker symbols
    market_ticker : str
        Market index ticker (e.g., 'SPY' for S&P 500)
    start_date : str
        Start date in format 'YYYY-MM-DD'
    end_date : str
        End date in format 'YYYY-MM-DD'
    
    Returns:
    --------
    dict
        Dictionary with ticker as key and beta statistics as value
    """
    results = {}
    
    # Fetch market data
    print(f"\nFetching market index data ({market_ticker})...")
    market_prices = fetch_stock_data(market_ticker, start_date, end_date)
    
    # Fetch and calculate beta for each stock
    print(f"\nCalculating beta for {len(stock_tickers)} stocks...")
    for ticker in stock_tickers:
        try:
            stock_prices = fetch_stock_data(ticker, start_date, end_date)
            
            # Ensure same length using copies
            min_len = min(len(stock_prices), len(market_prices))
            stock_prices_adj = stock_prices[-min_len:] if min_len > 0 else []
            market_prices_adj = market_prices[-min_len:] if min_len > 0 else []
            
            if len(stock_prices_adj) < 3:
                raise ValueError(f"Insufficient data points: {len(stock_prices_adj)}")
            
            # Calculate beta and stats
            beta = calculate_beta(stock_prices_adj, market_prices_adj)
            stats = calculate_beta_with_stats(stock_prices_adj, market_prices_adj)
            
            results[ticker] = stats
            
        except Exception as e:
            print(f"  ❌ Error with {ticker}: {e}")
            results[ticker] = None
    
    return results


if __name__ == "__main__":
    import sys
    
    # Check for command-line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--example":
        # Example usage
        print("Running with example data...\n")
        stock_prices = [100, 102, 101, 105, 108, 110, 107, 112]
        market_prices = [1000, 1005, 1003, 1010, 1020, 1025, 1015, 1030]
        
        beta = calculate_beta(stock_prices, market_prices)
        print(f"Beta: {beta:.4f}")
        
        stats = calculate_beta_with_stats(stock_prices, market_prices)
        print("\nDetailed Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value:.4f}")
    else:
        # Interactive mode (default)
        interactive_mode()
