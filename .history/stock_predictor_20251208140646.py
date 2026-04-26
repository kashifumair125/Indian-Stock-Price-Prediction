"""
Complete Indian Stock Price Prediction System
Author: AI Stock Analysis Team
Date: 2025
Features: Enhanced ML models, comprehensive analysis, UI compatibility
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import yfinance as yf
from datetime import datetime, timedelta
import logging

# Machine Learning Imports
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.ensemble import VotingRegressor, StackingRegressor, RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score

# Configuration
class Config:
    RANDOM_STATE = 42
    MA_PERIODS = [5, 10, 20, 50]
    RSI_PERIOD = 14
    BB_PERIOD = 20
    BB_STD = 2
    TEST_SIZE = 0.2
    MIN_DATA_POINTS = 100
    
    PROPHET_SEASONALITY = {
        'daily_seasonality': False,
        'weekly_seasonality': True,
        'yearly_seasonality': True
    }
    
    INDIAN_STOCKS = {
        'RELIANCE.NS': 'Reliance Industries',
        'TCS.NS': 'Tata Consultancy Services',
        'INFY.NS': 'Infosys',
        'HDFCBANK.NS': 'HDFC Bank',
        'ICICIBANK.NS': 'ICICI Bank',
        'HINDUNILVR.NS': 'Hindustan Unilever',
        'ITC.NS': 'ITC Limited',
        'SBIN.NS': 'State Bank of India',
        'BHARTIARTL.NS': 'Bharti Airtel',
        'KOTAKBANK.NS': 'Kotak Mahindra Bank',
        'LT.NS': 'Larsen & Toubro',
        'HCLTECH.NS': 'HCL Technologies',
        'ASIANPAINT.NS': 'Asian Paints',
        'MARUTI.NS': 'Maruti Suzuki',
        'BAJFINANCE.NS': 'Bajaj Finance'
    }

config = Config()

# Conditional Imports
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping
=======
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os
warnings.filterwarnings('ignore')

# Data fetching
import yfinance as yf

# Machine Learning
from sklearn.preprocessing import MinMaxScaler, RobustScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Deep Learning
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, GRU
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

# Advanced forecasting
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)

# --- Utility Functions ---
def preprocess_features(data):
    """Enhanced preprocessing with better handling of edge cases"""
    df = data.copy()
    
    # Handle infinite values
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # Forward fill then backward fill
    df = df.fillna(method='ffill').fillna(method='bfill')
    
    # Remove any remaining NaN rows
    df.dropna(inplace=True)
    
    return df

def calculate_risk_metrics(returns):
    """Calculate comprehensive risk metrics"""
    if len(returns) == 0:
        return {}
        
    return {
        'volatility': returns.std() * np.sqrt(252),
        'sharpe_ratio': (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0,
        'max_drawdown': ((returns.cumsum() + 1).cummax() - (returns.cumsum() + 1)).max(),
        'var_95': returns.quantile(0.05),
        'skewness': returns.skew(),
        'kurtosis': returns.kurtosis()
    }

# --- Enhanced Ensemble Predictor Class ---
class EnsemblePredictor:
    def __init__(self):
        self.models = {}
        
    def train_ensemble(self, X_train, y_train, ensemble_type='voting'):
        """Train ensemble with improved model selection and validation"""
        if ensemble_type == 'voting':
            model = self._create_voting_ensemble()
        elif ensemble_type == 'stacking':
            model = self._create_stacking_ensemble()
        else:
            raise ValueError("ensemble_type must be 'voting' or 'stacking'")
        
        model.fit(X_train, y_train)
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
        model.cv_score = -cv_scores.mean()
        return model

    def _create_voting_ensemble(self):
        """Create voting ensemble with optimized hyperparameters"""
        estimators = [
            ('lr', LinearRegression()),
            ('ridge', Ridge(alpha=1.0)),
            ('rf', RandomForestRegressor(n_estimators=100, max_depth=10, min_samples_split=5, random_state=config.RANDOM_STATE)),
            ('gb', GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=config.RANDOM_STATE))
        ]
        
        if XGBOOST_AVAILABLE:
            estimators.append(('xgb', XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=config.RANDOM_STATE)))
            
        return VotingRegressor(estimators)

    def _create_stacking_ensemble(self):
        """Create stacking ensemble with diverse base models"""
        base_models = [
            ('rf', RandomForestRegressor(n_estimators=50, max_depth=8, random_state=config.RANDOM_STATE)),
            ('gb', GradientBoostingRegressor(n_estimators=50, learning_rate=0.15, max_depth=5, random_state=config.RANDOM_STATE)),
            ('ridge', Ridge(alpha=0.5))
        ]
        
        if XGBOOST_AVAILABLE:
            base_models.append(('xgb', XGBRegressor(n_estimators=50, learning_rate=0.15, max_depth=5, random_state=config.RANDOM_STATE)))
            
        meta_model = Ridge(alpha=0.1)
        return StackingRegressor(estimators=base_models, final_estimator=meta_model, cv=5)

# --- Enhanced Main Stock Predictor Class ---
class IndianStockPredictor:
    def __init__(self, symbol="RELIANCE.NS", period="2y"):
=======
    try:
        from fbprophet import Prophet
        PROPHET_AVAILABLE = True
    except ImportError:
        PROPHET_AVAILABLE = False

import config

def safe_divide(numerator, denominator, default=0):
    """Safely divide two arrays/series, handling division by zero"""
    with np.errstate(divide='ignore', invalid='ignore'):
        result = np.where(denominator != 0, numerator / denominator, default)
        return np.where(np.isfinite(result), result, default)

def clean_data(df):
    """Clean data by removing infinities and extreme values"""
    # Replace infinite values with NaN
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # For each numeric column, cap extreme values at 99.9th percentile
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        if df[col].notna().sum() > 0:  # Check if column has any non-NaN values
            q99 = df[col].quantile(0.999)
            q01 = df[col].quantile(0.001)
            df[col] = df[col].clip(lower=q01, upper=q99)
    
    return df

class IndianStockPredictor:
    """
    A comprehensive stock price prediction system for Indian stocks
    Combines traditional ML, deep learning, and time-series forecasting
    """
    
    def __init__(self, symbol="RELIANCE.NS", period="2y"):
        """
        Initialize the predictor
        
        Args:
            symbol (str): Stock symbol (e.g., "RELIANCE.NS", "TCS.NS", "INFY.NS")
            period (str): Data period ("1y", "2y", "5y", "max")
        """
>>>>>>> 77cdb08d702964fb06771c5fc7bb7db3a686186b
        self.symbol = symbol
        self.period = period
        self.data = None
        self.processed_data = None
<<<<<<< HEAD
        self.X_train, self.X_test, self.y_train, self.y_test = None, None, None, None
        self.feature_scaler = RobustScaler()
        self.target_scaler = StandardScaler()
        self.models = {}
        self.ensemble_predictor = EnsemblePredictor()
        self.test_dates = None
        self.feature_names = None
        self.risk_metrics = {}
        self.predictions = {}  # Store predictions for visualization
        
    def fetch_data(self):
        """Enhanced data fetching with better error handling"""
=======
        self.scaler = RobustScaler()  # More robust to outliers than MinMaxScaler
        self.models = {}
        self.predictions = {}
        
        # Create directories if they don't exist
        self._create_directories()
        
    def _create_directories(self):
        """Create necessary directories for the project"""
        directories = [
            config.DATA_DIR,
            config.RAW_DATA_DIR,
            config.PROCESSED_DATA_DIR,
            config.MODELS_DIR,
            config.RESULTS_DIR,
            config.PLOTS_DIR,
            config.PREDICTIONS_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
    def fetch_data(self):
        """Fetch stock data from Yahoo Finance"""
        print(f"📡 Fetching data for {self.symbol}...")
        
>>>>>>> 77cdb08d702964fb06771c5fc7bb7db3a686186b
        try:
            stock = yf.Ticker(self.symbol)
            self.data = stock.history(period=self.period)
            
            if self.data.empty:
<<<<<<< HEAD
                logging.error(f"No data found for symbol {self.symbol}")
                return None
                
            self.data.columns = [col.capitalize() for col in self.data.columns]
            returns = self.data['Close'].pct_change().dropna()
            self.risk_metrics = calculate_risk_metrics(returns)
            logging.info(f"Successfully fetched {len(self.data)} data points for {self.symbol}")
            return self.data
            
        except Exception as e:
            logging.error(f"Error fetching data: {str(e)}")
            return None

    def get_stock_info(self):
        """Enhanced stock info retrieval"""
        try:
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            if self.data is not None and not self.data.empty:
                current_price = self.data['Close'].iloc[-1]
                info['current_price'] = current_price
                info['52_week_high'] = self.data['Close'].tail(252).max()
                info['52_week_low'] = self.data['Close'].tail(252).min()
                info['price_change_1d'] = ((current_price - self.data['Close'].iloc[-2]) / self.data['Close'].iloc[-2]) * 100
                
            return info
        except Exception as e:
            logging.warning(f"Could not fetch stock info: {str(e)}")
            return {}

    def _add_technical_indicators(self, df):
        """Enhanced technical indicators with more sophisticated calculations"""
        # Moving Averages
        for period in config.MA_PERIODS:
            df[f'MA_{period}'] = df['Close'].rolling(window=period).mean()
            df[f'MA_{period}_slope'] = df[f'MA_{period}'].diff(5)
            
        # EMA and MACD
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_hist'] = df['MACD'] - df['MACD_signal']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=config.RSI_PERIOD).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=config.RSI_PERIOD).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_middle'] = df['Close'].rolling(window=config.BB_PERIOD).mean()
        df['BB_std'] = df['Close'].rolling(window=config.BB_PERIOD).std()
        df['BB_upper'] = df['BB_middle'] + (df['BB_std'] * config.BB_STD)
        df['BB_lower'] = df['BB_middle'] - (df['BB_std'] * config.BB_STD)
        df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / df['BB_middle']
        df['BB_position'] = (df['Close'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower'])
        
        # Additional indicators
        df['Volatility'] = df['Close'].pct_change().rolling(window=20).std()
        df['Momentum'] = df['Close'] - df['Close'].shift(10)
        df['ROC'] = df['Close'].pct_change(periods=10)
        df['Williams_R'] = ((df['High'].rolling(14).max() - df['Close']) / 
                           (df['High'].rolling(14).max() - df['Low'].rolling(14).min())) * -100
        
        if 'Volume' in df.columns:
            df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
            df['Volume_ratio'] = df['Volume'] / df['Volume_MA']
            df['OBV'] = (df['Volume'] * np.where(df['Close'].diff() > 0, 1, -1)).cumsum()
        
        return df

    def prepare_data(self):
        """Enhanced data preparation with better feature engineering"""
        if self.data is None:
            raise ValueError("No data available. Please fetch data first.")
            
        df = self.data.copy()
        df = self._add_technical_indicators(df)
        df['Target'] = df['Close'].shift(-1)
        df = preprocess_features(df)
        
        if len(df) < config.MIN_DATA_POINTS:
            raise ValueError(f"Insufficient data ({len(df)} points) after processing. Need at least {config.MIN_DATA_POINTS}.")

        exclude_cols = ['Target', 'Dividends', 'Stock splits']
        self.feature_names = [col for col in df.columns if col not in exclude_cols]
        
        X = df[self.feature_names]
        y = df['Target']
        
        test_size = int(len(X) * config.TEST_SIZE)
        train_size = len(X) - test_size
        
        X_train_df, X_test_df = X.iloc[:train_size], X.iloc[train_size:]
        self.y_train, self.y_test = y.iloc[:train_size], y.iloc[train_size:]
        
        self.X_train = self.feature_scaler.fit_transform(X_train_df)
        self.X_test = self.feature_scaler.transform(X_test_df)
        self.processed_data = df
        self.test_dates = X_test_df.index
        
        logging.info(f"Data prepared: {len(self.X_train)} training samples, {len(self.X_test)} test samples")

    def train_linear_regression(self):
        """Train linear regression with regularization"""
        model = Ridge(alpha=1.0)
        model.fit(self.X_train, self.y_train)
        
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': np.abs(model.coef_)
        }).sort_values('importance', ascending=False)
        
        model.feature_importance = feature_importance
        self.models['Linear Regression'] = model

    def train_lstm(self, epochs=50, patience=10):
        """Enhanced LSTM training with early stopping"""
        if not TENSORFLOW_AVAILABLE:
            logging.warning("TensorFlow not available. Skipping LSTM training.")
            return
            
        sequence_length = min(60, len(self.X_train) // 4)
        X_train_lstm, y_train_lstm = self._create_sequences(self.X_train, self.y_train, sequence_length)
        
        if len(X_train_lstm) == 0:
            logging.warning("Insufficient data for LSTM training.")
            return
            
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=(sequence_length, self.X_train.shape[1])),
            Dropout(0.2),
            BatchNormalization(),
            LSTM(64, return_sequences=True),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.2),
            Dense(25, activation='relu'),
            Dense(1)
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
        
        early_stopping = EarlyStopping(monitor='val_loss', patience=patience, restore_best_weights=True)
        
        history = model.fit(
            X_train_lstm, y_train_lstm,
            epochs=epochs,
            batch_size=32,
            validation_split=0.2,
            callbacks=[early_stopping],
            verbose=0
        )
        
        model.sequence_length = sequence_length
        model.training_history = history.history
        self.models['LSTM'] = model

    def _create_sequences(self, X, y, sequence_length):
        """Create sequences for LSTM training"""
        if len(X) <= sequence_length:
            return np.array([]), np.array([])
            
        X_seq, y_seq = [], []
        for i in range(sequence_length, len(X)):
            X_seq.append(X[i-sequence_length:i])
            y_seq.append(y.iloc[i])
            
        return np.array(X_seq), np.array(y_seq)

    def train_prophet(self):
        """Enhanced Prophet training with better parameter tuning"""
        if not PROPHET_AVAILABLE:
            logging.warning("Prophet not available. Skipping Prophet training.")
            return
            
        df_prophet = self.processed_data[['Close']].reset_index()
        df_prophet.columns = ['ds', 'y']
        
        if hasattr(df_prophet['ds'].dtype, 'tz') and df_prophet['ds'].dtype.tz is not None:
            df_prophet['ds'] = df_prophet['ds'].dt.tz_localize(None)
            
        train_size = len(df_prophet) - len(self.y_test)
        df_prophet_train = df_prophet.iloc[:train_size]
        
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10,
            holidays_prior_scale=10,
            interval_width=0.8
        )
        
        model.fit(df_prophet_train)
        self.models['Prophet'] = model

    def train_ensemble(self, ensemble_type='voting'):
        """Train ensemble models with enhanced configuration"""
        model = self.ensemble_predictor.train_ensemble(self.X_train, self.y_train, ensemble_type)
        self.models[f'{ensemble_type.title()} Ensemble'] = model

    def evaluate_models(self):
        """Enhanced model evaluation with comprehensive metrics"""
        results = {}
        self.predictions = {}  # Reset predictions storage
        
        for name, model in self.models.items():
            try:
                if name == 'Prophet':
                    preds = self._get_prophet_predictions(model)
                elif name == 'LSTM':
                    preds = self._get_lstm_predictions(model)
                else:
                    preds = model.predict(self.X_test)
                
                if preds is not None and len(preds) > 0:
                    min_len = min(len(self.y_test.values), len(preds))
                    y_true = self.y_test.values[:min_len]
                    y_pred = preds[:min_len]
                    
                    results[name] = self._calculate_comprehensive_metrics(y_true, y_pred)
                    
                    # Store predictions for visualization
                    self.predictions[name] = {
                        'test_pred': y_pred,
                        'test_actual': y_true,
                        'test_dates': self.test_dates[:min_len]
                    }
                    
            except Exception as e:
                logging.error(f"Error evaluating {name}: {str(e)}")
                continue
                
        return results

    def _get_prophet_predictions(self, model):
        """Get predictions from Prophet model"""
        try:
            future = model.make_future_dataframe(periods=len(self.y_test))
            if hasattr(future['ds'].dtype, 'tz') and future['ds'].dtype.tz is not None:
                future['ds'] = future['ds'].dt.tz_localize(None)
                
            forecast = model.predict(future)
            return forecast['yhat'].iloc[-len(self.y_test):].values
        except Exception as e:
            logging.error(f"Error getting Prophet predictions: {str(e)}")
            return None

    def _get_lstm_predictions(self, model):
        """Get predictions from LSTM model"""
        try:
            sequence_length = getattr(model, 'sequence_length', 60)
            X_test_lstm, _ = self._create_sequences(self.X_test, self.y_test, sequence_length)
            
            if len(X_test_lstm) == 0:
                return None
                
            return model.predict(X_test_lstm).flatten()
        except Exception as e:
            logging.error(f"Error getting LSTM predictions: {str(e)}")
            return None

    def _calculate_comprehensive_metrics(self, y_true, y_pred):
        """Calculate comprehensive evaluation metrics"""
        min_len = min(len(y_true), len(y_pred))
        y_true = y_true[:min_len]
        y_pred = y_pred[:min_len]
        
        if len(y_true) == 0:
            return {}
            
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        actual_direction = np.diff(y_true) > 0
        pred_direction = np.diff(y_pred) > 0
        
        if len(actual_direction) > 0:
            directional_accuracy = np.mean(actual_direction == pred_direction) * 100
        else:
            directional_accuracy = 0
            
        returns_actual = np.diff(y_true) / y_true[:-1]
        returns_pred = np.diff(y_pred) / y_pred[:-1]
        
        strategy_returns = np.where(returns_pred > 0, returns_actual, 0)
        total_return = np.prod(1 + strategy_returns) - 1
        
        return {
            "RMSE": rmse,
            "MAE": mae,
            "R² Score": r2,
            "MAPE": mape,
            "Directional_Accuracy": directional_accuracy,
            "Strategy_Return": total_return * 100
        }

    def predict_future(self, days=30, best_model_name='Linear Regression'):
        """Enhanced future prediction with confidence intervals"""
        model = self.models.get(best_model_name)
        if not model:
            logging.error(f"Model {best_model_name} not found")
            return None, None, None
            
        if best_model_name == 'Prophet':
            return self._predict_future_prophet(model, days)
        elif best_model_name == 'LSTM':
            return self._predict_future_lstm(model, days)
        else:
            return self._predict_future_sklearn(model, days)

    def _predict_future_prophet(self, model, days):
        """Prophet future predictions"""
        try:
            future_dates_df = model.make_future_dataframe(periods=days)
            if hasattr(future_dates_df['ds'].dtype, 'tz'):
                future_dates_df['ds'] = future_dates_df['ds'].dt.tz_localize(None)
                
            forecast = model.predict(future_dates_df)
            predictions = forecast['yhat'].tail(days).values
            lower_bound = forecast['yhat_lower'].tail(days).values
            upper_bound = forecast['yhat_upper'].tail(days).values
            
            future_dates = pd.to_datetime([
                self.test_dates[-1] + timedelta(days=i) 
                for i in range(1, days + 1)
            ])
            
            return predictions, future_dates, (lower_bound, upper_bound)
        except Exception as e:
            logging.error(f"Error in Prophet prediction: {str(e)}")
            return None, None, None

    def _predict_future_lstm(self, model, days):
        """LSTM future predictions"""
        try:
            sequence_length = getattr(model, 'sequence_length', 60)
            last_sequence = self.X_test[-sequence_length:].reshape(1, sequence_length, -1)
            
            predictions = []
            current_sequence = last_sequence.copy()
            
            for _ in range(days):
                pred = model.predict(current_sequence, verbose=0)[0][0]
                predictions.append(pred)
                
                new_features = current_sequence[0, -1, :].copy()
                new_features[self.feature_names.index('Close')] = pred
                
                new_sequence = np.append(
                    current_sequence[0, 1:, :],
                    new_features.reshape(1, -1),
                    axis=0
                ).reshape(1, sequence_length, -1)
                
                current_sequence = new_sequence
            
            future_dates = pd.to_datetime([
                self.test_dates[-1] + timedelta(days=i)
                for i in range(1, days + 1)
            ])
            
            return np.array(predictions), future_dates, None
        except Exception as e:
            logging.error(f"Error in LSTM prediction: {str(e)}")
            return None, None, None

    def _predict_future_sklearn(self, model, days):
        """Sklearn model future predictions"""
        try:
            last_features = self.X_test[-1].reshape(1, -1)
            predictions = []
            
            for _ in range(days):
                pred = model.predict(last_features)[0]
                predictions.append(pred)
                
                new_features = last_features.copy()
                close_idx = self.feature_names.index('Close')
                new_features[0, close_idx] = pred
                last_features = new_features
            
            future_dates = pd.to_datetime([
                self.test_dates[-1] + timedelta(days=i)
                for i in range(1, days + 1)
            ])
            
            return np.array(predictions), future_dates, None
        except Exception as e:
            logging.error(f"Error in sklearn prediction: {str(e)}")
            return None, None, None

    def run_monte_carlo_simulation(self, future_predictions, days=30, simulations=1000):
        """Enhanced Monte Carlo simulation with better statistical modeling"""
        if self.processed_data is None or len(future_predictions) == 0:
            return None
            
        daily_returns = self.processed_data['Close'].pct_change().dropna()
        mean_return = daily_returns.mean()
        std_dev = daily_returns.std()
        
        simulated_paths = np.zeros((days, simulations))
        initial_price = future_predictions[0] if len(future_predictions) > 0 else self.processed_data['Close'].iloc[-1]
        
        for i in range(simulations):
            prices = [initial_price]
            
            for d in range(1, days):
                if np.random.random() < 0.05:
                    shock = np.random.normal(mean_return, std_dev * 3)
                else:
                    shock = np.random.normal(mean_return, std_dev)
                
                next_price = prices[-1] * (1 + shock)
                prices.append(max(next_price, 0.01))
                
            simulated_paths[:, i] = prices
            
        return simulated_paths

    def generate_trading_signals(self):
        """Generate trading signals based on technical indicators"""
        if self.processed_data is None:
            return pd.Series(dtype='float64')
        
        df = self.processed_data.copy()
        
        # MACD Strategy
        df['MACD_Signal'] = 0
        df.loc[(df['MACD'] > df['MACD_signal']) & 
               (df['MACD'].shift(1) <= df['MACD_signal'].shift(1)), 'MACD_Signal'] = 1
        df.loc[(df['MACD'] < df['MACD_signal']) & 
               (df['MACD'].shift(1) >= df['MACD_signal'].shift(1)), 'MACD_Signal'] = -1
        
        # RSI Strategy
        df['RSI_Signal'] = 0
        df.loc[(df['RSI'] < 30) & (df['RSI'].shift(1) >= 30), 'RSI_Signal'] = 1
        df.loc[(df['RSI'] > 70) & (df['RSI'].shift(1) <= 70), 'RSI_Signal'] = -1
        
        # Bollinger Bands Strategy
        df['BB_Signal'] = 0
        df.loc[(df['Close'] < df['BB_lower']) & (df['Close'].shift(1) >= df['BB_lower']), 'BB_Signal'] = 1
        df.loc[(df['Close'] > df['BB_upper']) & (df['Close'].shift(1) <= df['BB_upper']), 'BB_Signal'] = -1
        
        # Combined Signal
        df['Combined_Signal'] = df['MACD_Signal'] + df['RSI_Signal'] + df['BB_Signal']
        
        # Simplified final signal
        final_signal = pd.Series(0, index=df.index)
        final_signal[df['Combined_Signal'] >= 2] = 1
        final_signal[df['Combined_Signal'] <= -2] = -1
        
        return final_signal

    def generate_trading_report(self):
        """Generate comprehensive trading report"""
        if self.processed_data is None:
            return {}
            
        current_price = self.processed_data['Close'].iloc[-1]
        returns = self.processed_data['Close'].pct_change().dropna()
        latest_data = self.processed_data.iloc[-1]
        
        report = {
            'current_price': current_price,
            'daily_change': ((current_price - self.processed_data['Close'].iloc[-2]) / 
                           self.processed_data['Close'].iloc[-2]) * 100,
            'rsi': latest_data.get('RSI', 'N/A'),
            'macd_signal': 'Bullish' if latest_data.get('MACD', 0) > latest_data.get('MACD_signal', 0) else 'Bearish',
            'bb_position': latest_data.get('BB_position', 'N/A'),
            'volatility': returns.std() * np.sqrt(252) * 100,
            'risk_metrics': self.risk_metrics
        }
        
        # Trading recommendation
        signals = []
        if latest_data.get('RSI', 50) < 30:
            signals.append('RSI indicates oversold condition')
        elif latest_data.get('RSI', 50) > 70:
            signals.append('RSI indicates overbought condition')
            
        if latest_data.get('MACD', 0) > latest_data.get('MACD_signal', 0):
            signals.append('MACD shows bullish momentum')
        else:
            signals.append('MACD shows bearish momentum')
            
        report['signals'] = signals
        
        return report
=======
                raise ValueError(f"No data found for symbol {self.symbol}")
                
            print(f"✅ Data fetched successfully: {len(self.data)} records")
            print(f"📅 Date range: {self.data.index[0].date()} to {self.data.index[-1].date()}")
            
            # Save raw data
            try:
                self.data.to_csv(f"{config.RAW_DATA_DIR}{self.symbol}_{self.period}_raw.csv")
            except:
                pass
            
            return self.data
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None
    
    def add_technical_indicators(self, df):
        """Add technical indicators for better prediction"""
        
        # Only add indicators if we have enough data
        min_period_needed = max(config.MA_PERIODS + config.EMA_PERIODS + [config.RSI_PERIOD, config.BB_PERIOD])
        
        if len(df) < min_period_needed:
            print(f"⚠️ Limited data ({len(df)} points). Adding basic indicators only.")
            # Add only basic indicators for small datasets
            if len(df) >= 5:
                df['MA_5'] = df['Close'].rolling(window=5, min_periods=1).mean()
                df['Price_Change'] = df['Close'].pct_change().fillna(0)
                df['Volatility'] = df['Price_Change'].rolling(window=5, min_periods=1).std().fillna(0)
            return df
        
        # Moving averages
        for period in config.MA_PERIODS:
            if len(df) >= period:
                df[f'MA_{period}'] = df['Close'].rolling(window=period, min_periods=max(1, period//2)).mean()
        
        # Exponential moving averages
        for period in config.EMA_PERIODS:
            if len(df) >= period:
                df[f'EMA_{period}'] = df['Close'].ewm(span=period, min_periods=max(1, period//2)).mean()
        
        # MACD (Moving Average Convergence Divergence)
        if 'EMA_12' in df.columns and 'EMA_26' in df.columns:
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_signal'] = df['MACD'].ewm(span=config.MACD_SIGNAL, min_periods=1).mean()
            df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
        
        # RSI (Relative Strength Index) - Improved calculation
        if len(df) >= config.RSI_PERIOD:
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(window=config.RSI_PERIOD, min_periods=max(1, config.RSI_PERIOD//2)).mean()
            avg_loss = loss.rolling(window=config.RSI_PERIOD, min_periods=max(1, config.RSI_PERIOD//2)).mean()
            
            rs = safe_divide(avg_gain, avg_loss, 0)
            df['RSI'] = 100 - safe_divide(100, (1 + rs), 50)
        
        # Bollinger Bands
        if len(df) >= config.BB_PERIOD:
            df['BB_middle'] = df['Close'].rolling(window=config.BB_PERIOD, min_periods=max(1, config.BB_PERIOD//2)).mean()
            std = df['Close'].rolling(window=config.BB_PERIOD, min_periods=max(1, config.BB_PERIOD//2)).std()
            df['BB_upper'] = df['BB_middle'] + (std * config.BB_STD)
            df['BB_lower'] = df['BB_middle'] - (std * config.BB_STD)
            df['BB_width'] = df['BB_upper'] - df['BB_lower']
            df['BB_position'] = safe_divide((df['Close'] - df['BB_lower']), (df['BB_upper'] - df['BB_lower']), 0.5)
        
        # Stochastic Oscillator
        if len(df) >= 14:
            low_14 = df['Low'].rolling(window=14, min_periods=7).min()
            high_14 = df['High'].rolling(window=14, min_periods=7).max()
            df['Stoch_K'] = safe_divide(100 * (df['Close'] - low_14), (high_14 - low_14), 50)
            df['Stoch_D'] = df['Stoch_K'].rolling(window=3, min_periods=1).mean()
        
        # Williams %R
        if len(df) >= 14:
            df['Williams_R'] = safe_divide(-100 * (high_14 - df['Close']), (high_14 - low_14), -50)
        
        # Volume indicators
        df['Volume_MA'] = df['Volume'].rolling(window=min(20, len(df)), min_periods=1).mean()
        df['Volume_ratio'] = safe_divide(df['Volume'], df['Volume_MA'], 1.0)
        df['Volume_rate_of_change'] = df['Volume'].pct_change(periods=min(10, len(df)//2)).fillna(0)
        
        # Price features
        df['High_Low_Pct'] = safe_divide((df['High'] - df['Low']), df['Close'], 0)
        df['Price_Change'] = df['Close'].pct_change().fillna(0)
        df['Price_Range'] = df['High'] - df['Low']
        df['Open_Close_ratio'] = safe_divide(df['Open'], df['Close'], 1.0)
        df['High_Close_ratio'] = safe_divide(df['High'], df['Close'], 1.0)
        df['Low_Close_ratio'] = safe_divide(df['Low'], df['Close'], 1.0)
        
        # Volatility indicators
        df['Volatility'] = df['Price_Change'].rolling(window=min(10, len(df)), min_periods=1).std().fillna(0)
        df['Volatility_MA'] = df['Volatility'].rolling(window=min(10, len(df)), min_periods=1).mean().fillna(0)
        
        # Momentum indicators
        momentum_period = min(10, len(df)//2)
        if momentum_period > 0:
            df['Momentum'] = df['Close'] - df['Close'].shift(momentum_period)
            df['ROC'] = df['Close'].pct_change(periods=momentum_period).fillna(0) * 100
        
        # Average True Range (ATR)
        if len(df) >= 14:
            df['TR1'] = df['High'] - df['Low']
            df['TR2'] = abs(df['High'] - df['Close'].shift())
            df['TR3'] = abs(df['Low'] - df['Close'].shift())
            df['True_Range'] = df[['TR1', 'TR2', 'TR3']].max(axis=1)
            df['ATR'] = df['True_Range'].rolling(window=14, min_periods=7).mean()
            df.drop(['TR1', 'TR2', 'TR3'], axis=1, inplace=True)
        
        # Clean the data to remove infinities and extreme values
        df = clean_data(df)
        
        # Fill any remaining NaN values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if df[col].isna().any():
                # Forward fill first, then backward fill
                df[col] = df[col].fillna(method='ffill').fillna(method='bfill')
                # If still NaN, fill with column median (more robust than mean)
                if df[col].isna().any():
                    df[col] = df[col].fillna(df[col].median())
        
        return df
    
    def prepare_data(self):
        """Prepare and engineer features for modeling"""
        if self.data is None:
            self.fetch_data()
        
        print("🔧 Preparing data and engineering features...")
        
        # Create a copy for processing
        df = self.data.copy()
        
        # Check initial data size
        print(f"📊 Initial data points: {len(df)}")
        
        # Add technical indicators
        df = self.add_technical_indicators(df)
        
        # Create lag features if enabled and we have enough data
        if config.USE_LAG_FEATURES and len(df) > max(config.LAG_PERIODS):
            for lag in config.LAG_PERIODS:
                if lag < len(df):
                    df[f'Close_lag_{lag}'] = df['Close'].shift(lag)
                    df[f'Volume_lag_{lag}'] = df['Volume'].shift(lag)
                    df[f'High_lag_{lag}'] = df['High'].shift(lag)
                    df[f'Low_lag_{lag}'] = df['Low'].shift(lag)
        
        # Create future target (next day's closing price)
        df['Target'] = df['Close'].shift(-1)
        
        # Handle NaN values more gracefully
        initial_length = len(df)
        
        # First, try forward fill and backward fill
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        # If we still have NaN values, fill with appropriate defaults
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if df[col].isna().any():
                if 'lag' in col.lower():
                    # For lag features, use the median of the original column
                    base_col = col.split('_lag_')[0]
                    if base_col in df.columns:
                        df[col] = df[col].fillna(df[base_col].median())
                    else:
                        df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(df[col].median())
        
        # Remove the last row (Target is NaN)
        df = df.iloc[:-1]
        
        # Final cleanup - remove any remaining NaN rows
        df = df.dropna()
        
        # Clean data one more time
        df = clean_data(df)
        
        print(f"📊 After processing: {len(df)} data points (removed {initial_length - len(df)} rows)")
        
        # Adaptive minimum data points based on available data
        adaptive_min = min(config.MIN_DATA_POINTS, max(20, len(self.data) // 4))
        
        # Data quality checks
        if len(df) < adaptive_min:
            raise ValueError(f"Insufficient data points: {len(df)} < {adaptive_min}. Try a longer time period or different stock.")
        
        self.processed_data = df
        
        # Save processed data
        try:
            df.to_csv(f"{config.PROCESSED_DATA_DIR}{self.symbol}_{self.period}_processed.csv")
        except:
            pass  # Directory might not exist in web environment
        
        print(f"✅ Data prepared: {len(df)} records with {len(df.columns)} features")
        
        return df
    
    def split_data(self, test_size=None):
        """Split data into train and test sets"""
        if self.processed_data is None:
            self.prepare_data()
        
        if test_size is None:
            test_size = config.TEST_SIZE
        
        # Ensure we have enough data for both train and test
        min_test_size = max(5, int(len(self.processed_data) * 0.1))
        min_train_size = max(10, int(len(self.processed_data) * 0.6))
        
        # Adjust test size if necessary
        calculated_test_size = int(len(self.processed_data) * test_size)
        calculated_test_size = max(min_test_size, min(calculated_test_size, len(self.processed_data) - min_train_size))
        
        split_point = len(self.processed_data) - calculated_test_size
        
        train_data = self.processed_data[:split_point]
        test_data = self.processed_data[split_point:]
        
        print(f"📊 Data split - Train: {len(train_data)}, Test: {len(test_data)}")
        
        return train_data, test_data
    
    def train_linear_regression(self):
        """Train Linear Regression model"""
        print("🤖 Training Linear Regression model...")
        
        train_data, test_data = self.split_data()
        
        # Select features (excluding target and non-numeric columns)
        feature_columns = [col for col in train_data.columns 
                          if col not in ['Target'] and 
                          train_data[col].dtype in ['int64', 'float64']]
        
        X_train = train_data[feature_columns].copy()
        y_train = train_data['Target'].copy()
        X_test = test_data[feature_columns].copy()
        y_test = test_data['Target'].copy()
        
        # Handle any remaining NaN values and infinities
        X_train = X_train.fillna(X_train.median())
        X_test = X_test.fillna(X_train.median())  # Use train median for test
        
        # Clean data one more time
        X_train = X_train.replace([np.inf, -np.inf], np.nan).fillna(X_train.median())
        X_test = X_test.replace([np.inf, -np.inf], np.nan).fillna(X_train.median())
        
        # Verify no infinite or extreme values remain
        for col in X_train.columns:
            if not np.isfinite(X_train[col]).all():
                print(f"Warning: Found non-finite values in {col}, replacing with median")
                X_train[col] = X_train[col].replace([np.inf, -np.inf], X_train[col].median())
            if not np.isfinite(X_test[col]).all():
                X_test[col] = X_test[col].replace([np.inf, -np.inf], X_train[col].median())
        
        # Train model
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)
        
        # Make predictions
        train_pred = lr_model.predict(X_train)
        test_pred = lr_model.predict(X_test)
        
        # Store model and predictions
        self.models['linear_regression'] = lr_model
        self.predictions['linear_regression'] = {
            'train_pred': train_pred,
            'test_pred': test_pred,
            'train_actual': y_train.values,
            'test_actual': y_test.values,
            'test_dates': test_data.index,
            'feature_importance': dict(zip(feature_columns, lr_model.coef_))
        }
        
        # Calculate metrics
        train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        test_r2 = r2_score(y_test, test_pred)
        
        print(f"📈 Linear Regression - Train RMSE: {train_rmse:.2f}, Test RMSE: {test_rmse:.2f}, R²: {test_r2:.4f}")
        
        return lr_model
    
    def prepare_lstm_data(self, sequence_length=None):
        """Prepare data for LSTM model"""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow not available. Please install: pip install tensorflow")
            
        if self.processed_data is None:
            self.prepare_data()
        
        if sequence_length is None:
            # Adaptive sequence length based on data size
            sequence_length = min(config.LSTM_SEQUENCE_LENGTH, len(self.processed_data) // 4)
            sequence_length = max(5, sequence_length)  # Minimum sequence length
        
        # Use only Close price for LSTM (simpler and more stable)
        data = self.processed_data['Close'].values.reshape(-1, 1)
        
        # Scale the data
        scaled_data = self.scaler.fit_transform(data)
        
        # Create sequences
        X, y = [], []
        for i in range(sequence_length, len(scaled_data)):
            X.append(scaled_data[i-sequence_length:i, 0])
            y.append(scaled_data[i, 0])
        
        if len(X) == 0:
            raise ValueError(f"Not enough data for LSTM. Need at least {sequence_length + 1} points.")
        
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        # Split data
        test_size = min(config.TEST_SIZE, 0.3)  # Cap test size at 30%
        split_point = max(1, int(len(X) * (1 - test_size)))
        
        X_train, X_test = X[:split_point], X[split_point:]
        y_train, y_test = y[:split_point], y[split_point:]
        
        return X_train, X_test, y_train, y_test, sequence_length
    
    def build_lstm_model(self, sequence_length=None):
        """Build LSTM model architecture"""
        if sequence_length is None:
            sequence_length = config.LSTM_SEQUENCE_LENGTH
            
        model = Sequential([
            LSTM(32, return_sequences=True, input_shape=(sequence_length, 1)),
            Dropout(0.2),
            
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            
            Dense(16),
            Dense(1)
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
        return model
    
    def train_lstm(self, sequence_length=None, epochs=None, batch_size=None):
        """Train LSTM model"""
        if not TENSORFLOW_AVAILABLE:
            print("⚠️ TensorFlow not available. Skipping LSTM training.")
            return None
            
        print("🧠 Training LSTM model...")
        
        if epochs is None:
            epochs = config.LSTM_EPOCHS
        if batch_size is None:
            batch_size = config.LSTM_BATCH_SIZE
        
        try:
            # Prepare data
            X_train, X_test, y_train, y_test, actual_seq_length = self.prepare_lstm_data(sequence_length)
            
            # Build model
            lstm_model = self.build_lstm_model(actual_seq_length)
            
            # Callbacks
            early_stopping = EarlyStopping(
                monitor='val_loss', 
                patience=10, 
                restore_best_weights=True,
                verbose=0
            )
            reduce_lr = ReduceLROnPlateau(
                monitor='val_loss', 
                factor=0.2, 
                patience=5, 
                min_lr=0.0001,
                verbose=0
            )
            
            # Train model
            history = lstm_model.fit(
                X_train, y_train,
                batch_size=batch_size,
                epochs=epochs,
                validation_data=(X_test, y_test),
                callbacks=[early_stopping, reduce_lr],
                verbose=config.VERBOSE
            )
            
            # Make predictions
            train_pred = lstm_model.predict(X_train, verbose=0)
            test_pred = lstm_model.predict(X_test, verbose=0)
            
            # Inverse transform predictions
            train_pred = self.scaler.inverse_transform(train_pred)
            test_pred = self.scaler.inverse_transform(test_pred)
            y_train_actual = self.scaler.inverse_transform(y_train.reshape(-1, 1))
            y_test_actual = self.scaler.inverse_transform(y_test.reshape(-1, 1))
            
            # Store model and predictions
            self.models['lstm'] = lstm_model
            self.predictions['lstm'] = {
                'train_pred': train_pred.flatten(),
                'test_pred': test_pred.flatten(),
                'train_actual': y_train_actual.flatten(),
                'test_actual': y_test_actual.flatten(),
                'history': history,
                'test_dates': self.processed_data.index[-len(y_test):],
                'sequence_length': actual_seq_length
            }
            
            # Calculate metrics
            train_rmse = np.sqrt(mean_squared_error(y_train_actual, train_pred))
            test_rmse = np.sqrt(mean_squared_error(y_test_actual, test_pred))
            test_r2 = r2_score(y_test_actual, test_pred)
            
            print(f"🧠 LSTM - Train RMSE: {train_rmse:.2f}, Test RMSE: {test_rmse:.2f}, R²: {test_r2:.4f}")
            
            return lstm_model
            
        except Exception as e:
            print(f"❌ LSTM training failed: {e}")
            return None
    
    def train_prophet(self):
        """Train Prophet model for time-series forecasting"""
        if not PROPHET_AVAILABLE:
            print("⚠️ Prophet not available. Skipping Prophet training.")
            return None
            
        print("📊 Training Prophet model...")
        
        if self.processed_data is None:
            self.prepare_data()
        
        try:
            # Prepare data for Prophet
            prophet_data = pd.DataFrame({
                'ds': self.processed_data.index.tz_localize(None) if self.processed_data.index.tz else self.processed_data.index,
                'y': self.processed_data['Close']
            })
            
            # Split data
            test_size = min(config.TEST_SIZE, 0.3)
            split_point = max(1, int(len(prophet_data) * (1 - test_size)))
            train_data = prophet_data[:split_point]
            test_data = prophet_data[split_point:]
            
            # Train Prophet model
            prophet_model = Prophet(
                daily_seasonality=config.PROPHET_SEASONALITY['daily_seasonality'],
                weekly_seasonality=config.PROPHET_SEASONALITY['weekly_seasonality'],
                yearly_seasonality=config.PROPHET_SEASONALITY['yearly_seasonality'] and len(train_data) > 365,
                changepoint_prior_scale=config.PROPHET_CHANGEPOINT_PRIOR_SCALE
            )
            
            # Suppress Prophet's verbose output
            import logging
            logging.getLogger('prophet').setLevel(logging.WARNING)
            logging.getLogger('cmdstanpy').setLevel(logging.WARNING)
            
            prophet_model.fit(train_data)
            
            # Make predictions
            future = prophet_model.make_future_dataframe(periods=len(test_data))
            forecast = prophet_model.predict(future)
            
            # Extract predictions
            train_pred = forecast['yhat'][:len(train_data)].values
            test_pred = forecast['yhat'][len(train_data):].values
            
            # Store model and predictions
            self.models['prophet'] = prophet_model
            self.predictions['prophet'] = {
                'train_pred': train_pred,
                'test_pred': test_pred,
                'train_actual': train_data['y'].values,
                'test_actual': test_data['y'].values,
                'forecast': forecast,
                'test_dates': test_data['ds']
            }
            
            # Calculate metrics
            train_rmse = np.sqrt(mean_squared_error(train_data['y'], train_pred))
            test_rmse = np.sqrt(mean_squared_error(test_data['y'], test_pred))
            test_r2 = r2_score(test_data['y'], test_pred)
            
            print(f"📊 Prophet - Train RMSE: {train_rmse:.2f}, Test RMSE: {test_rmse:.2f}, R²: {test_r2:.4f}")
            
            return prophet_model
            
        except Exception as e:
            print(f"❌ Prophet training failed: {e}")
            return None
    
    def evaluate_models(self):
        """Evaluate and compare all models"""
        print("\n" + "="*60)
        print("📊 MODEL EVALUATION SUMMARY")
        print("="*60)
        
        results = {}
        
        for model_name, pred_data in self.predictions.items():
            try:
                test_rmse = np.sqrt(mean_squared_error(pred_data['test_actual'], pred_data['test_pred']))
                test_mae = mean_absolute_error(pred_data['test_actual'], pred_data['test_pred'])
                test_r2 = r2_score(pred_data['test_actual'], pred_data['test_pred'])
                
                # Calculate MAPE (Mean Absolute Percentage Error)
                mape = np.mean(np.abs(safe_divide(pred_data['test_actual'] - pred_data['test_pred'], pred_data['test_actual'], 0))) * 100
                
                # Calculate directional accuracy
                if len(pred_data['test_actual']) > 1:
                    actual_direction = np.diff(pred_data['test_actual']) > 0
                    pred_direction = np.diff(pred_data['test_pred']) > 0
                    directional_accuracy = np.mean(actual_direction == pred_direction) * 100
                else:
                    directional_accuracy = 0
                
                results[model_name] = {
                    'RMSE': test_rmse,
                    'MAE': test_mae,
                    'R²': test_r2,
                    'MAPE': mape,
                    'Directional_Accuracy': directional_accuracy
                }
                
                print(f"\n🤖 {model_name.upper()}:")
                print(f"   RMSE: {config.CURRENCY_SYMBOL}{test_rmse:.2f}")
                print(f"   MAE:  {config.CURRENCY_SYMBOL}{test_mae:.2f}")
                print(f"   R²:   {test_r2:.4f}")
                print(f"   MAPE: {mape:.2f}%")
                print(f"   Direction Accuracy: {directional_accuracy:.1f}%")
                
            except Exception as e:
                print(f"❌ Error evaluating {model_name}: {e}")
                continue
        
        # Save results
        if results:
            try:
                results_df = pd.DataFrame(results).T
                results_df.to_csv(f"{config.RESULTS_DIR}model_comparison_{self.symbol}.csv")
            except:
                pass  # Directory might not exist
        
        return results
    
    def predict_future(self, days=None):
        """Predict future stock prices"""
        if days is None:
            days = config.PREDICTION_DAYS
            
        print(f"\n🔮 Predicting next {days} days...")
        
        future_predictions = {}
        current_price = self.processed_data['Close'].iloc[-1]
        
        # LSTM predictions
        if 'lstm' in self.models and 'lstm' in self.predictions:
            try:
                seq_length = self.predictions['lstm'].get('sequence_length', config.LSTM_SEQUENCE_LENGTH)
                seq_length = min(seq_length, len(self.processed_data))
                
                last_sequence = self.scaler.transform(
                    self.processed_data['Close'].tail(seq_length).values.reshape(-1, 1)
                )
                
                future_pred = []
                current_sequence = last_sequence.copy()
                
                for _ in range(days):
                    # Reshape for LSTM input
                    input_seq = current_sequence[-seq_length:].reshape(1, seq_length, 1)
                    next_pred = self.models['lstm'].predict(input_seq, verbose=0)
                    future_pred.append(next_pred[0, 0])
                    
                    # Update sequence
                    current_sequence = np.append(current_sequence, next_pred)
                
                # Inverse transform
                future_pred = self.scaler.inverse_transform(np.array(future_pred).reshape(-1, 1))
                future_predictions['LSTM'] = future_pred.flatten()
                
            except Exception as e:
                print(f"❌ LSTM prediction failed: {e}")
        
        # Prophet predictions
        if 'prophet' in self.models:
            try:
                future_dates = self.models['prophet'].make_future_dataframe(periods=days)
                forecast = self.models['prophet'].predict(future_dates)
                future_predictions['Prophet'] = forecast['yhat'].tail(days).values
            except Exception as e:
                print(f"❌ Prophet prediction failed: {e}")
        
        # Linear Regression predictions (simplified approach)
        if 'linear_regression' in self.models:
            try:
                # Use last known values to predict
                last_features = self.processed_data.iloc[-1:].drop(['Target'], axis=1, errors='ignore')
                last_features = last_features.select_dtypes(include=[np.number])
                
                # Clean the features
                last_features = last_features.replace([np.inf, -np.inf], np.nan).fillna(last_features.median())
                
                lr_predictions = []
                for _ in range(days):
                    next_pred = self.models['linear_regression'].predict(last_features)[0]
                    lr_predictions.append(next_pred)
                    # Simple approach: assume features remain similar
                
                future_predictions['Linear_Regression'] = lr_predictions
            except Exception as e:
                print(f"❌ Linear Regression prediction failed: {e}")
        
        # Create future dates
        last_date = self.processed_data.index[-1]
        future_dates = [last_date + timedelta(days=i+1) for i in range(days)]
        
        # Create predictions DataFrame
        if future_predictions:
            try:
                predictions_df = pd.DataFrame(future_predictions, index=future_dates)
                predictions_df.to_csv(f"{config.PREDICTIONS_DIR}{self.symbol}_future_predictions.csv")
            except:
                pass
        
        # Display predictions
        print(f"\n📈 Future Price Predictions for {self.symbol}:")
        print("-" * 50)
        
        print(f"Current Price: {config.CURRENCY_SYMBOL}{current_price:.2f}")
        print()
        
        for model_name, predictions in future_predictions.items():
            print(f"{model_name}:")
            for i, (date, price) in enumerate(zip(future_dates[:10], predictions[:10])):
                change = safe_divide((price - current_price), current_price, 0) * 100
                direction = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                print(f"  {date.strftime('%Y-%m-%d')}: {config.CURRENCY_SYMBOL}{price:.2f} ({change:+.1f}%) {direction}")
            
            if days > 10:
                print(f"  ... (showing first 10 of {days} predictions)")
            print()
        
        return future_predictions, future_dates
    
    def generate_trading_signals(self):
        """Generate buy/sell signals based on technical indicators"""
        if self.processed_data is None:
            self.prepare_data()
        
        df = self.processed_data.copy()
        signals = pd.Series(0, index=df.index)  # 0 = Hold, 1 = Buy, -1 = Sell
        
        # Moving average crossover strategy
        if 'MA_5' in df.columns and 'MA_20' in df.columns:
            ma5_above = df['MA_5'] > df['MA_20']
            ma5_above_prev = df['MA_5'].shift(1) > df['MA_20'].shift(1)
            
            # Golden cross (buy signal)
            golden_cross = ma5_above & ~ma5_above_prev
            signals[golden_cross] = 1
            
            # Death cross (sell signal)
            death_cross = ~ma5_above & ma5_above_prev
            signals[death_cross] = -1
        
        # RSI-based signals
        if 'RSI' in df.columns:
            oversold = (df['RSI'] < 30) & (signals != -1)
            overbought = (df['RSI'] > 70) & (signals != 1)
            
            signals[oversold] = 1  # Buy
            signals[overbought] = -1  # Sell
        
        # MACD signals
        if 'MACD' in df.columns and 'MACD_signal' in df.columns:
            macd_above = df['MACD'] > df['MACD_signal']
            macd_above_prev = df['MACD'].shift(1) > df['MACD_signal'].shift(1)
            
            macd_bullish = macd_above & ~macd_above_prev
            macd_bearish = ~macd_above & macd_above_prev
            
            signals[macd_bullish] = 1
            signals[macd_bearish] = -1
        
        # Bollinger Bands signals
        if all(col in df.columns for col in ['BB_upper', 'BB_lower', 'Close']):
            bb_buy = (df['Close'] < df['BB_lower']) & (signals != -1)
            bb_sell = (df['Close'] > df['BB_upper']) & (signals != 1)
            
            signals[bb_buy] = 1
            signals[bb_sell] = -1
        
        return signals
    
    def save_results(self):
        """Save all results to files"""
        print("💾 Saving results...")
        
        try:
            # Save processed data
            if self.processed_data is not None:
                self.processed_data.to_csv(f"{config.RESULTS_DIR}{self.symbol}_processed_data.csv")
            
            # Save model predictions
            for model_name, pred_data in self.predictions.items():
                results = pd.DataFrame({
                    'Date': pred_data['test_dates'],
                    'Actual': pred_data['test_actual'],
                    'Predicted': pred_data['test_pred']
                })
                results.to_csv(f"{config.RESULTS_DIR}{self.symbol}_{model_name}_predictions.csv", index=False)
            
            # Save trading signals
            signals = self.generate_trading_signals()
            signals_df = pd.DataFrame({
                'Date': signals.index,
                'Signal': signals.values
            })
            signals_df.to_csv(f"{config.RESULTS_DIR}{self.symbol}_trading_signals.csv", index=False)
            
            print("✅ Results saved successfully!")
            
        except Exception as e:
            print(f"⚠️ Could not save some results: {e}")
    
    def plot_predictions(self):
        """Plot actual vs predicted prices for all trained models"""
        if not self.predictions:
            print("⚠️ No predictions available to plot. Train a model first.")
            return
        
        for model_name, pred_data in self.predictions.items():
            try:
                plt.figure(figsize=config.FIGURE_SIZE, dpi=config.DPI)
                
                # Actual
                plt.plot(pred_data['test_dates'], pred_data['test_actual'], label='Actual', linewidth=2)
                # Predicted
                plt.plot(pred_data['test_dates'], pred_data['test_pred'], label='Predicted', linestyle='--', linewidth=2)
                
                plt.title(f"{self.symbol} - {model_name.upper()} Predictions")
                plt.xlabel("Date")
                plt.ylabel(f"Price ({config.CURRENCY_SYMBOL})")
                plt.legend()
                plt.tight_layout()
                
                if config.SAVE_PLOTS:
                    os.makedirs(config.PLOTS_DIR, exist_ok=True)
                    out_path = f"{config.PLOTS_DIR}{self.symbol}_{model_name}_predictions.{config.PLOT_FORMAT}"
                    plt.savefig(out_path)
                    print(f"🖼️ Saved plot: {out_path}")
                
                if config.SHOW_PLOTS:
                    plt.show()
                else:
                    plt.close()
            except Exception as e:
                print(f"⚠️ Could not plot {model_name}: {e}")
    
    def get_stock_info(self):
        """Get comprehensive stock information"""
        try:
            stock = yf.Ticker(self.symbol)
            info = stock.info

            stock_details = {
                'symbol': self.symbol,
                'company_name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'market_cap_formatted': f"₹{info.get('marketCap', 0):,}" if isinstance(info.get('marketCap'), int) else 'N/A',
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'pb_ratio': info.get('priceToBook', 'N/A'),
                'dividend_yield': f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else 'N/A',
                'beta': info.get('beta', 'N/A'),
                '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                'current_price': info.get('currentPrice', 'N/A'),
                'previous_close': info.get('regularMarketPreviousClose', 'N/A'),
                'day_change': info.get('regularMarketChange', 'N/A'),
                'day_change_percent': f"{info.get('regularMarketChangePercent', 0) * 100:.2f}%" if info.get('regularMarketChangePercent') else 'N/A',
                'volume': info.get('regularMarketVolume', 'N/A'),
                'avg_volume': info.get('averageVolume', 'N/A'),
                'website': info.get('website', 'N/A'),
                'summary': info.get('longBusinessSummary', 'N/A'),
                'country': info.get('country', 'N/A'),
                'currency': info.get('currency', 'N/A'),
                'exchange': info.get('exchange', 'N/A'),
                'quote_type': info.get('quoteType', 'N/A'),
                'short_name': info.get('shortName', 'N/A'),
                'logo_url': info.get('logo_url', 'N/A'),
            }

            return stock_details

        except Exception as e:
            print(f"❌ Failed to fetch stock info: {e}")
            return None

    def save_stock_info(self):
        """Save stock info to a JSON file"""
        info = self.get_stock_info()
        if info:
            import json
            with open(f"{config.RESULTS_DIR}{self.symbol}_info.json", 'w') as f:
                json.dump(info, f, indent=4)
            print(f"✅ Stock info saved to {config.RESULTS_DIR}{self.symbol}_info.json")

# Helper function for easy usage
def quick_predict(symbol, period="2y", models=['linear_regression', 'lstm', 'prophet']):
    """Quick prediction function for easy usage"""
    predictor = IndianStockPredictor(symbol=symbol, period=period)

    # Fetch and prepare data
    if predictor.fetch_data() is None:
        return None, None, None

    try:
        predictor.prepare_data()
    except ValueError as e:
        print(f"❌ Data preparation failed: {e}")
        return None, None, None

    # Train selected models
    if 'linear_regression' in models:
        predictor.train_linear_regression()
    if 'lstm' in models and TENSORFLOW_AVAILABLE:
        predictor.train_lstm()
    if 'prophet' in models and PROPHET_AVAILABLE:
        predictor.train_prophet()

    # Evaluate and predict
    predictor.evaluate_models()

    try:
        future_pred, future_dates = predictor.predict_future()
        stock_info = predictor.get_stock_info()
        return predictor, future_pred, stock_info
    except Exception as e:
        print(f"❌ Future prediction failed: {e}")
        return predictor, None, None
>>>>>>> 77cdb08d702964fb06771c5fc7bb7db3a686186b
