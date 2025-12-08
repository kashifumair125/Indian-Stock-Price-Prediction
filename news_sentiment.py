"""
News Sentiment Analysis Module
Fetches and analyzes news sentiment for stocks
"""
import requests
from datetime import datetime, timedelta
import pandas as pd
from textblob import TextBlob  # Simple sentiment analysis
import yfinance as yf

class NewsSentimentAnalyzer:
    def __init__(self, symbol):
        """
        Initialize news sentiment analyzer

        Args:
            symbol: Stock symbol
        """
        self.symbol = symbol
        self.news = []
        self.sentiment_scores = []

    def fetch_news(self, days=7):
        """
        Fetch news for the stock

        Args:
            days: Number of days to look back
        """
        try:
            # Using yfinance to get news
            ticker = yf.Ticker(self.symbol)
            news = ticker.news

            self.news = []
            for article in news[:20]:  # Limit to 20 articles
                try:
                    self.news.append({
                        'title': article.get('title', 'No title'),
                        'publisher': article.get('publisher', 'Unknown'),
                        'link': article.get('link', ''),
                        'published': datetime.fromtimestamp(article.get('providerPublishTime', 0)),
                        'type': article.get('type', 'news')
                    })
                except:
                    continue

            return self.news

        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def analyze_sentiment(self):
        """
        Analyze sentiment of news articles

        Returns:
            DataFrame with sentiment scores
        """
        if not self.news:
            self.fetch_news()

        self.sentiment_scores = []

        for article in self.news:
            try:
                # Simple sentiment analysis using TextBlob
                text = article['title']
                blob = TextBlob(text)
                sentiment = blob.sentiment.polarity  # -1 to 1

                # Classify sentiment
                if sentiment > 0.1:
                    sentiment_label = 'Positive'
                    emoji = '😊'
                elif sentiment < -0.1:
                    sentiment_label = 'Negative'
                    emoji = '😞'
                else:
                    sentiment_label = 'Neutral'
                    emoji = '😐'

                self.sentiment_scores.append({
                    'title': article['title'][:80] + '...' if len(article['title']) > 80 else article['title'],
                    'publisher': article['publisher'],
                    'published': article['published'],
                    'sentiment_score': sentiment,
                    'sentiment': sentiment_label,
                    'emoji': emoji,
                    'link': article['link']
                })

            except Exception as e:
                continue

        return pd.DataFrame(self.sentiment_scores)

    def get_overall_sentiment(self):
        """
        Get overall sentiment score

        Returns:
            dict with overall metrics
        """
        if not self.sentiment_scores:
            self.analyze_sentiment()

        if not self.sentiment_scores:
            return {
                'avg_sentiment': 0,
                'sentiment_label': 'Neutral',
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_articles': 0
            }

        df = pd.DataFrame(self.sentiment_scores)

        avg_sentiment = df['sentiment_score'].mean()

        if avg_sentiment > 0.1:
            overall_label = 'Positive'
            emoji = '😊'
            color = 'green'
        elif avg_sentiment < -0.1:
            overall_label = 'Negative'
            emoji = '😞'
            color = 'red'
        else:
            overall_label = 'Neutral'
            emoji = '😐'
            color = 'gray'

        positive = len(df[df['sentiment'] == 'Positive'])
        negative = len(df[df['sentiment'] == 'Negative'])
        neutral = len(df[df['sentiment'] == 'Neutral'])

        return {
            'avg_sentiment': avg_sentiment,
            'sentiment_label': overall_label,
            'emoji': emoji,
            'color': color,
            'positive_count': positive,
            'negative_count': negative,
            'neutral_count': neutral,
            'total_articles': len(df),
            'sentiment_distribution': {
                'Positive': positive,
                'Neutral': neutral,
                'Negative': negative
            }
        }

    def get_sentiment_trend(self):
        """
        Get sentiment trend over time

        Returns:
            DataFrame with daily sentiment averages
        """
        if not self.sentiment_scores:
            self.analyze_sentiment()

        if not self.sentiment_scores:
            return pd.DataFrame()

        df = pd.DataFrame(self.sentiment_scores)
        df['date'] = pd.to_datetime(df['published']).dt.date

        # Group by date and calculate average sentiment
        trend = df.groupby('date').agg({
            'sentiment_score': 'mean',
            'title': 'count'
        }).reset_index()

        trend.columns = ['date', 'avg_sentiment', 'article_count']

        return trend
