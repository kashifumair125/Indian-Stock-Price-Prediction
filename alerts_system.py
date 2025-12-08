"""
Alerts and Notifications System
Monitors stocks and generates alerts based on conditions
"""
import yfinance as yf
from datetime import datetime
import pandas as pd

class AlertsSystem:
    def __init__(self):
        """Initialize alerts system"""
        self.alerts = []
        self.triggered_alerts = []

    def add_alert(self, symbol, alert_type, condition, value, message=""):
        """
        Add a new alert

        Args:
            symbol: Stock symbol
            alert_type: Type of alert (price, change_pct, volume, rsi, etc.)
            condition: Condition (above, below, crosses_above, crosses_below)
            value: Threshold value
            message: Custom message
        """
        alert = {
            'id': len(self.alerts) + 1,
            'symbol': symbol,
            'alert_type': alert_type,
            'condition': condition,
            'value': value,
            'message': message,
            'created_at': datetime.now(),
            'status': 'active',
            'triggered': False
        }

        self.alerts.append(alert)
        return alert

    def check_alerts(self):
        """
        Check all active alerts and trigger if conditions are met

        Returns:
            List of triggered alerts
        """
        newly_triggered = []

        for alert in self.alerts:
            if alert['status'] != 'active' or alert['triggered']:
                continue

            symbol = alert['symbol']
            alert_type = alert['alert_type']
            condition = alert['condition']
            value = alert['value']

            try:
                # Get current data
                ticker = yf.Ticker(symbol)

                if alert_type == 'price':
                    current_value = self._get_current_price(ticker)

                elif alert_type == 'change_pct':
                    current_value = self._get_change_pct(ticker)

                elif alert_type == 'volume':
                    current_value = self._get_current_volume(ticker)

                elif alert_type == 'rsi':
                    current_value = self._calculate_rsi(ticker)

                elif alert_type == 'ma_cross':
                    current_value = self._check_ma_crossover(ticker)

                else:
                    continue

                # Check condition
                triggered = False

                if condition == 'above' and current_value > value:
                    triggered = True
                elif condition == 'below' and current_value < value:
                    triggered = True
                elif condition == 'equals' and abs(current_value - value) < 0.01:
                    triggered = True

                if triggered:
                    alert['triggered'] = True
                    alert['triggered_at'] = datetime.now()
                    alert['triggered_value'] = current_value

                    notification = {
                        'alert_id': alert['id'],
                        'symbol': symbol,
                        'alert_type': alert_type,
                        'message': alert['message'] or f"{symbol} {alert_type} is {condition} {value}",
                        'current_value': current_value,
                        'timestamp': datetime.now()
                    }

                    newly_triggered.append(notification)
                    self.triggered_alerts.append(notification)

            except Exception as e:
                print(f"Error checking alert for {symbol}: {e}")
                continue

        return newly_triggered

    def _get_current_price(self, ticker):
        """Get current price"""
        try:
            info = getattr(ticker, 'fast_info', {}) or {}
            price = info.get('last_price') or info.get('lastPrice')
            if price is None:
                hist = ticker.history(period="1d", interval="1m")
                if not hist.empty:
                    price = float(hist['Close'].iloc[-1])
            return float(price) if price else 0
        except:
            return 0

    def _get_change_pct(self, ticker):
        """Get percentage change"""
        try:
            info = getattr(ticker, 'fast_info', {}) or {}
            price = info.get('last_price')
            prev_close = info.get('previous_close')

            if price and prev_close:
                change_pct = ((price - prev_close) / prev_close) * 100
                return change_pct
        except:
            pass
        return 0

    def _get_current_volume(self, ticker):
        """Get current volume"""
        try:
            hist = ticker.history(period="1d", interval="1m")
            if not hist.empty:
                return float(hist['Volume'].sum())
        except:
            pass
        return 0

    def _calculate_rsi(self, ticker, period=14):
        """Calculate RSI"""
        try:
            hist = ticker.history(period="1mo")
            if len(hist) < period + 1:
                return 50

            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            return float(rsi.iloc[-1])
        except:
            return 50

    def _check_ma_crossover(self, ticker):
        """Check for MA crossover"""
        try:
            hist = ticker.history(period="3mo")
            if len(hist) < 50:
                return 0

            hist['MA20'] = hist['Close'].rolling(window=20).mean()
            hist['MA50'] = hist['Close'].rolling(window=50).mean()

            # Check if MA20 crossed above MA50 recently
            if hist['MA20'].iloc[-1] > hist['MA50'].iloc[-1] and hist['MA20'].iloc[-2] <= hist['MA50'].iloc[-2]:
                return 1  # Golden cross
            elif hist['MA20'].iloc[-1] < hist['MA50'].iloc[-1] and hist['MA20'].iloc[-2] >= hist['MA50'].iloc[-2]:
                return -1  # Death cross
            else:
                return 0  # No cross
        except:
            return 0

    def get_active_alerts(self):
        """Get list of active alerts"""
        return [a for a in self.alerts if a['status'] == 'active' and not a['triggered']]

    def get_triggered_alerts(self):
        """Get list of triggered alerts"""
        return self.triggered_alerts

    def remove_alert(self, alert_id):
        """Remove an alert"""
        self.alerts = [a for a in self.alerts if a['id'] != alert_id]

    def get_alerts_dataframe(self):
        """Get alerts as DataFrame"""
        if not self.alerts:
            return pd.DataFrame()

        df = pd.DataFrame(self.alerts)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')

        return df[['id', 'symbol', 'alert_type', 'condition', 'value', 'status', 'triggered', 'created_at']]
