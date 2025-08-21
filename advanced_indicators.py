"""
Advanced Technical Indicators for Stock Analysis
Includes: Fractal Dimension, Market Regime Detection, Sentiment Indicators
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AdvancedTechnicalIndicators:
    """Advanced technical indicators for enhanced stock analysis"""
    
    def __init__(self, data):
        """
        Initialize with price data
        
        Args:
            data (pd.DataFrame): OHLCV data with datetime index
        """
        self.data = data
        self.results = {}
        
    def calculate_fractal_dimension(self, window=20, method='box_counting'):
        """
        Calculate fractal dimension using different methods
        
        Args:
            window (int): Rolling window size
            method (str): 'box_counting', 'higuchi', or 'katz'
            
        Returns:
            pd.Series: Fractal dimension values
        """
        if method == 'box_counting':
            return self._box_counting_fractal(window)
        elif method == 'higuchi':
            return self._higuchi_fractal(window)
        elif method == 'katz':
            return self._katz_fractal(window)
        else:
            raise ValueError("Method must be 'box_counting', 'higuchi', or 'katz'")
    
    def _box_counting_fractal(self, window):
        """Box counting method for fractal dimension"""
        def box_count(series):
            if len(series) < 2:
                return np.nan
            
            # Normalize the series
            series_norm = (series - series.min()) / (series.max() - series.min())
            
            # Create grid boxes
            box_sizes = [2, 4, 8, 16]
            box_counts = []
            
            for size in box_sizes:
                if size > len(series_norm):
                    continue
                    
                # Count boxes that contain data points
                count = 0
                for i in range(0, len(series_norm), size):
                    end_idx = min(i + size, len(series_norm))
                    if end_idx > i:
                        segment = series_norm[i:end_idx]
                        if len(segment) > 0 and (segment.max() - segment.min()) > 0:
                            count += 1
                
                if count > 0:
                    box_counts.append(count)
            
            if len(box_counts) < 2:
                return np.nan
            
            # Calculate fractal dimension using log-log relationship
            try:
                log_sizes = np.log([1/s for s in box_sizes[:len(box_counts)]])
                log_counts = np.log(box_counts)
                
                # Linear regression
                slope, intercept, r_value, p_value, std_err = stats.linregress(log_sizes, log_counts)
                return slope if r_value > 0.8 else np.nan
            except:
                return np.nan
        
        # Apply rolling window
        fractal_dim = self.data['Close'].rolling(window=window).apply(box_count)
        self.results['fractal_dimension'] = fractal_dim
        return fractal_dim
    
    def _higuchi_fractal(self, window):
        """Higuchi method for fractal dimension"""
        def higuchi_method(series):
            if len(series) < 2:
                return np.nan
            
            try:
                # Normalize series
                series_norm = (series - series.min()) / (series.max() - series.min())
                
                # Higuchi parameters
                k_max = min(20, len(series_norm) // 4)
                k_values = range(1, k_max + 1)
                L_values = []
                
                for k in k_values:
                    L_k = 0
                    for m in range(k):
                        # Calculate L(m,k)
                        indices = range(m, len(series_norm), k)
                        if len(indices) < 2:
                            continue
                        
                        # Sum of absolute differences
                        diff_sum = sum(abs(series_norm[indices[i]] - series_norm[indices[i-1]]) 
                                     for i in range(1, len(indices)))
                        
                        # Normalize by k
                        L_k += diff_sum * (len(series_norm) - 1) / (k * k * len(indices))
                    
                    if L_k > 0:
                        L_values.append(L_k)
                
                if len(L_values) < 2:
                    return np.nan
                
                # Calculate fractal dimension
                log_k = np.log(k_values[:len(L_values)])
                log_L = np.log(L_values)
                
                slope, _, r_value, _, _ = stats.linregress(log_k, log_L)
                return -slope if r_value > 0.8 else np.nan
                
            except:
                return np.nan
        
        fractal_dim = self.data['Close'].rolling(window=window).apply(higuchi_method)
        self.results['fractal_dimension_higuchi'] = fractal_dim
        return fractal_dim
    
    def _katz_fractal(self, window):
        """Katz method for fractal dimension"""
        def katz_method(series):
            if len(series) < 2:
                return np.nan
            
            try:
                # Normalize series
                series_norm = (series - series.min()) / (series.max() - series.min())
                
                # Calculate total length
                total_length = sum(abs(series_norm[i] - series_norm[i-1]) 
                                for i in range(1, len(series_norm)))
                
                # Calculate straight-line distance
                straight_distance = abs(series_norm[-1] - series_norm[0])
                
                if straight_distance == 0:
                    return np.nan
                
                # Katz fractal dimension
                fractal_dim = np.log(len(series_norm)) / np.log(len(series_norm) * straight_distance / total_length)
                return fractal_dim
                
            except:
                return np.nan
        
        fractal_dim = self.data['Close'].rolling(window=window).apply(katz_method)
        self.results['fractal_dimension_katz'] = fractal_dim
        return fractal_dim
    
    def detect_market_regime(self, n_regimes=3, features=['returns', 'volatility', 'volume_ratio']):
        """
        Detect market regimes using clustering
        
        Args:
            n_regimes (int): Number of market regimes to detect
            features (list): Features to use for regime detection
            
        Returns:
            pd.Series: Market regime labels
        """
        # Calculate features
        returns = self.data['Close'].pct_change()
        volatility = returns.rolling(window=20).std()
        volume_ratio = self.data['Volume'] / self.data['Volume'].rolling(window=20).mean()
        
        # Create feature matrix
        feature_data = pd.DataFrame({
            'returns': returns,
            'volatility': volatility,
            'volume_ratio': volume_ratio
        }).dropna()
        
        # Select only requested features
        feature_data = feature_data[features]
        
        if len(feature_data) < n_regimes * 10:  # Need sufficient data
            return pd.Series(index=self.data.index, dtype='object')
        
        # Standardize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(feature_data)
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=n_regimes, random_state=42, n_init=10)
        regime_labels = kmeans.fit_predict(features_scaled)
        
        # Map regimes to descriptive names
        regime_names = self._classify_regimes(feature_data, regime_labels)
        
        # Create result series
        result = pd.Series(index=feature_data.index, data=regime_names)
        result = result.reindex(self.data.index)
        
        self.results['market_regime'] = result
        return result
    
    def _classify_regimes(self, features, labels):
        """Classify market regimes based on characteristics"""
        regime_names = []
        
        for label in np.unique(labels):
            mask = labels == label
            regime_data = features[mask]
            
            # Calculate regime characteristics
            avg_return = regime_data['returns'].mean()
            avg_vol = regime_data['volatility'].mean()
            avg_volume = regime_data['volume_ratio'].mean()
            
            # Classify based on characteristics
            if avg_vol > features['volatility'].quantile(0.7):
                if avg_return > 0:
                    regime_name = "High Volatility Bull"
                else:
                    regime_name = "High Volatility Bear"
            elif avg_vol < features['volatility'].quantile(0.3):
                if avg_return > 0:
                    regime_name = "Low Volatility Bull"
                else:
                    regime_name = "Low Volatility Bear"
            else:
                if avg_return > 0:
                    regime_name = "Moderate Bull"
                else:
                    regime_name = "Moderate Bear"
            
            regime_names.extend([regime_name] * mask.sum())
        
        return regime_names
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI using pure Python/NumPy"""
        if len(prices) < period + 1:
            return np.full(len(prices), np.nan)
        
        # Calculate price changes
        deltas = np.diff(prices)
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate average gains and losses
        avg_gains = np.zeros_like(prices)
        avg_losses = np.zeros_like(prices)
        
        # First average
        avg_gains[period] = np.mean(gains[:period])
        avg_losses[period] = np.mean(losses[:period])
        
        # Subsequent averages using smoothing
        for i in range(period + 1, len(prices)):
            avg_gains[i] = (avg_gains[i-1] * (period - 1) + gains[i-1]) / period
            avg_losses[i] = (avg_losses[i-1] * (period - 1) + losses[i-1]) / period
        
        # Calculate RS and RSI
        rs = avg_gains / np.where(avg_losses == 0, 1e-10, avg_losses)  # Avoid division by zero
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD using pure Python/NumPy"""
        if len(prices) < slow:
            return np.full(len(prices), np.nan), np.full(len(prices), np.nan), np.full(len(prices), np.nan)
        
        # Calculate EMAs
        def ema(data, period):
            alpha = 2 / (period + 1)
            ema_values = np.zeros_like(data)
            ema_values[0] = data[0]
            
            for i in range(1, len(data)):
                ema_values[i] = alpha * data[i] + (1 - alpha) * ema_values[i-1]
            
            return ema_values
        
        ema_fast = ema(prices, fast)
        ema_slow = ema(prices, slow)
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line
        signal_line = ema(macd_line, signal)
        
        # Histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate_sentiment_indicators(self, window=20):
        """
        Calculate sentiment indicators
        
        Args:
            window (int): Rolling window size
            
        Returns:
            dict: Dictionary of sentiment indicators
        """
        # Price momentum sentiment
        momentum = self.data['Close'].pct_change(periods=window)
        momentum_sentiment = np.where(momentum > 0, 1, np.where(momentum < 0, -1, 0))
        
        # Volume sentiment
        volume_ma = self.data['Volume'].rolling(window=window).mean()
        volume_sentiment = np.where(self.data['Volume'] > volume_ma * 1.5, 1, 
                                  np.where(self.data['Volume'] < volume_ma * 0.5, -1, 0))
        
        # Volatility sentiment (inverse relationship)
        volatility = self.data['Close'].pct_change().rolling(window=window).std()
        vol_ma = volatility.rolling(window=window).mean()
        volatility_sentiment = np.where(volatility < vol_ma * 0.8, 1,
                                      np.where(volatility > vol_ma * 1.2, -1, 0))
        
        # RSI sentiment (using our own implementation)
        rsi = self._calculate_rsi(self.data['Close'].values, timeperiod=14)
        rsi_sentiment = np.where(rsi > 70, -1, np.where(rsi < 30, 1, 0))
        
        # MACD sentiment (using our own implementation)
        macd, macd_signal, _ = self._calculate_macd(self.data['Close'].values)
        macd_sentiment = np.where(macd > macd_signal, 1, -1)
        
        # Composite sentiment score
        sentiment_score = (momentum_sentiment + volume_sentiment + volatility_sentiment + 
                          rsi_sentiment + macd_sentiment) / 5
        
        # Normalize to [-1, 1] range
        sentiment_score = np.clip(sentiment_score, -1, 1)
        
        # Create results
        results = {
            'momentum_sentiment': pd.Series(momentum_sentiment, index=self.data.index),
            'volume_sentiment': pd.Series(volume_sentiment, index=self.data.index),
            'volatility_sentiment': pd.Series(volatility_sentiment, index=self.data.index),
            'rsi_sentiment': pd.Series(rsi_sentiment, index=self.data.index),
            'macd_sentiment': pd.Series(macd_sentiment, index=self.data.index),
            'composite_sentiment': pd.Series(sentiment_score, index=self.data.index)
        }
        
        self.results.update(results)
        return results
    
    def get_all_indicators(self):
        """Calculate all advanced indicators"""
        print("🔄 Calculating Fractal Dimension...")
        self.calculate_fractal_dimension(method='box_counting')
        
        print("🔄 Detecting Market Regimes...")
        self.detect_market_regime()
        
        print("🔄 Calculating Sentiment Indicators...")
        self.calculate_sentiment_indicators()
        
        return self.results
    
    def plot_indicators(self):
        """Plot all calculated indicators"""
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(4, 2, figsize=(15, 12))
        fig.suptitle('Advanced Technical Indicators', fontsize=16)
        
        # Fractal Dimension
        if 'fractal_dimension' in self.results:
            axes[0, 0].plot(self.results['fractal_dimension'])
            axes[0, 0].set_title('Fractal Dimension (Box Counting)')
            axes[0, 0].set_ylabel('Dimension')
        
        # Market Regime
        if 'market_regime' in self.results:
            regime_data = self.results['market_regime'].dropna()
            if len(regime_data) > 0:
                regime_counts = regime_data.value_counts()
                axes[0, 1].pie(regime_counts.values, labels=regime_counts.index, autopct='%1.1f%%')
                axes[0, 1].set_title('Market Regime Distribution')
        
        # Sentiment Indicators
        if 'composite_sentiment' in self.results:
            axes[1, 0].plot(self.results['composite_sentiment'])
            axes[1, 0].set_title('Composite Sentiment Score')
            axes[1, 0].set_ylabel('Sentiment (-1 to 1)')
            axes[1, 0].axhline(y=0, color='r', linestyle='--', alpha=0.5)
        
        # Volume Sentiment
        if 'volume_sentiment' in self.results:
            axes[1, 1].plot(self.results['volume_sentiment'])
            axes[1, 1].set_title('Volume Sentiment')
            axes[1, 1].set_ylabel('Sentiment')
        
        # RSI Sentiment
        if 'rsi_sentiment' in self.results:
            axes[2, 0].plot(self.results['rsi_sentiment'])
            axes[2, 0].set_title('RSI Sentiment')
            axes[2, 0].set_ylabel('Sentiment')
        
        # MACD Sentiment
        if 'macd_sentiment' in self.results:
            axes[2, 1].plot(self.results['macd_sentiment'])
            axes[2, 1].set_title('MACD Sentiment')
            axes[2, 1].set_ylabel('Sentiment')
        
        # Price with Regime Overlay
        if 'market_regime' in self.results:
            axes[3, 0].plot(self.data['Close'])
            axes[3, 0].set_title('Price with Market Regime')
            axes[3, 0].set_ylabel('Price')
            
            # Color code by regime
            regime_data = self.results['market_regime'].dropna()
            if len(regime_data) > 0:
                for regime in regime_data.unique():
                    mask = regime_data == regime
                    regime_dates = regime_data[mask].index
                    regime_prices = self.data.loc[regime_dates, 'Close']
                    axes[3, 0].scatter(regime_dates, regime_prices, alpha=0.6, label=regime)
                axes[3, 0].legend()
        
        # Volatility
        volatility = self.data['Close'].pct_change().rolling(window=20).std()
        axes[3, 1].plot(volatility)
        axes[3, 1].set_title('Price Volatility')
        axes[3, 1].set_ylabel('Volatility')
        
        plt.tight_layout()
        return fig
