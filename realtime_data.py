"""
Real-Time Data Feed for Stock Price Prediction
Includes: WebSocket-based and simulated real-time price feeds
"""

import asyncio
import websockets
import json
import time
import threading
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
from queue import Queue
import warnings
warnings.filterwarnings('ignore')

class RealTimeDataFeed:
    """Real-time data feed for stock prices"""
    
    def __init__(self, symbols=None, update_interval=1):
        """
        Initialize real-time data feed
        
        Args:
            symbols (list): List of stock symbols to monitor
            update_interval (int): Update interval in seconds
        """
        self.symbols = symbols or ['TCS.NS', 'RELIANCE.NS', 'HDFCBANK.NS']
        self.update_interval = update_interval
        self.data_queue = Queue()
        self.is_running = False
        self.latest_data = {}
        self.callbacks = []
        self.websocket = None
        
        # Initialize data structure
        for symbol in self.symbols:
            self.latest_data[symbol] = {
                'price': 0.0,
                'change': 0.0,
                'change_pct': 0.0,
                'volume': 0,
                'timestamp': None,
                'high': 0.0,
                'low': 0.0,
                'open': 0.0
            }
    
    def add_callback(self, callback):
        """Add callback function to be called when new data arrives"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback):
        """Remove callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self, symbol, data):
        """Notify all registered callbacks with new data"""
        for callback in self.callbacks:
            try:
                callback(symbol, data)
            except Exception as e:
                print(f"Error in callback: {e}")
    
    def start_simulated_feed(self):
        """Start simulated real-time data feed"""
        print("🔄 Starting simulated real-time data feed...")
        self.is_running = True
        
        def simulate_data():
            while self.is_running:
                for symbol in self.symbols:
                    try:
                        # Get current data from yfinance
                        stock = yf.Ticker(symbol)
                        hist = stock.history(period="2d")
                        
                        if len(hist) >= 2:
                            current_price = hist['Close'].iloc[-1]
                            prev_price = hist['Close'].iloc[-2]
                            change = current_price - prev_price
                            change_pct = (change / prev_price) * 100
                            
                            # Add some realistic noise to simulate real-time updates
                            noise = np.random.normal(0, current_price * 0.001)  # 0.1% noise
                            simulated_price = current_price + noise
                            
                            # Update latest data
                            self.latest_data[symbol].update({
                                'price': simulated_price,
                                'change': change,
                                'change_pct': change_pct,
                                'volume': hist['Volume'].iloc[-1],
                                'timestamp': datetime.now(),
                                'high': hist['High'].iloc[-1],
                                'low': hist['Low'].iloc[-1],
                                'open': hist['Open'].iloc[-1]
                            })
                            
                            # Put data in queue
                            self.data_queue.put({
                                'symbol': symbol,
                                'data': self.latest_data[symbol].copy()
                            })
                            
                            # Notify callbacks
                            self._notify_callbacks(symbol, self.latest_data[symbol])
                            
                    except Exception as e:
                        print(f"Error updating {symbol}: {e}")
                        continue
                
                time.sleep(self.update_interval)
        
        # Start simulation in separate thread
        self.simulation_thread = threading.Thread(target=simulate_data, daemon=True)
        self.simulation_thread.start()
        
        print(f"✅ Simulated feed started for {len(self.symbols)} symbols")
    
    def start_websocket_feed(self, websocket_url=None):
        """Start WebSocket-based real-time data feed"""
        if websocket_url is None:
            print("❌ WebSocket URL not provided. Using simulated feed instead.")
            self.start_simulated_feed()
            return
        
        print(f"🔄 Starting WebSocket feed: {websocket_url}")
        self.is_running = True
        
        async def websocket_handler():
            try:
                async with websockets.connect(websocket_url) as websocket:
                    self.websocket = websocket
                    print("✅ WebSocket connected")
                    
                    # Subscribe to symbols
                    subscribe_message = {
                        "action": "subscribe",
                        "symbols": self.symbols
                    }
                    await websocket.send(json.dumps(subscribe_message))
                    
                    # Listen for messages
                    while self.is_running:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                            data = json.loads(message)
                            
                            # Process incoming data
                            self._process_websocket_data(data)
                            
                        except asyncio.TimeoutError:
                            continue
                        except Exception as e:
                            print(f"Error processing WebSocket message: {e}")
                            continue
                            
            except Exception as e:
                print(f"WebSocket error: {e}")
                print("Falling back to simulated feed...")
                self.start_simulated_feed()
        
        # Start WebSocket in separate thread
        def run_websocket():
            asyncio.run(websocket_handler())
        
        self.websocket_thread = threading.Thread(target=run_websocket, daemon=True)
        self.websocket_thread.start()
    
    def _process_websocket_data(self, data):
        """Process incoming WebSocket data"""
        try:
            # Extract symbol and price data
            symbol = data.get('symbol')
            if symbol not in self.symbols:
                return
            
            # Update latest data
            self.latest_data[symbol].update({
                'price': float(data.get('price', 0)),
                'change': float(data.get('change', 0)),
                'change_pct': float(data.get('change_pct', 0)),
                'volume': int(data.get('volume', 0)),
                'timestamp': datetime.now(),
                'high': float(data.get('high', 0)),
                'low': float(data.get('low', 0)),
                'open': float(data.get('open', 0))
            })
            
            # Put data in queue
            self.data_queue.put({
                'symbol': symbol,
                'data': self.latest_data[symbol].copy()
            })
            
            # Notify callbacks
            self._notify_callbacks(symbol, self.latest_data[symbol])
            
        except Exception as e:
            print(f"Error processing WebSocket data: {e}")
    
    def get_latest_data(self, symbol=None):
        """Get latest data for symbol(s)"""
        if symbol is None:
            return self.latest_data
        return self.latest_data.get(symbol, {})
    
    def get_data_queue(self):
        """Get data from the queue"""
        if not self.data_queue.empty():
            return self.data_queue.get()
        return None
    
    def get_all_data(self):
        """Get all latest data as DataFrame"""
        data_list = []
        for symbol, data in self.latest_data.items():
            if data['timestamp'] is not None:
                data_copy = data.copy()
                data_copy['symbol'] = symbol
                data_list.append(data_copy)
        
        if data_list:
            df = pd.DataFrame(data_list)
            df = df.set_index('symbol')
            return df
        return pd.DataFrame()
    
    def stop_feed(self):
        """Stop the real-time data feed"""
        print("🛑 Stopping real-time data feed...")
        self.is_running = False
        
        # Close WebSocket if open
        if self.websocket:
            asyncio.create_task(self.websocket.close())
        
        print("✅ Real-time data feed stopped")
    
    def get_price_alerts(self, symbol, threshold_pct=5.0):
        """Get price alerts for significant changes"""
        if symbol not in self.latest_data:
            return None
        
        data = self.latest_data[symbol]
        change_pct = abs(data['change_pct'])
        
        if change_pct >= threshold_pct:
            alert_type = "PRICE_ALERT"
            if data['change_pct'] > 0:
                alert_type = "PRICE_SURGE"
            else:
                alert_type = "PRICE_DROP"
            
            return {
                'symbol': symbol,
                'alert_type': alert_type,
                'current_price': data['price'],
                'change_pct': data['change_pct'],
                'threshold': threshold_pct,
                'timestamp': data['timestamp']
            }
        
        return None
    
    def get_volume_alerts(self, symbol, volume_multiplier=2.0):
        """Get volume alerts for unusual trading activity"""
        if symbol not in self.latest_data:
            return None
        
        data = self.latest_data[symbol]
        current_volume = data['volume']
        
        # Get historical average volume (simplified)
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="5d")
            avg_volume = hist['Volume'].mean()
            
            if current_volume >= avg_volume * volume_multiplier:
                return {
                    'symbol': symbol,
                    'alert_type': 'HIGH_VOLUME',
                    'current_volume': current_volume,
                    'average_volume': avg_volume,
                    'multiplier': current_volume / avg_volume,
                    'timestamp': data['timestamp']
                }
        except:
            pass
        
        return None

class RealTimeAnalyzer:
    """Real-time analysis of streaming data"""
    
    def __init__(self, data_feed):
        """
        Initialize real-time analyzer
        
        Args:
            data_feed (RealTimeDataFeed): Real-time data feed instance
        """
        self.data_feed = data_feed
        self.price_history = {}
        self.analysis_results = {}
        self.alert_history = []
        
        # Initialize price history for each symbol
        for symbol in data_feed.symbols:
            self.price_history[symbol] = []
            self.analysis_results[symbol] = {}
        
        # Register callback for real-time analysis
        self.data_feed.add_callback(self._analyze_realtime)
    
    def _analyze_realtime(self, symbol, data):
        """Analyze incoming real-time data"""
        # Store price history
        self.price_history[symbol].append({
            'price': data['price'],
            'timestamp': data['timestamp'],
            'volume': data['volume']
        })
        
        # Keep only last 1000 data points
        if len(self.price_history[symbol]) > 1000:
            self.price_history[symbol] = self.price_history[symbol][-1000:]
        
        # Perform real-time analysis
        self._calculate_realtime_indicators(symbol)
        
        # Check for alerts
        self._check_alerts(symbol, data)
    
    def _calculate_realtime_indicators(self, symbol):
        """Calculate real-time technical indicators"""
        if len(self.price_history[symbol]) < 20:
            return
        
        prices = [p['price'] for p in self.price_history[symbol]]
        volumes = [p['volume'] for p in self.price_history[symbol]]
        
        # Simple moving averages
        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else sma_20
        
        # RSI (simplified)
        if len(prices) >= 14:
            changes = np.diff(prices[-14:])
            gains = np.where(changes > 0, changes, 0)
            losses = np.where(changes < 0, -changes, 0)
            
            avg_gain = np.mean(gains)
            avg_loss = np.mean(losses)
            
            if avg_loss != 0:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            else:
                rsi = 100
        else:
            rsi = 50
        
        # Volume analysis
        avg_volume = np.mean(volumes[-20:])
        current_volume = volumes[-1] if volumes else 0
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Store results
        self.analysis_results[symbol] = {
            'sma_20': sma_20,
            'sma_50': sma_50,
            'rsi': rsi,
            'volume_ratio': volume_ratio,
            'trend': 'bullish' if sma_20 > sma_50 else 'bearish',
            'last_updated': datetime.now()
        }
    
    def _check_alerts(self, symbol, data):
        """Check for various types of alerts"""
        # Price alerts
        price_alert = self.data_feed.get_price_alerts(symbol, threshold_pct=3.0)
        if price_alert:
            self.alert_history.append(price_alert)
        
        # Volume alerts
        volume_alert = self.data_feed.get_volume_alerts(symbol, volume_multiplier=2.0)
        if volume_alert:
            self.alert_history.append(volume_alert)
        
        # Technical alerts
        if symbol in self.analysis_results:
            analysis = self.analysis_results[symbol]
            
            # RSI alerts
            if analysis['rsi'] > 80:
                self.alert_history.append({
                    'symbol': symbol,
                    'alert_type': 'RSI_OVERBOUGHT',
                    'rsi': analysis['rsi'],
                    'timestamp': datetime.now()
                })
            elif analysis['rsi'] < 20:
                self.alert_history.append({
                    'symbol': symbol,
                    'alert_type': 'RSI_OVERSOLD',
                    'rsi': analysis['rsi'],
                    'timestamp': datetime.now()
                })
            
            # Moving average crossover alerts
            if len(self.price_history[symbol]) >= 50:
                prev_analysis = self.analysis_results.get(symbol, {})
                if 'sma_20' in prev_analysis:
                    prev_trend = prev_analysis.get('trend', 'neutral')
                    current_trend = analysis['trend']
                    
                    if prev_trend != current_trend:
                        self.alert_history.append({
                            'symbol': symbol,
                            'alert_type': 'TREND_CHANGE',
                            'previous_trend': prev_trend,
                            'current_trend': current_trend,
                            'timestamp': datetime.now()
                        })
    
    def get_analysis_summary(self, symbol=None):
        """Get analysis summary for symbol(s)"""
        if symbol is None:
            return self.analysis_results
        
        return self.analysis_results.get(symbol, {})
    
    def get_alerts(self, alert_type=None, limit=50):
        """Get alerts with optional filtering"""
        alerts = self.alert_history
        
        if alert_type:
            alerts = [a for a in alerts if a['alert_type'] == alert_type]
        
        # Return most recent alerts
        return sorted(alerts, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def get_price_chart_data(self, symbol, period='1h'):
        """Get price chart data for visualization"""
        if symbol not in self.price_history:
            return None
        
        history = self.price_history[symbol]
        
        if period == '1h':
            # Last hour of data
            cutoff_time = datetime.now() - timedelta(hours=1)
            filtered_data = [p for p in history if p['timestamp'] >= cutoff_time]
        elif period == '1d':
            # Last 24 hours
            cutoff_time = datetime.now() - timedelta(days=1)
            filtered_data = [p for p in history if p['timestamp'] >= cutoff_time]
        else:
            # All available data
            filtered_data = history
        
        if not filtered_data:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(filtered_data)
        df = df.set_index('timestamp')
        df = df.sort_index()
        
        return df
    
    def export_data(self, symbol, filename=None):
        """Export real-time data to CSV"""
        if symbol not in self.price_history:
            print(f"No data available for {symbol}")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"realtime_{symbol}_{timestamp}.csv"
        
        # Get all data
        df = pd.DataFrame(self.price_history[symbol])
        df = df.set_index('timestamp')
        
        # Export to CSV
        df.to_csv(filename)
        print(f"Data exported to {filename}")
        
        return filename

