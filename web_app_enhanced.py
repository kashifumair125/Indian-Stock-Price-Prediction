"""
Indian Stock Price Prediction - Enhanced Professional Web Application
Author: Enhanced by Claude
Date: 2025

A professional-grade Streamlit web interface with advanced features:
- Dark/Light mode
- Real-time ticker
- Market heatmap
- Advanced charting
- Stock screener
- Portfolio tracker

Run with: streamlit run web_app_enhanced.py
"""
from advanced_indicators import AdvancedTechnicalIndicators
from ensemble_models import EnsembleModels
from realtime_data import RealTimeDataFeed, RealTimeAnalyzer
import streamlit as st
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
import json

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
    # Large Cap IT
    'TCS.NS': {'name': 'Tata Consultancy Services Limited', 'sector': 'IT'},
    'INFY.NS': {'name': 'Infosys Limited', 'sector': 'IT'},
    'WIPRO.NS': {'name': 'Wipro Limited', 'sector': 'IT'},
    'TECHM.NS': {'name': 'Tech Mahindra Limited', 'sector': 'IT'},
    'HCLTECH.NS': {'name': 'HCL Technologies Limited', 'sector': 'IT'},
    'LTI.NS': {'name': 'L&T Infotech Limited', 'sector': 'IT'},

    # Banking & Finance
    'HDFCBANK.NS': {'name': 'HDFC Bank Limited', 'sector': 'Banking'},
    'ICICIBANK.NS': {'name': 'ICICI Bank Limited', 'sector': 'Banking'},
    'SBIN.NS': {'name': 'State Bank of India', 'sector': 'Banking'},
    'KOTAKBANK.NS': {'name': 'Kotak Mahindra Bank Limited', 'sector': 'Banking'},
    'AXISBANK.NS': {'name': 'Axis Bank Limited', 'sector': 'Banking'},
    'INDUSINDBK.NS': {'name': 'IndusInd Bank Limited', 'sector': 'Banking'},
    'BAJFINANCE.NS': {'name': 'Bajaj Finance Limited', 'sector': 'Finance'},
    'BAJAJFINSV.NS': {'name': 'Bajaj Finserv Limited', 'sector': 'Finance'},
    'HDFCLIFE.NS': {'name': 'HDFC Life Insurance', 'sector': 'Finance'},
    'SBILIFE.NS': {'name': 'SBI Life Insurance', 'sector': 'Finance'},

    # Energy & Oil
    'RELIANCE.NS': {'name': 'Reliance Industries Limited', 'sector': 'Energy'},
    'ONGC.NS': {'name': 'Oil and Natural Gas Corporation', 'sector': 'Energy'},
    'IOC.NS': {'name': 'Indian Oil Corporation', 'sector': 'Energy'},
    'BPCL.NS': {'name': 'Bharat Petroleum Corporation', 'sector': 'Energy'},
    'HINDPETRO.NS': {'name': 'Hindustan Petroleum Corporation', 'sector': 'Energy'},
    'ADANIPORTS.NS': {'name': 'Adani Ports and SEZ Limited', 'sector': 'Infrastructure'},
    'ADANIGREEN.NS': {'name': 'Adani Green Energy Limited', 'sector': 'Energy'},

    # FMCG & Consumer
    'HINDUNILVR.NS': {'name': 'Hindustan Unilever Limited', 'sector': 'FMCG'},
    'ITC.NS': {'name': 'ITC Limited', 'sector': 'FMCG'},
    'NESTLEIND.NS': {'name': 'Nestle India Limited', 'sector': 'FMCG'},
    'BRITANNIA.NS': {'name': 'Britannia Industries Limited', 'sector': 'FMCG'},
    'DABUR.NS': {'name': 'Dabur India Limited', 'sector': 'FMCG'},
    'GODREJCP.NS': {'name': 'Godrej Consumer Products', 'sector': 'FMCG'},
    'MARICO.NS': {'name': 'Marico Limited', 'sector': 'FMCG'},
    'COLPAL.NS': {'name': 'Colgate-Palmolive India', 'sector': 'FMCG'},

    # Automobiles
    'MARUTI.NS': {'name': 'Maruti Suzuki India Limited', 'sector': 'Auto'},
    'TATAMOTORS.NS': {'name': 'Tata Motors Limited', 'sector': 'Auto'},
    'M&M.NS': {'name': 'Mahindra & Mahindra Limited', 'sector': 'Auto'},
    'BAJAJ-AUTO.NS': {'name': 'Bajaj Auto Limited', 'sector': 'Auto'},
    'HEROMOTOCO.NS': {'name': 'Hero MotoCorp Limited', 'sector': 'Auto'},
    'EICHERMOT.NS': {'name': 'Eicher Motors Limited', 'sector': 'Auto'},
    'ASHOKLEY.NS': {'name': 'Ashok Leyland Limited', 'sector': 'Auto'},

    # Pharmaceuticals
    'SUNPHARMA.NS': {'name': 'Sun Pharmaceutical Industries', 'sector': 'Pharma'},
    'DRREDDY.NS': {'name': 'Dr. Reddy\'s Laboratories', 'sector': 'Pharma'},
    'CIPLA.NS': {'name': 'Cipla Limited', 'sector': 'Pharma'},
    'BIOCON.NS': {'name': 'Biocon Limited', 'sector': 'Pharma'},
    'AUROPHARMA.NS': {'name': 'Aurobindo Pharma Limited', 'sector': 'Pharma'},
    'LUPIN.NS': {'name': 'Lupin Limited', 'sector': 'Pharma'},
    'DIVISLAB.NS': {'name': 'Divi\'s Laboratories Limited', 'sector': 'Pharma'},

    # Telecom
    'BHARTIARTL.NS': {'name': 'Bharti Airtel Limited', 'sector': 'Telecom'},
    'IDEA.NS': {'name': 'Vodafone Idea Limited', 'sector': 'Telecom'},

    # Metals & Mining
    'TATASTEEL.NS': {'name': 'Tata Steel Limited', 'sector': 'Metals'},
    'JSWSTEEL.NS': {'name': 'JSW Steel Limited', 'sector': 'Metals'},
    'HINDALCO.NS': {'name': 'Hindalco Industries Limited', 'sector': 'Metals'},
    'COALINDIA.NS': {'name': 'Coal India Limited', 'sector': 'Mining'},
    'VEDL.NS': {'name': 'Vedanta Limited', 'sector': 'Mining'},
    'NMDC.NS': {'name': 'NMDC Limited', 'sector': 'Mining'},

    # Construction & Infrastructure
    'LT.NS': {'name': 'Larsen & Toubro Limited', 'sector': 'Infrastructure'},
    'ULTRACEMCO.NS': {'name': 'UltraTech Cement Limited', 'sector': 'Cement'},
    'SHREECEM.NS': {'name': 'Shree Cement Limited', 'sector': 'Cement'},
    'ACC.NS': {'name': 'ACC Limited', 'sector': 'Cement'},
    'GRASIM.NS': {'name': 'Grasim Industries Limited', 'sector': 'Cement'},

    # Power & Utilities
    'POWERGRID.NS': {'name': 'Power Grid Corporation', 'sector': 'Power'},
    'NTPC.NS': {'name': 'NTPC Limited', 'sector': 'Power'},
    'TATAPOWER.NS': {'name': 'Tata Power Company', 'sector': 'Power'},

    # Consumer Durables
    'TITAN.NS': {'name': 'Titan Company Limited', 'sector': 'Consumer'},
    'ASIANPAINT.NS': {'name': 'Asian Paints Limited', 'sector': 'Consumer'},
    'PIDILITIND.NS': {'name': 'Pidilite Industries Limited', 'sector': 'Consumer'},
    'VOLTAS.NS': {'name': 'Voltas Limited', 'sector': 'Consumer'},
    'HAVELLS.NS': {'name': 'Havells India Limited', 'sector': 'Consumer'},
}

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []
    if 'page' not in st.session_state:
        st.session_state.page = 'Dashboard'
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = ['TCS.NS', 'RELIANCE.NS', 'HDFCBANK.NS']

init_session_state()

# Theme CSS
def get_theme_css():
    """Get CSS based on current theme"""
    if st.session_state.theme == 'dark':
        bg_color = "#0E1117"
        text_color = "#FAFAFA"
        card_bg = "#1E1E1E"
        border_color = "#333"
        gradient1 = "#667eea"
        gradient2 = "#764ba2"
    else:
        bg_color = "#FFFFFF"
        text_color = "#1E1E1E"
        card_bg = "#F8F9FA"
        border_color = "#E0E0E0"
        gradient1 = "#4facfe"
        gradient2 = "#00f2fe"

    return f"""
    <style>
        /* Main theme colors */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}

        /* Hide Streamlit default elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}

        /* Theme toggle button */
        .theme-toggle {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            background: linear-gradient(135deg, {gradient1} 0%, {gradient2} 100%);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }}

        .theme-toggle:hover {{
            transform: scale(1.1);
        }}

        /* Scrolling ticker */
        .ticker-container {{
            background: linear-gradient(135deg, {gradient1} 0%, {gradient2} 100%);
            color: white;
            padding: 10px 0;
            overflow: hidden;
            white-space: nowrap;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }}

        .ticker-content {{
            display: inline-block;
            animation: scroll-left 60s linear infinite;
            padding-left: 100%;
        }}

        @keyframes scroll-left {{
            0% {{ transform: translateX(0); }}
            100% {{ transform: translateX(-100%); }}
        }}

        .ticker-item {{
            display: inline-block;
            margin: 0 30px;
            font-weight: 600;
        }}

        /* Card styling */
        .metric-card {{
            background: {card_bg};
            padding: 1.5rem;
            border-radius: 15px;
            border: 1px solid {border_color};
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin: 0.5rem 0;
        }}

        /* Navigation pills */
        .nav-pills {{
            display: flex;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}

        .nav-pill {{
            background: {card_bg};
            padding: 10px 20px;
            border-radius: 25px;
            border: 2px solid {border_color};
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
        }}

        .nav-pill:hover {{
            background: linear-gradient(135deg, {gradient1} 0%, {gradient2} 100%);
            color: white;
            border-color: transparent;
        }}

        .nav-pill.active {{
            background: linear-gradient(135deg, {gradient1} 0%, {gradient2} 100%);
            color: white;
            border-color: transparent;
        }}

        /* Heatmap styling */
        .heatmap-container {{
            background: {card_bg};
            padding: 20px;
            border-radius: 15px;
            border: 1px solid {border_color};
            margin: 20px 0;
        }}

        /* Portfolio table */
        .portfolio-table {{
            width: 100%;
            border-collapse: collapse;
            background: {card_bg};
            border-radius: 10px;
            overflow: hidden;
        }}

        .portfolio-table th {{
            background: linear-gradient(135deg, {gradient1} 0%, {gradient2} 100%);
            color: white;
            padding: 12px;
            text-align: left;
        }}

        .portfolio-table td {{
            padding: 12px;
            border-bottom: 1px solid {border_color};
        }}

        /* Screener filters */
        .screener-filters {{
            background: {card_bg};
            padding: 20px;
            border-radius: 15px;
            border: 1px solid {border_color};
            margin: 20px 0;
        }}
    </style>
    """

# Apply theme CSS
st.markdown(get_theme_css(), unsafe_allow_html=True)

# Currency utilities
@st.cache_data(ttl=300)
def get_symbol_currency(symbol):
    """Resolve currency code for a given symbol"""
    try:
        ticker = yf.Ticker(symbol)
        currency = None
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
    """Fetch near-real-time quote"""
    data = {
        'price': None,
        'prev_close': None,
        'change_pct': None,
        'ts': None,
        'currency': get_symbol_currency(symbol)
    }
    try:
        t = yf.Ticker(symbol)
        fi = getattr(t, 'fast_info', {}) or {}
        price = fi.get('last_price') or fi.get('lastPrice') or fi.get('regular_market_price') or fi.get('last_close')
        prev_close = fi.get('previous_close') or fi.get('previousClose') or fi.get('last_close')

        if price is None or prev_close is None:
            try:
                info = t.get_info() if hasattr(t, 'get_info') else {}
            except:
                info = {}
            price = price or info.get('currentPrice') or info.get('regularMarketPrice')
            prev_close = prev_close or info.get('previousClose') or info.get('regularMarketPreviousClose')

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

# ========================= PAGE FUNCTIONS =========================

def render_ticker():
    """Render scrolling ticker with live prices"""
    ticker_stocks = st.session_state.watchlist[:10]  # Top 10 from watchlist
    ticker_html = '<div class="ticker-container"><div class="ticker-content">'

    for symbol in ticker_stocks:
        quote = get_live_quote(symbol)
        if quote and quote.get('price'):
            name = EXTENDED_INDIAN_STOCKS.get(symbol, {}).get('name', symbol)[:15]
            price = quote['price']
            change = quote.get('change_pct', 0)
            arrow = "▲" if change > 0 else "▼" if change < 0 else "●"
            color = "#2ecc71" if change > 0 else "#e74c3c" if change < 0 else "#95a5a6"

            ticker_html += f'''
            <span class="ticker-item">
                <strong>{name}</strong>
                {currency_symbol_for(symbol)}{price:.2f}
                <span style="color: {color};">{arrow} {abs(change):.2f}%</span>
            </span>
            '''

    ticker_html += '</div></div>'
    st.markdown(ticker_html, unsafe_allow_html=True)

def render_market_heatmap():
    """Render market heatmap by sector"""
    st.markdown("### 🔥 Market Heatmap by Sector")

    with st.spinner("Loading market data..."):
        # Calculate sector performance
        sector_data = {}
        for symbol, info in EXTENDED_INDIAN_STOCKS.items():
            sector = info.get('sector', 'Other')
            if sector not in sector_data:
                sector_data[sector] = {'stocks': [], 'changes': []}

            quote = get_live_quote(symbol)
            if quote and quote.get('change_pct') is not None:
                sector_data[sector]['stocks'].append(symbol)
                sector_data[sector]['changes'].append(quote['change_pct'])

        # Calculate average change per sector
        heatmap_data = []
        for sector, data in sector_data.items():
            if data['changes']:
                avg_change = np.mean(data['changes'])
                heatmap_data.append({
                    'Sector': sector,
                    'Change %': avg_change,
                    'Stocks': len(data['stocks'])
                })

        if heatmap_data:
            df = pd.DataFrame(heatmap_data)

            # Create treemap
            fig = px.treemap(
                df,
                path=['Sector'],
                values='Stocks',
                color='Change %',
                color_continuous_scale=['#e74c3c', '#f39c12', '#2ecc71'],
                color_continuous_midpoint=0,
                title='Sector Performance Heatmap'
            )

            fig.update_layout(
                height=400,
                template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white'
            )

            st.plotly_chart(fig, use_container_width=True)

            # Sector table
            df = df.sort_values('Change %', ascending=False)
            df['Change %'] = df['Change %'].apply(lambda x: f"{x:+.2f}%")
            st.dataframe(df, use_container_width=True, hide_index=True)

def render_dashboard():
    """Render main dashboard"""
    st.title("📊 Market Dashboard")

    # Real-time ticker
    render_ticker()

    # Quick stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Stocks", len(EXTENDED_INDIAN_STOCKS), "+5 new")

    with col2:
        st.metric("Watchlist", len(st.session_state.watchlist), "+2 today")

    with col3:
        portfolio_value = sum([p.get('current_value', 0) for p in st.session_state.portfolio])
        st.metric("Portfolio Value", f"₹{portfolio_value:,.2f}")

    with col4:
        st.metric("Market Status", "🟢 Open" if datetime.now().hour < 15 else "🔴 Closed")

    # Market heatmap
    render_market_heatmap()

    # Top gainers/losers
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Top Gainers")
        gainers = []
        for symbol in list(EXTENDED_INDIAN_STOCKS.keys())[:20]:
            quote = get_live_quote(symbol)
            if quote and quote.get('change_pct'):
                gainers.append({
                    'Symbol': symbol,
                    'Name': EXTENDED_INDIAN_STOCKS[symbol]['name'][:30],
                    'Price': format_price(symbol, quote['price']),
                    'Change': f"+{quote['change_pct']:.2f}%"
                })

        gainers = sorted(gainers, key=lambda x: float(x['Change'].replace('+', '').replace('%', '')), reverse=True)[:5]
        if gainers:
            st.dataframe(pd.DataFrame(gainers), use_container_width=True, hide_index=True)

    with col2:
        st.markdown("### 📉 Top Losers")
        losers = []
        for symbol in list(EXTENDED_INDIAN_STOCKS.keys())[:20]:
            quote = get_live_quote(symbol)
            if quote and quote.get('change_pct') and quote['change_pct'] < 0:
                losers.append({
                    'Symbol': symbol,
                    'Name': EXTENDED_INDIAN_STOCKS[symbol]['name'][:30],
                    'Price': format_price(symbol, quote['price']),
                    'Change': f"{quote['change_pct']:.2f}%"
                })

        losers = sorted(losers, key=lambda x: float(x['Change'].replace('%', '')))[:5]
        if losers:
            st.dataframe(pd.DataFrame(losers), use_container_width=True, hide_index=True)

def render_stock_screener():
    """Render stock screener page"""
    st.title("🔍 Stock Screener")

    st.markdown("### Filter Stocks by Criteria")

    # Filter controls
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

    # Apply filters button
    if st.button("🔍 Apply Filters", type="primary"):
        with st.spinner("Screening stocks..."):
            results = []

            for symbol, info in EXTENDED_INDIAN_STOCKS.items():
                # Apply sector filter
                if selected_sector != 'All' and info['sector'] != selected_sector:
                    continue

                quote = get_live_quote(symbol)
                if not quote or quote.get('price') is None:
                    continue

                price = quote['price']
                change = quote.get('change_pct', 0)

                # Apply filters
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

                # Sort
                if sort_by == "Change %":
                    df = df.sort_values('Change %', ascending=False)
                elif sort_by == "Price":
                    df = df.sort_values('Price', ascending=False)
                else:
                    df = df.sort_values('Name')

                # Display results
                st.success(f"Found {len(df)} stocks matching your criteria")

                # Format for display
                display_df = df[['Symbol', 'Name', 'Sector', 'Price (Formatted)', 'Change %']].copy()
                display_df['Change %'] = display_df['Change %'].apply(lambda x: f"{x:+.2f}%")
                display_df.columns = ['Symbol', 'Name', 'Sector', 'Price', 'Change %']

                st.dataframe(display_df, use_container_width=True, hide_index=True)

                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results (CSV)",
                    data=csv,
                    file_name=f"stock_screener_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No stocks found matching your criteria. Try adjusting the filters.")

def render_portfolio_tracker():
    """Render portfolio tracker page"""
    st.title("💼 Portfolio Tracker")

    # Add position form
    with st.expander("➕ Add New Position", expanded=False):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            p_symbol = st.selectbox(
                "Stock Symbol",
                options=list(EXTENDED_INDIAN_STOCKS.keys()),
                format_func=lambda x: f"{x} - {EXTENDED_INDIAN_STOCKS[x]['name'][:20]}"
            )

        with col2:
            p_quantity = st.number_input("Quantity", min_value=1, value=10, step=1)

        with col3:
            p_buy_price = st.number_input("Buy Price (₹)", min_value=0.01, value=100.0, step=0.01)

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
            st.success(f"Added {p_quantity} shares of {p_symbol} to portfolio!")
            st.rerun()

    # Display portfolio
    if st.session_state.portfolio:
        st.markdown("### 📊 Your Portfolio")

        # Calculate portfolio metrics
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
                'Name': position['name'][:25],
                'Quantity': position['quantity'],
                'Buy Price': f"₹{position['buy_price']:.2f}",
                'Current Price': format_price(position['symbol'], current_price),
                'Buy Value': f"₹{position['buy_value']:,.2f}",
                'Current Value': f"₹{current_value:,.2f}",
                'P&L': f"₹{profit_loss:,.2f}",
                'P&L %': f"{profit_loss_pct:+.2f}%",
                'Days Held': (datetime.now() - datetime.strptime(position['buy_date'], '%Y-%m-%d')).days,
                '_pl_value': profit_loss,
                '_current_val': current_value
            })

        # Portfolio summary
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

        # Portfolio table
        df = pd.DataFrame(portfolio_data)
        display_df = df.drop(columns=['_pl_value', '_current_val'])
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Portfolio allocation pie chart
        st.markdown("### 📊 Portfolio Allocation")
        fig = px.pie(
            df,
            values='_current_val',
            names='Symbol',
            title='Portfolio Allocation by Current Value'
        )
        fig.update_layout(
            template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        # Performance chart
        st.markdown("### 📈 Position Performance")
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df['Symbol'],
            y=df['_pl_value'],
            name='P&L',
            marker_color=['#2ecc71' if x > 0 else '#e74c3c' for x in df['_pl_value']]
        ))

        fig.update_layout(
            title='Profit/Loss by Position',
            xaxis_title='Stock',
            yaxis_title='P&L (₹)',
            template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # Actions
        col1, col2 = st.columns([3, 1])

        with col1:
            if st.button("🗑️ Clear Portfolio", type="secondary"):
                st.session_state.portfolio = []
                st.success("Portfolio cleared!")
                st.rerun()

        with col2:
            csv = pd.DataFrame(st.session_state.portfolio).to_csv(index=False)
            st.download_button(
                label="📥 Export",
                data=csv,
                file_name=f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("Your portfolio is empty. Add positions using the form above!")

def render_advanced_charting():
    """Render advanced charting page"""
    st.title("📈 Advanced Charting")

    # Stock selection
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        selected_stock = st.selectbox(
            "Select Stock",
            options=list(EXTENDED_INDIAN_STOCKS.keys()),
            format_func=lambda x: f"{x} - {EXTENDED_INDIAN_STOCKS[x]['name']}"
        )

    with col2:
        timeframe = st.selectbox(
            "Timeframe",
            options=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y'],
            index=3
        )

    with col3:
        interval = st.selectbox(
            "Interval",
            options=['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'],
            index=5
        )

    # Fetch data
    with st.spinner(f"Loading {selected_stock} data..."):
        try:
            ticker = yf.Ticker(selected_stock)
            df = ticker.history(period=timeframe, interval=interval)

            if df.empty:
                st.error("No data available for this stock/timeframe combination.")
                return

            # Chart options
            col1, col2, col3 = st.columns(3)

            with col1:
                chart_type = st.selectbox("Chart Type", ['Candlestick', 'Line', 'OHLC', 'Area'])

            with col2:
                show_volume = st.checkbox("Show Volume", value=True)

            with col3:
                show_ma = st.checkbox("Show Moving Averages", value=True)

            # Technical indicators
            st.markdown("#### Technical Indicators")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                show_rsi = st.checkbox("RSI")

            with col2:
                show_macd = st.checkbox("MACD")

            with col3:
                show_bb = st.checkbox("Bollinger Bands")

            with col4:
                show_ema = st.checkbox("EMA")

            # Calculate indicators
            if show_ma:
                df['MA20'] = df['Close'].rolling(window=20).mean()
                df['MA50'] = df['Close'].rolling(window=50).mean()

            if show_ema:
                df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
                df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()

            if show_bb:
                df['BB_middle'] = df['Close'].rolling(window=20).mean()
                bb_std = df['Close'].rolling(window=20).std()
                df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
                df['BB_lower'] = df['BB_middle'] - (bb_std * 2)

            if show_rsi:
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))

            if show_macd:
                exp1 = df['Close'].ewm(span=12, adjust=False).mean()
                exp2 = df['Close'].ewm(span=26, adjust=False).mean()
                df['MACD'] = exp1 - exp2
                df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
                df['MACD_hist'] = df['MACD'] - df['MACD_signal']

            # Create subplots
            rows = 1
            row_heights = [0.7]
            subplot_titles = ['Price']

            if show_volume:
                rows += 1
                row_heights.append(0.15)
                subplot_titles.append('Volume')

            if show_rsi:
                rows += 1
                row_heights.append(0.15)
                subplot_titles.append('RSI')

            if show_macd:
                rows += 1
                row_heights.append(0.15)
                subplot_titles.append('MACD')

            # Normalize row heights
            total_height = sum(row_heights)
            row_heights = [h/total_height for h in row_heights]

            fig = make_subplots(
                rows=rows,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=row_heights,
                subplot_titles=subplot_titles
            )

            # Main price chart
            if chart_type == 'Candlestick':
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='Price'
                ), row=1, col=1)
            elif chart_type == 'Line':
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['Close'],
                    mode='lines',
                    name='Close',
                    line=dict(color='#1f77b4', width=2)
                ), row=1, col=1)
            elif chart_type == 'OHLC':
                fig.add_trace(go.Ohlc(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='Price'
                ), row=1, col=1)
            elif chart_type == 'Area':
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['Close'],
                    fill='tozeroy',
                    name='Close',
                    line=dict(color='#1f77b4', width=2)
                ), row=1, col=1)

            # Add moving averages
            if show_ma:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df['MA20'],
                    mode='lines', name='MA20',
                    line=dict(color='orange', width=1)
                ), row=1, col=1)

                fig.add_trace(go.Scatter(
                    x=df.index, y=df['MA50'],
                    mode='lines', name='MA50',
                    line=dict(color='green', width=1)
                ), row=1, col=1)

            # Add EMA
            if show_ema:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df['EMA12'],
                    mode='lines', name='EMA12',
                    line=dict(color='purple', width=1, dash='dash')
                ), row=1, col=1)

                fig.add_trace(go.Scatter(
                    x=df.index, y=df['EMA26'],
                    mode='lines', name='EMA26',
                    line=dict(color='brown', width=1, dash='dash')
                ), row=1, col=1)

            # Add Bollinger Bands
            if show_bb:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df['BB_upper'],
                    mode='lines', name='BB Upper',
                    line=dict(color='gray', width=1, dash='dot'),
                    showlegend=False
                ), row=1, col=1)

                fig.add_trace(go.Scatter(
                    x=df.index, y=df['BB_lower'],
                    mode='lines', name='BB Lower',
                    line=dict(color='gray', width=1, dash='dot'),
                    fill='tonexty',
                    fillcolor='rgba(128,128,128,0.1)',
                    showlegend=False
                ), row=1, col=1)

            current_row = 1

            # Add volume
            if show_volume:
                current_row += 1
                colors = ['#2ecc71' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#e74c3c'
                         for i in range(len(df))]

                fig.add_trace(go.Bar(
                    x=df.index,
                    y=df['Volume'],
                    name='Volume',
                    marker_color=colors,
                    showlegend=False
                ), row=current_row, col=1)

            # Add RSI
            if show_rsi:
                current_row += 1
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['RSI'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='purple', width=2),
                    showlegend=False
                ), row=current_row, col=1)

                fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=current_row, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=current_row, col=1)

            # Add MACD
            if show_macd:
                current_row += 1
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['MACD'],
                    mode='lines',
                    name='MACD',
                    line=dict(color='blue', width=2),
                    showlegend=False
                ), row=current_row, col=1)

                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df['MACD_signal'],
                    mode='lines',
                    name='Signal',
                    line=dict(color='red', width=2),
                    showlegend=False
                ), row=current_row, col=1)

                colors = ['green' if val >= 0 else 'red' for val in df['MACD_hist']]
                fig.add_trace(go.Bar(
                    x=df.index,
                    y=df['MACD_hist'],
                    name='Histogram',
                    marker_color=colors,
                    showlegend=False
                ), row=current_row, col=1)

            # Update layout
            fig.update_layout(
                title=f'{selected_stock} - {EXTENDED_INDIAN_STOCKS[selected_stock]["name"]}',
                xaxis_rangeslider_visible=False,
                template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white',
                height=800,
                showlegend=True,
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)

            # Current stats
            st.markdown("### 📊 Current Statistics")
            col1, col2, col3, col4, col5 = st.columns(5)

            current_price = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2] if len(df) > 1 else current_price
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100

            with col1:
                st.metric("Current Price", format_price(selected_stock, current_price),
                         f"{change_pct:+.2f}%")

            with col2:
                st.metric("High", format_price(selected_stock, df['High'].max()))

            with col3:
                st.metric("Low", format_price(selected_stock, df['Low'].min()))

            with col4:
                st.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")

            with col5:
                volatility = df['Close'].pct_change().std() * 100
                st.metric("Volatility", f"{volatility:.2f}%")

        except Exception as e:
            st.error(f"Error loading chart: {str(e)}")

def render_stock_analysis():
    """Render the original stock analysis page"""
    st.title("🤖 AI Stock Analysis")

    # This would be the original analysis functionality
    # Import from the original web_app.py functions
    st.info("This is where the AI prediction analysis would go. Integrating with original web_app.py...")

# ========================= MAIN APP =========================

def main():
    """Main application"""

    # Theme toggle button
    col1, col2, col3 = st.columns([6, 1, 1])

    with col3:
        theme_icon = "🌙" if st.session_state.theme == 'dark' else "☀️"
        if st.button(theme_icon, key="theme_toggle"):
            st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            st.rerun()

    # Navigation
    st.sidebar.title("🎯 Navigation")

    pages = {
        "📊 Dashboard": render_dashboard,
        "📈 Advanced Charts": render_advanced_charting,
        "🤖 AI Analysis": render_stock_analysis,
        "🔍 Stock Screener": render_stock_screener,
        "💼 Portfolio": render_portfolio_tracker
    }

    page = st.sidebar.radio("Select Page", list(pages.keys()), key="page_selector")

    # Watchlist management
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⭐ Watchlist")

    with st.sidebar.expander("Manage Watchlist"):
        new_stock = st.selectbox(
            "Add Stock",
            options=[s for s in EXTENDED_INDIAN_STOCKS.keys() if s not in st.session_state.watchlist],
            key="watchlist_add"
        )

        if st.button("➕ Add"):
            if new_stock not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_stock)
                st.success(f"Added {new_stock}")
                st.rerun()

        if st.session_state.watchlist:
            for stock in st.session_state.watchlist[:5]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(stock)
                with col2:
                    if st.button("🗑️", key=f"remove_{stock}"):
                        st.session_state.watchlist.remove(stock)
                        st.rerun()

    # Render selected page
    pages[page]()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <small>
        Made with ❤️ by Umair Kashif<br>
        Enhanced Professional Edition
        </small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
