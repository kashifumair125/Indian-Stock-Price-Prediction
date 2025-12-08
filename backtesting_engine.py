"""
Backtesting Engine for Trading Strategies
Allows testing trading strategies on historical data
"""
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class BacktestingEngine:
    def __init__(self, symbol, start_date, end_date, initial_capital=100000):
        """
        Initialize backtesting engine

        Args:
            symbol: Stock symbol
            start_date: Start date for backtest
            end_date: End date for backtest
            initial_capital: Starting capital in rupees
        """
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.data = None
        self.trades = []
        self.positions = []
        self.equity_curve = []

    def load_data(self):
        """Load historical data"""
        ticker = yf.Ticker(self.symbol)
        self.data = ticker.history(start=self.start_date, end=self.end_date)

        if self.data.empty:
            raise ValueError("No data available for the specified period")

        # Calculate technical indicators
        self.data['MA20'] = self.data['Close'].rolling(window=20).mean()
        self.data['MA50'] = self.data['Close'].rolling(window=50).mean()
        self.data['RSI'] = self._calculate_rsi(self.data['Close'], 14)

        # MACD
        exp1 = self.data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = self.data['Close'].ewm(span=26, adjust=False).mean()
        self.data['MACD'] = exp1 - exp2
        self.data['MACD_signal'] = self.data['MACD'].ewm(span=9, adjust=False).mean()

        # Bollinger Bands
        self.data['BB_middle'] = self.data['Close'].rolling(window=20).mean()
        bb_std = self.data['Close'].rolling(window=20).std()
        self.data['BB_upper'] = self.data['BB_middle'] + (bb_std * 2)
        self.data['BB_lower'] = self.data['BB_middle'] - (bb_std * 2)

        return self.data

    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def run_strategy(self, strategy_name='MA_CROSSOVER', **params):
        """
        Run a trading strategy

        Strategies:
        - MA_CROSSOVER: Moving average crossover
        - RSI_OVERSOLD: Buy when RSI < 30, sell when RSI > 70
        - MACD_CROSSOVER: MACD crosses signal line
        - BOLLINGER_BANDS: Buy at lower band, sell at upper band
        """
        if self.data is None:
            self.load_data()

        # Reset
        self.trades = []
        position = 0  # 0 = no position, 1 = long
        entry_price = 0
        shares = 0
        capital = self.initial_capital
        equity = capital

        for i in range(1, len(self.data)):
            date = self.data.index[i]
            price = self.data['Close'].iloc[i]

            # Strategy logic
            buy_signal = False
            sell_signal = False

            if strategy_name == 'MA_CROSSOVER':
                short_ma = params.get('short_ma', 20)
                long_ma = params.get('long_ma', 50)

                prev_short = self.data['MA20'].iloc[i-1] if short_ma == 20 else self.data['MA50'].iloc[i-1]
                curr_short = self.data['MA20'].iloc[i] if short_ma == 20 else self.data['MA50'].iloc[i]
                prev_long = self.data['MA50'].iloc[i-1]
                curr_long = self.data['MA50'].iloc[i]

                # Golden cross
                if prev_short <= prev_long and curr_short > curr_long and position == 0:
                    buy_signal = True
                # Death cross
                elif prev_short >= prev_long and curr_short < curr_long and position == 1:
                    sell_signal = True

            elif strategy_name == 'RSI_OVERSOLD':
                rsi = self.data['RSI'].iloc[i]
                oversold = params.get('oversold', 30)
                overbought = params.get('overbought', 70)

                if rsi < oversold and position == 0:
                    buy_signal = True
                elif rsi > overbought and position == 1:
                    sell_signal = True

            elif strategy_name == 'MACD_CROSSOVER':
                prev_macd = self.data['MACD'].iloc[i-1]
                curr_macd = self.data['MACD'].iloc[i]
                prev_signal = self.data['MACD_signal'].iloc[i-1]
                curr_signal = self.data['MACD_signal'].iloc[i]

                # Bullish crossover
                if prev_macd <= prev_signal and curr_macd > curr_signal and position == 0:
                    buy_signal = True
                # Bearish crossover
                elif prev_macd >= prev_signal and curr_macd < curr_signal and position == 1:
                    sell_signal = True

            elif strategy_name == 'BOLLINGER_BANDS':
                if price <= self.data['BB_lower'].iloc[i] and position == 0:
                    buy_signal = True
                elif price >= self.data['BB_upper'].iloc[i] and position == 1:
                    sell_signal = True

            # Execute trades
            if buy_signal and capital > 0:
                shares = int(capital / price)
                if shares > 0:
                    entry_price = price
                    cost = shares * price
                    capital -= cost
                    position = 1

                    self.trades.append({
                        'date': date,
                        'type': 'BUY',
                        'price': price,
                        'shares': shares,
                        'value': cost,
                        'capital': capital
                    })

            elif sell_signal and position == 1:
                proceeds = shares * price
                profit = proceeds - (shares * entry_price)
                profit_pct = (profit / (shares * entry_price)) * 100
                capital += proceeds

                self.trades.append({
                    'date': date,
                    'type': 'SELL',
                    'price': price,
                    'shares': shares,
                    'value': proceeds,
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'capital': capital
                })

                position = 0
                shares = 0

            # Calculate equity
            if position == 1:
                equity = capital + (shares * price)
            else:
                equity = capital

            self.equity_curve.append({
                'date': date,
                'equity': equity,
                'position': position
            })

        # Close any open positions at the end
        if position == 1:
            final_price = self.data['Close'].iloc[-1]
            proceeds = shares * final_price
            profit = proceeds - (shares * entry_price)
            profit_pct = (profit / (shares * entry_price)) * 100
            capital += proceeds

            self.trades.append({
                'date': self.data.index[-1],
                'type': 'SELL',
                'price': final_price,
                'shares': shares,
                'value': proceeds,
                'profit': profit,
                'profit_pct': profit_pct,
                'capital': capital
            })

        return self.trades, self.equity_curve

    def calculate_metrics(self):
        """Calculate performance metrics"""
        if not self.equity_curve:
            return {}

        equity_df = pd.DataFrame(self.equity_curve)
        final_equity = equity_df['equity'].iloc[-1]

        # Returns
        total_return = ((final_equity - self.initial_capital) / self.initial_capital) * 100

        # Trade statistics
        trades_df = pd.DataFrame(self.trades)
        profitable_trades = len(trades_df[(trades_df['type'] == 'SELL') & (trades_df.get('profit', 0) > 0)])
        total_trades = len(trades_df[trades_df['type'] == 'SELL'])
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0

        # Average profit per trade
        sell_trades = trades_df[trades_df['type'] == 'SELL']
        avg_profit = sell_trades['profit'].mean() if len(sell_trades) > 0 else 0
        avg_profit_pct = sell_trades['profit_pct'].mean() if len(sell_trades) > 0 else 0

        # Max drawdown
        equity_series = equity_df['equity']
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max * 100
        max_drawdown = drawdown.min()

        # Sharpe ratio (simplified)
        daily_returns = equity_series.pct_change().dropna()
        if len(daily_returns) > 0 and daily_returns.std() != 0:
            sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0

        # Buy and hold comparison
        buy_hold_return = ((self.data['Close'].iloc[-1] - self.data['Close'].iloc[0]) /
                          self.data['Close'].iloc[0]) * 100

        metrics = {
            'Initial Capital': self.initial_capital,
            'Final Equity': final_equity,
            'Total Return': total_return,
            'Total Return %': total_return,
            'Total Trades': total_trades,
            'Profitable Trades': profitable_trades,
            'Win Rate %': win_rate,
            'Average Profit': avg_profit,
            'Average Profit %': avg_profit_pct,
            'Max Drawdown %': max_drawdown,
            'Sharpe Ratio': sharpe_ratio,
            'Buy & Hold Return %': buy_hold_return,
            'Alpha': total_return - buy_hold_return
        }

        return metrics

    def plot_results(self):
        """Plot backtest results"""
        if not self.equity_curve:
            return None

        equity_df = pd.DataFrame(self.equity_curve)
        trades_df = pd.DataFrame(self.trades)

        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Price & Trades', 'Equity Curve'),
            row_heights=[0.6, 0.4]
        )

        # Price chart
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=self.data['Close'],
            mode='lines',
            name='Price',
            line=dict(color='#1f77b4', width=2)
        ), row=1, col=1)

        # Buy signals
        buy_trades = trades_df[trades_df['type'] == 'BUY']
        if len(buy_trades) > 0:
            fig.add_trace(go.Scatter(
                x=buy_trades['date'],
                y=buy_trades['price'],
                mode='markers',
                name='Buy',
                marker=dict(symbol='triangle-up', size=15, color='green')
            ), row=1, col=1)

        # Sell signals
        sell_trades = trades_df[trades_df['type'] == 'SELL']
        if len(sell_trades) > 0:
            fig.add_trace(go.Scatter(
                x=sell_trades['date'],
                y=sell_trades['price'],
                mode='markers',
                name='Sell',
                marker=dict(symbol='triangle-down', size=15, color='red')
            ), row=1, col=1)

        # Equity curve
        fig.add_trace(go.Scatter(
            x=equity_df['date'],
            y=equity_df['equity'],
            mode='lines',
            name='Equity',
            line=dict(color='#2ca02c', width=2),
            fill='tozeroy',
            fillcolor='rgba(44, 160, 44, 0.1)'
        ), row=2, col=1)

        # Initial capital line
        fig.add_hline(
            y=self.initial_capital,
            line_dash="dash",
            line_color="gray",
            opacity=0.5,
            row=2, col=1
        )

        fig.update_layout(
            title='Backtest Results',
            xaxis_title='Date',
            yaxis_title='Price (₹)',
            yaxis2_title='Equity (₹)',
            height=800,
            showlegend=True,
            hovermode='x unified'
        )

        return fig

    def get_trade_list(self):
        """Get list of trades as DataFrame"""
        if not self.trades:
            return pd.DataFrame()

        trades_df = pd.DataFrame(self.trades)
        trades_df['date'] = pd.to_datetime(trades_df['date']).dt.date
        return trades_df
