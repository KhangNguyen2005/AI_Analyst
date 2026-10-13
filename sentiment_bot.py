import requests
import logging
from datetime import datetime, timedelta
from textblob import TextBlob
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalysisBot:
    """Analyze market sentiment for stocks"""

    def __init__(self, news_api_key=None):
        self.name = "Sentiment Analysis Bot"
        self.news_api_key = news_api_key
        self.sentiment_cache = {}

    def analyze_sentiment(self, text):
        """Analyze sentiment of text using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            return polarity, subjectivity
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0, 0

    def fetch_stock_news(self, symbol, days=7):
        """Fetch recent news for a stock"""
        try:
            if self.news_api_key:
                url = f"https://newsapi.org/v2/everything"
                params = {
                    "q": symbol,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "pageSize": 20,
                    "apiKey": self.news_api_key
                }
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    return response.json().get("articles", [])
            return []
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []

    def analyze(self, symbol, lookback_days=7):
        """Analyze sentiment for a stock"""
        try:
            analysis = {
                "symbol": symbol,
                "timestamp": pd.Timestamp.now(),
                "overall_sentiment": 0,
                "confidence": 0,
                "signal": "NEUTRAL",
                "articles_analyzed": 0,
                "sentiment_scores": []
            }

            # Fetch news
            news_articles = self.fetch_stock_news(symbol, lookback_days)

            if not news_articles:
                analysis["reason"] = "No recent news data available"
                return analysis

            sentiments = []
            for article in news_articles:
                title = article.get("title", "")
                description = article.get("description", "") or ""

                # Analyze title and description
                text_to_analyze = f"{title} {description}"
                polarity, subjectivity = self.analyze_sentiment(text_to_analyze)

                # Weight by subjectivity (less subjective = more reliable)
                weighted_polarity = polarity * (1 - subjectivity * 0.3)
                sentiments.append({
                    "polarity": polarity,
                    "weighted_polarity": weighted_polarity,
                    "source": article.get("source", {}).get("name"),
                    "published_at": article.get("publishedAt")
                })

            if sentiments:
                # Calculate overall sentiment
                avg_sentiment = sum(s["weighted_polarity"] for s in sentiments) / len(sentiments)
                analysis["overall_sentiment"] = avg_sentiment
                analysis["sentiment_scores"] = sentiments
                analysis["articles_analyzed"] = len(sentiments)
                analysis["confidence"] = min(abs(avg_sentiment) * 0.8, 1.0)  # Cap at 80% confidence

                if avg_sentiment > 0.3:
                    analysis["signal"] = "BUY"
                elif avg_sentiment < -0.3:
                    analysis["signal"] = "SELL"
                else:
                    analysis["signal"] = "NEUTRAL"

            return analysis

        except Exception as e:
            logger.error(f"Error in sentiment analysis for {symbol}: {e}")
            return {
                "symbol": symbol,
                "overall_sentiment": 0,
                "confidence": 0,
                "signal": "NEUTRAL",
                "reason": f"Error: {e}"
            }

    def analyze_social_sentiment(self, symbol):
        """Simple social sentiment based on common patterns"""
        # This is a placeholder for social sentiment analysis
        # In production, you'd integrate with APIs like Twitter API, Reddit API, etc.
        analysis = {
            "symbol": symbol,
            "platform": "Social",
            "positive_mentions": 0,
            "negative_mentions": 0,
            "neutral_mentions": 0,
            "sentiment_score": 0
        }
        return analysis
