"""
Indian Stock Price Prediction - Professional Web Application (FIXED)
Author: Enhanced by Claude
Date: 2025

FIXES:
- ✅ Dark mode CSS properly applied
- ✅ Ticker rendering fixed
- ✅ Full AI analysis integrated
- ✅ All features working

Run with: streamlit run web_app_pro.py
"""
from advanced_indicators import AdvancedTechnicalIndicators
from ensemble_models import EnsembleModels
from realtime_data import RealTimeDataFeed, RealTimeAnalyzer
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import warnings
from datetime import datetime, timedelta
import time
import yfinance as yf
from config import CURRENCY_SYMBOLS, CURRENCY_SYMBOL, LIVE_REFRESH_SECONDS
import requests

# Suppress warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Indian Stock Price Prediction - Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add src to path
sys.path.append('src')

try:
    from stock_predictor import IndianStockPredictor
except ImportError as e:
    st.error(f"❌ **Import Error**: {e}")
    st.stop()

# Enhanced stock list with sectors
EXTENDED_INDIAN_STOCKS = {
    'TCS.NS': {'name': 'Tata Consultancy Services Limited', 'sector': 'IT'},
    'INFY.NS': {'name': 'Infosys Limited', 'sector': 'IT'},
    'WIPRO.NS': {'name': 'Wipro Limited', 'sector': 'IT'},
    'TECHM.NS': {'name': 'Tech Mahindra Limited', 'sector': 'IT'},
    'HCLTECH.NS': {'name': 'HCL Technologies Limited', 'sector': 'IT'},
    'HDFCBANK.NS': {'name': 'HDFC Bank Limited', 'sector': 'Banking'},
    'ICICIBANK.NS': {'name': 'ICICI Bank Limited', 'sector': 'Banking'},
    'SBIN.NS': {'name': 'State Bank of India', 'sector': 'Banking'},
    'KOTAKBANK.NS': {'name': 'Kotak Mahindra Bank Limited', 'sector': 'Banking'},
    'AXISBANK.NS': {'name': 'Axis Bank Limited', 'sector': 'Banking'},
    'BAJFINANCE.NS': {'name': 'Bajaj Finance Limited', 'sector': 'Finance'},
    'RELIANCE.NS': {'name': 'Reliance Industries Limited', 'sector': 'Energy'},
    'ONGC.NS': {'name': 'Oil and Natural Gas Corporation', 'sector': 'Energy'},
    'IOC.NS': {'name': 'Indian Oil Corporation', 'sector': 'Energy'},
    'HINDUNILVR.NS': {'name': 'Hindustan Unilever Limited', 'sector': 'FMCG'},
    'ITC.NS': {'name': 'ITC Limited', 'sector': 'FMCG'},
    'NESTLEIND.NS': {'name': 'Nestle India Limited', 'sector': 'FMCG'},
    'MARUTI.NS': {'name': 'Maruti Suzuki India Limited', 'sector': 'Auto'},
    'TATAMOTORS.NS': {'name': 'Tata Motors Limited', 'sector': 'Auto'},
    'M&M.NS': {'name': 'Mahindra & Mahindra Limited', 'sector': 'Auto'},
    'SUNPHARMA.NS': {'name': 'Sun Pharmaceutical Industries', 'sector': 'Pharma'},
    'DRREDDY.NS': {'name': 'Dr. Reddy\'s Laboratories', 'sector': 'Pharma'},
    'CIPLA.NS': {'name': 'Cipla Limited', 'sector': 'Pharma'},
    'TATASTEEL.NS': {'name': 'Tata Steel Limited', 'sector': 'Metals'},
    'JSWSTEEL.NS': {'name': 'JSW Steel Limited', 'sector': 'Metals'},
    'LT.NS': {'name': 'Larsen & Toubro Limited', 'sector': 'Infrastructure'},
    'ULTRACEMCO.NS': {'name': 'UltraTech Cement Limited', 'sector': 'Cement'},
    'TITAN.NS': {'name': 'Titan Company Limited', 'sector': 'Consumer'},
    'ASIANPAINT.NS': {'name': 'Asian Paints Limited', 'sector': 'Consumer'},
}

# Initialize session state
def init_session_state():
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = ['TCS.NS', 'RELIANCE.NS', 'HDFCBANK.NS']

init_session_state()

# Theme CSS - FIXED VERSION
def apply_theme_css():
    """Apply theme CSS properly"""
    theme = st.session_state.theme

    if theme == 'dark':
        bg = "#0E1117"
        text = "#FAFAFA"
        card = "#262730"
        border = "#404040"
    else:
        bg = "#FFFFFF"
        text = "#1E1E1E"
        card = "#F8F9FA"
        border = "#DEDEDE"

    css = f"""
    <style>
        .stApp {{
            background-color: {bg} !important;
            color: {text} !important;
        }}
        .element-container, .row-widget, .stMarkdown {{
            color: {text} !important;
        }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}

        /* Cards */
        .metric-card {{
            background: {card};
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid {border};
            color: {text};
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

apply_theme_css()

# Currency utilities
@st.cache_data(ttl=300)
def get_symbol_currency(symbol):
    try:
        ticker = yf.Ticker(symbol)
        try:
            currency = getattr(ticker, 'fast_info', {}).get('currency')
        except:
            currency = None
        if not currency:
            try:
                info = ticker.get_info() if hasattr(ticker, 'get_info') else {}
            except:
                info = {}
            currency = info.get('currency') or info.get('financialCurrency')
        return (currency or 'INR').upper()
    except:
        return 'INR'

def currency_symbol_for(symbol):
    code = get_symbol_currency(symbol)
    return CURRENCY_SYMBOLS.get(code, CURRENCY_SYMBOL)

def format_price(symbol, value):
    return f"{currency_symbol_for(symbol)}{value:.2f}"

@st.cache_data(ttl=LIVE_REFRESH_SECONDS)
def get_live_quote(symbol):
    data = {'price': None, 'prev_close': None, 'change_pct': None, 'ts': None, 'currency': get_symbol_currency(symbol)}
    try:
        t = yf.Ticker(symbol)
        fi = getattr(t, 'fast_info', {}) or {}
        price = fi.get('last_price') or fi.get('lastPrice') or fi.get('regular_market_price')
        prev_close = fi.get('previous_close') or fi.get('previousClose')

        if price is None:
            hist = t.history(period="1d", interval="1m")
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
                prev_close = prev_close or float(hist['Close'].iloc[-2]) if len(hist) > 1 else price
                data['ts'] = hist.index[-1].to_pydatetime()

        if data['ts'] is None:
            data['ts'] = datetime.now()

        data['price'] = float(price) if price is not None else None
        data['prev_close'] = float(prev_close) if prev_close is not None else None

        if data['price'] is not None and data['prev_close'] not in (None, 0):
            data['change_pct'] = ((data['price'] - data['prev_close']) / data['prev_close']) * 100
    except:
        pass
    return data

# ==================== TICKER - FIXED ====================
def render_ticker():
    """Render ticker using Streamlit native components"""
    st.markdown("### 📊 Live Market Ticker")

    cols = st.columns(min(len(st.session_state.watchlist), 5))

    for idx, symbol in enumerate(st.session_state.watchlist[:5]):
        quote = get_live_quote(symbol)
        with cols[idx]:
            if quote and quote.get('price'):
                name = EXTENDED_INDIAN_STOCKS.get(symbol, {}).get('name', symbol)[:10]
                price = quote['price']
                change = quote.get('change_pct', 0)

                delta = f"{change:+.2f}%"
                st.metric(
                    label=name,
                    value=format_price(symbol, price),
                    delta=delta
                )

# ==================== MARKET HEATMAP ====================
def render_market_heatmap():
    st.markdown("### 🔥 Market Heatmap by Sector")

    with st.spinner("Loading heatmap..."):
        sector_data = {}
        for symbol, info in EXTENDED_INDIAN_STOCKS.items():
            sector = info.get('sector', 'Other')
            if sector not in sector_data:
                sector_data[sector] = {'stocks': [], 'changes': []}

            quote = get_live_quote(symbol)
            if quote and quote.get('change_pct') is not None:
                sector_data[sector]['stocks'].append(symbol)
                sector_data[sector]['changes'].append(quote['change_pct'])

        heatmap_data = []
        for sector, data in sector_data.items():
            if data['changes']:
                heatmap_data.append({
                    'Sector': sector,
                    'Change %': np.mean(data['changes']),
                    'Stocks': len(data['stocks'])
                })

        if heatmap_data:
            df = pd.DataFrame(heatmap_data)
            fig = px.treemap(
                df,
                path=['Sector'],
                values='Stocks',
                color='Change %',
                color_continuous_scale=['red', 'yellow', 'green'],
                color_continuous_midpoint=0,
                title='Sector Performance'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

            df = df.sort_values('Change %', ascending=False)
            df['Change %'] = df['Change %'].apply(lambda x: f"{x:+.2f}%")
            st.dataframe(df, use_container_width=True, hide_index=True)

# ==================== DASHBOARD ====================
def render_dashboard():
    st.title("📊 Market Dashboard")

    render_ticker()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Stocks", len(EXTENDED_INDIAN_STOCKS))
    with col2:
        st.metric("Watchlist", len(st.session_state.watchlist))
    with col3:
        portfolio_value = sum([p.get('current_value', 0) for p in st.session_state.portfolio])
        st.metric("Portfolio Value", f"₹{portfolio_value:,.2f}")
    with col4:
        st.metric("Market Status", "🟢 Open" if datetime.now().hour < 15 else "🔴 Closed")

    render_market_heatmap()

    # Top gainers/losers
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Top Gainers")
        gainers = []
        for symbol in list(EXTENDED_INDIAN_STOCKS.keys())[:15]:
            quote = get_live_quote(symbol)
            if quote and quote.get('change_pct') and quote['change_pct'] > 0:
                gainers.append({
                    'Symbol': symbol,
                    'Name': EXTENDED_INDIAN_STOCKS[symbol]['name'][:25],
                    'Price': format_price(symbol, quote['price']),
                    'Change': f"+{quote['change_pct']:.2f}%"
                })

        gainers = sorted(gainers, key=lambda x: float(x['Change'].replace('+', '').replace('%', '')), reverse=True)[:5]
        if gainers:
            st.dataframe(pd.DataFrame(gainers), use_container_width=True, hide_index=True)

    with col2:
        st.markdown("### 📉 Top Losers")
        losers = []
        for symbol in list(EXTENDED_INDIAN_STOCKS.keys())[:15]:
            quote = get_live_quote(symbol)
            if quote and quote.get('change_pct') and quote['change_pct'] < 0:
                losers.append({
                    'Symbol': symbol,
                    'Name': EXTENDED_INDIAN_STOCKS[symbol]['name'][:25],
                    'Price': format_price(symbol, quote['price']),
                    'Change': f"{quote['change_pct']:.2f}%"
                })

        losers = sorted(losers, key=lambda x: float(x['Change'].replace('%', '')))[:5]
        if losers:
            st.dataframe(pd.DataFrame(losers), use_container_width=True, hide_index=True)

# ==================== STOCK SCREENER ====================
def render_stock_screener():
    st.title("🔍 Stock Screener")
    st.markdown("### Filter Stocks by Criteria")

    col1, col2, col3 = st.columns(3)
    with col1:
        sectors = ['All'] + sorted(list(set([info['sector'] for info in EXTENDED_INDIAN_STOCKS.values()])))
        selected_sector = st.selectbox("Sector", sectors)
    with col2:
        min_price = st.number_input("Min Price (₹)", min_value=0.0, value=0.0, step=10.0)
    with col3:
        max_price = st.number_input("Max Price (₹)", min_value=0.0, value=10000.0, step=100.0)

    col1, col2, col3 = st.columns(3)
    with col1:
        min_change = st.number_input("Min Change %", value=-100.0, step=1.0)
    with col2:
        max_change = st.number_input("Max Change %", value=100.0, step=1.0)
    with col3:
        sort_by = st.selectbox("Sort By", ["Change %", "Price", "Name"])

    if st.button("🔍 Apply Filters", type="primary"):
        with st.spinner("Screening stocks..."):
            results = []
            for symbol, info in EXTENDED_INDIAN_STOCKS.items():
                if selected_sector != 'All' and info['sector'] != selected_sector:
                    continue

                quote = get_live_quote(symbol)
                if not quote or quote.get('price') is None:
                    continue

                price = quote['price']
                change = quote.get('change_pct', 0)

                if price < min_price or price > max_price:
                    continue
                if change < min_change or change > max_change:
                    continue

                results.append({
                    'Symbol': symbol,
                    'Name': info['name'],
                    'Sector': info['sector'],
                    'Price': price,
                    'Change %': change,
                    'Price (Formatted)': format_price(symbol, price)
                })

            if results:
                df = pd.DataFrame(results)
                if sort_by == "Change %":
                    df = df.sort_values('Change %', ascending=False)
                elif sort_by == "Price":
                    df = df.sort_values('Price', ascending=False)
                else:
                    df = df.sort_values('Name')

                st.success(f"Found {len(df)} stocks")
                display_df = df[['Symbol', 'Name', 'Sector', 'Price (Formatted)', 'Change %']].copy()
                display_df['Change %'] = display_df['Change %'].apply(lambda x: f"{x:+.2f}%")
                display_df.columns = ['Symbol', 'Name', 'Sector', 'Price', 'Change %']
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.warning("No stocks found matching criteria")

# ==================== PORTFOLIO TRACKER ====================
def render_portfolio_tracker():
    st.title("💼 Portfolio Tracker")

    with st.expander("➕ Add New Position"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            p_symbol = st.selectbox("Stock", list(EXTENDED_INDIAN_STOCKS.keys()))
        with col2:
            p_quantity = st.number_input("Quantity", min_value=1, value=10)
        with col3:
            p_buy_price = st.number_input("Buy Price (₹)", min_value=0.01, value=100.0)
        with col4:
            p_buy_date = st.date_input("Buy Date", value=datetime.now())

        if st.button("➕ Add to Portfolio", type="primary"):
            position = {
                'symbol': p_symbol,
                'name': EXTENDED_INDIAN_STOCKS[p_symbol]['name'],
                'quantity': p_quantity,
                'buy_price': p_buy_price,
                'buy_date': p_buy_date.strftime('%Y-%m-%d'),
                'buy_value': p_quantity * p_buy_price
            }
            st.session_state.portfolio.append(position)
            st.success(f"Added {p_quantity} shares of {p_symbol}")
            st.rerun()

    if st.session_state.portfolio:
        st.markdown("### 📊 Your Portfolio")

        portfolio_data = []
        total_invested = 0
        total_current = 0

        for position in st.session_state.portfolio:
            quote = get_live_quote(position['symbol'])
            current_price = quote.get('price', position['buy_price'])
            current_value = position['quantity'] * current_price
            profit_loss = current_value - position['buy_value']
            profit_loss_pct = (profit_loss / position['buy_value']) * 100

            total_invested += position['buy_value']
            total_current += current_value

            portfolio_data.append({
                'Symbol': position['symbol'],
                'Name': position['name'][:20],
                'Quantity': position['quantity'],
                'Buy Price': f"₹{position['buy_price']:.2f}",
                'Current Price': format_price(position['symbol'], current_price),
                'P&L': f"₹{profit_loss:,.2f}",
                'P&L %': f"{profit_loss_pct:+.2f}%",
                '_pl_value': profit_loss
            })

        total_pl = total_current - total_invested
        total_pl_pct = (total_pl / total_invested * 100) if total_invested > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Invested", f"₹{total_invested:,.2f}")
        with col2:
            st.metric("Current Value", f"₹{total_current:,.2f}")
        with col3:
            st.metric("Total P&L", f"₹{total_pl:,.2f}", f"{total_pl_pct:+.2f}%")
        with col4:
            st.metric("Positions", len(st.session_state.portfolio))

        df = pd.DataFrame(portfolio_data)
        display_df = df.drop(columns=['_pl_value'])
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        if st.button("🗑️ Clear Portfolio"):
            st.session_state.portfolio = []
            st.rerun()
    else:
        st.info("Portfolio is empty. Add positions above!")

# ==================== ADVANCED CHARTING ====================
def render_advanced_charting():
    st.title("📈 Advanced Charting")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        selected_stock = st.selectbox("Select Stock", list(EXTENDED_INDIAN_STOCKS.keys()))
    with col2:
        timeframe = st.selectbox("Timeframe", ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y'], index=3)
    with col3:
        interval = st.selectbox("Interval", ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'], index=5)

    with st.spinner(f"Loading {selected_stock} data..."):
        try:
            ticker = yf.Ticker(selected_stock)
            df = ticker.history(period=timeframe, interval=interval)

            if df.empty:
                st.error("No data available")
                return

            col1, col2, col3 = st.columns(3)
            with col1:
                chart_type = st.selectbox("Chart Type", ['Candlestick', 'Line', 'Area'])
            with col2:
                show_volume = st.checkbox("Show Volume", value=True)
            with col3:
                show_ma = st.checkbox("Show Moving Averages", value=True)

            if show_ma:
                df['MA20'] = df['Close'].rolling(window=20).mean()
                df['MA50'] = df['Close'].rolling(window=50).mean()

            # Create chart
            fig = make_subplots(rows=2 if show_volume else 1, cols=1, shared_xaxes=True,
                               vertical_spacing=0.03, row_heights=[0.7, 0.3] if show_volume else [1.0])

            if chart_type == 'Candlestick':
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                                            low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
            elif chart_type == 'Line':
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines',
                                        name='Close', line=dict(color='#1f77b4', width=2)), row=1, col=1)
            else:
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'], fill='tozeroy',
                                        name='Close', line=dict(color='#1f77b4', width=2)), row=1, col=1)

            if show_ma:
                fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], mode='lines',
                                        name='MA20', line=dict(color='orange', width=1)), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], mode='lines',
                                        name='MA50', line=dict(color='green', width=1)), row=1, col=1)

            if show_volume:
                colors = ['green' if df['Close'].iloc[i] >= df['Open'].iloc[i] else 'red'
                         for i in range(len(df))]
                fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume',
                                    marker_color=colors), row=2, col=1)

            fig.update_layout(title=f'{selected_stock} - {EXTENDED_INDIAN_STOCKS[selected_stock]["name"]}',
                            xaxis_rangeslider_visible=False, height=600, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

            # Stats
            st.markdown("### 📊 Current Statistics")
            col1, col2, col3, col4 = st.columns(4)
            current_price = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2] if len(df) > 1 else current_price
            change_pct = ((current_price - prev_close) / prev_close) * 100

            with col1:
                st.metric("Current Price", format_price(selected_stock, current_price), f"{change_pct:+.2f}%")
            with col2:
                st.metric("High", format_price(selected_stock, df['High'].max()))
            with col3:
                st.metric("Low", format_price(selected_stock, df['Low'].min()))
            with col4:
                st.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")

        except Exception as e:
            st.error(f"Error loading chart: {str(e)}")

# ==================== AI ANALYSIS - FULLY INTEGRATED ====================
def render_ai_analysis():
    st.title("🤖 AI Stock Analysis")

    with st.sidebar:
        st.markdown("### 📊 Analysis Settings")

        selected_stock = st.selectbox(
            "Select Stock",
            options=list(EXTENDED_INDIAN_STOCKS.keys()),
            format_func=lambda x: f"{x} - {EXTENDED_INDIAN_STOCKS[x]['name'][:20]}"
        )

        period = st.selectbox("Time Period", ['3mo', '6mo', '1y', '2y', '5y'], index=2)

        st.markdown("### 🤖 Select AI Models")
        use_linear = st.checkbox("📊 Linear Regression", value=True)
        use_lstm = st.checkbox("🧠 LSTM Neural Network", value=True)
        use_prophet = st.checkbox("📈 Prophet Time Series", value=True)

        with st.expander("⚙️ Advanced Settings"):
            prediction_days = st.slider("Prediction Days", 7, 90, 30)
            lstm_epochs = st.slider("LSTM Training Epochs", 10, 100, 50) if use_lstm else 50
            risk_tolerance = st.select_slider("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"], value="Moderate")

        start_analysis = st.button("🚀 Start Analysis", type="primary")

    if start_analysis:
        if not any([use_linear, use_lstm, use_prophet]):
            st.error("Please select at least one AI model")
            return

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white;
                    padding: 20px; border-radius: 10px; text-align: center;">
            <h2>🔍 Analyzing {selected_stock}</h2>
            <p>Running AI analysis with {sum([use_linear, use_lstm, use_prophet])} models</p>
        </div>
        """, unsafe_allow_html=True)

        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Initialize
            status_text.info("🚀 Initializing AI system...")
            progress_bar.progress(10)
            predictor = IndianStockPredictor(symbol=selected_stock, period=period)

            # Fetch data
            status_text.info("📡 Fetching market data...")
            progress_bar.progress(20)
            data = predictor.fetch_data()
            if data is None:
                st.error("Failed to fetch data")
                return

            # Prepare data
            status_text.info("🔧 Engineering features...")
            progress_bar.progress(30)
            predictor.prepare_data()

            # Display stock info
            st.markdown("### 📊 Stock Overview")
            col1, col2, col3, col4 = st.columns(4)
            current_price = data['Close'].iloc[-1]

            with col1:
                st.metric("Current Price", format_price(selected_stock, current_price))
            with col2:
                st.metric("52W High", format_price(selected_stock, data['High'].max()))
            with col3:
                st.metric("52W Low", format_price(selected_stock, data['Low'].min()))
            with col4:
                volatility = data['Close'].pct_change().std() * np.sqrt(252) * 100
                st.metric("Volatility", f"{volatility:.1f}%")

            # Train models
            results = {}
            current_progress = 40

            if use_linear:
                status_text.info("🤖 Training Linear Regression...")
                progress_bar.progress(current_progress)
                predictor.train_linear_regression()
                current_progress += 20

            if use_lstm:
                status_text.info("🧠 Training LSTM...")
                progress_bar.progress(current_progress)
                predictor.train_lstm(epochs=lstm_epochs)
                current_progress += 20

            if use_prophet:
                status_text.info("📈 Training Prophet...")
                progress_bar.progress(current_progress)
                predictor.train_prophet()
                current_progress += 20

            # Evaluate
            status_text.info("📊 Evaluating models...")
            progress_bar.progress(90)
            results = predictor.evaluate_models()

            # Predict
            future_pred, future_dates = predictor.predict_future(days=prediction_days)

            progress_bar.progress(100)
            status_text.success("✅ Analysis Complete!")
            time.sleep(1)
            status_text.empty()
            progress_bar.empty()

            # Display results
            st.markdown("### 🏆 Model Performance")
            if results:
                cols = st.columns(len(results))
                for idx, (model_name, metrics) in enumerate(results.items()):
                    with cols[idx]:
                        st.markdown(f"""
                        <div style="background: #262730; padding: 15px; border-radius: 10px; border: 2px solid #667eea;">
                            <h4 style="color: #667eea;">{model_name.upper()}</h4>
                            <p><strong>RMSE:</strong> ₹{metrics['RMSE']:.2f}</p>
                            <p><strong>R²:</strong> {metrics['R²']:.4f}</p>
                            <p><strong>MAPE:</strong> {metrics['MAPE']:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)

            # Future predictions
            st.markdown("### 🔮 Future Predictions")
            if future_pred:
                fig = go.Figure()
                colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
                for idx, (model_name, predictions) in enumerate(future_pred.items()):
                    fig.add_trace(go.Scatter(
                        x=future_dates, y=predictions, mode='lines+markers',
                        name=model_name, line=dict(width=3, color=colors[idx % len(colors)])
                    ))

                fig.add_hline(y=current_price, line_dash="dot", line_color="gray",
                            annotation_text=f"Current: ₹{current_price:.2f}")

                fig.update_layout(
                    title=f'{prediction_days}-Day Price Forecast',
                    xaxis_title='Date',
                    yaxis_title='Price (₹)',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)

                # Prediction summary
                st.markdown("### 📊 Prediction Summary")
                avg_predictions = []
                for i in range(len(list(future_pred.values())[0])):
                    day_preds = [model_preds[i] for model_preds in future_pred.values()]
                    avg_predictions.append(np.mean(day_preds))

                pred_summary = []
                for day in [1, 7, 15, 30]:
                    if day <= len(avg_predictions):
                        pred_price = avg_predictions[day-1]
                        change = ((pred_price - current_price) / current_price) * 100
                        pred_summary.append({
                            'Period': f'{day} Day{"s" if day > 1 else ""}',
                            'Predicted Price': f'₹{pred_price:.2f}',
                            'Change': f'{change:+.1f}%',
                            'Direction': '📈' if change > 0 else '📉' if change < 0 else '➡️'
                        })

                if pred_summary:
                    st.dataframe(pd.DataFrame(pred_summary), use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            st.exception(e)
    else:
        st.info("👈 Configure analysis settings in the sidebar and click 'Start Analysis'")

# ==================== MAIN APP ====================
def main():
    # Theme toggle
    col1, col2 = st.columns([9, 1])
    with col2:
        theme_icon = "☀️" if st.session_state.theme == 'dark' else "🌙"
        if st.button(theme_icon, key="theme_toggle"):
            st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            st.rerun()

    # Navigation
    st.sidebar.title("🎯 Navigation")
    pages = {
        "📊 Dashboard": render_dashboard,
        "📈 Advanced Charts": render_advanced_charting,
        "🤖 AI Analysis": render_ai_analysis,
        "🔍 Stock Screener": render_stock_screener,
        "💼 Portfolio": render_portfolio_tracker
    }

    page = st.sidebar.radio("Select Page", list(pages.keys()))

    # Watchlist
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⭐ Watchlist")
    with st.sidebar.expander("Manage Watchlist"):
        new_stock = st.selectbox("Add Stock",
                                [s for s in EXTENDED_INDIAN_STOCKS.keys()
                                 if s not in st.session_state.watchlist])
        if st.button("➕ Add"):
            st.session_state.watchlist.append(new_stock)
            st.rerun()

        for stock in st.session_state.watchlist[:5]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(stock)
            with col2:
                if st.button("🗑️", key=f"rm_{stock}"):
                    st.session_state.watchlist.remove(stock)
                    st.rerun()

    # Render selected page
    pages[page]()

if __name__ == "__main__":
    main()
