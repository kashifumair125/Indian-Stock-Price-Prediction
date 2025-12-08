"""
Indian Stock Price Prediction - Interactive Web Application
Premium Responsive Design with Modern UI/UX
Date: 2025

A beautiful, mobile-friendly Streamlit web interface for stock prediction.
Run with: streamlit run web_app.py
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

# Modern UI Components
try:
    from streamlit_option_menu import option_menu
    from streamlit_extras.metric_cards import style_metric_cards
    from streamlit_extras.colored_header import colored_header
    from streamlit_extras.add_vertical_space import add_vertical_space
except ImportError:
    pass  # Graceful fallback if extras not installed

# Premium Styles
try:
    from premium_styles import get_premium_css
except ImportError:
    def get_premium_css(dark_mode=False):
        return "<style></style>"  # Fallback

# Suppress warnings
warnings.filterwarnings('ignore')

# Page configuration - Premium Responsive Setup
st.set_page_config(
    page_title="Indian Stock Price Prediction",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/kashifumair125/Indian-Stock-Price-Prediction',
        'Report a bug': 'https://github.com/kashifumair125/Indian-Stock-Price-Prediction/issues',
        'About': '# Premium Stock Prediction System\nAI-Powered Stock Analysis with Modern UI/UX'
    }
)

# Initialize session state for dark mode
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Apply Premium Responsive CSS
st.markdown(get_premium_css(st.session_state.dark_mode), unsafe_allow_html=True)

# Add experimental sidebar control
try:
    import streamlit as st
    # Try to use experimental features for sidebar control
    if hasattr(st, 'experimental_rerun'):
        st.experimental_rerun = st.rerun
except:
    pass

# Add src to path (if needed)
sys.path.append('src')

try:
    from stock_predictor import IndianStockPredictor
except ImportError as e:
    # If import fails, show error
    st.error(f"""
    ❌ **Import Error**: {e}
    
    Please ensure that:
    1. The `stock_predictor.py` file is in the same directory or in a `src/` folder
    2. All required packages are installed: `pip install yfinance scikit-learn pandas numpy matplotlib seaborn`
    3. For LSTM: `pip install tensorflow`
    4. For Prophet: `pip install prophet` or `pip install fbprophet`
    """)
    st.stop()

# Dark Mode Toggle Button
col_dm1, col_dm2, col_dm3 = st.columns([1, 4, 1])
with col_dm3:
    dark_mode_label = "🌙 Dark" if not st.session_state.dark_mode else "☀️ Light"
    if st.button(dark_mode_label, key="dark_mode_toggle", use_container_width=True):
        toggle_dark_mode()
        st.rerun()

# Enhanced stock list with more Indian stocks
EXTENDED_INDIAN_STOCKS = {
    # Large Cap IT
    'TCS.NS': 'Tata Consultancy Services Limited',
    'INFY.NS': 'Infosys Limited',
    'WIPRO.NS': 'Wipro Limited',
    'TECHM.NS': 'Tech Mahindra Limited',
    'HCLTECH.NS': 'HCL Technologies Limited',
    'LTI.NS': 'L&T Infotech Limited',
    
    # Banking & Finance
    'HDFCBANK.NS': 'HDFC Bank Limited',
    'ICICIBANK.NS': 'ICICI Bank Limited',
    'SBIN.NS': 'State Bank of India',
    'KOTAKBANK.NS': 'Kotak Mahindra Bank Limited',
    'AXISBANK.NS': 'Axis Bank Limited',
    'INDUSINDBK.NS': 'IndusInd Bank Limited',
    'BAJFINANCE.NS': 'Bajaj Finance Limited',
    'BAJAJFINSV.NS': 'Bajaj Finserv Limited',
    'HDFCLIFE.NS': 'HDFC Life Insurance',
    'SBILIFE.NS': 'SBI Life Insurance',
    
    # Energy & Oil
    'RELIANCE.NS': 'Reliance Industries Limited',
    'ONGC.NS': 'Oil and Natural Gas Corporation',
    'IOC.NS': 'Indian Oil Corporation',
    'BPCL.NS': 'Bharat Petroleum Corporation',
    'HINDPETRO.NS': 'Hindustan Petroleum Corporation',
    'ADANIPORTS.NS': 'Adani Ports and SEZ Limited',
    'ADANIGREEN.NS': 'Adani Green Energy Limited',
    
    # FMCG & Consumer
    'HINDUNILVR.NS': 'Hindustan Unilever Limited',
    'ITC.NS': 'ITC Limited',
    'NESTLEIND.NS': 'Nestle India Limited',
    'BRITANNIA.NS': 'Britannia Industries Limited',
    'DABUR.NS': 'Dabur India Limited',
    'GODREJCP.NS': 'Godrej Consumer Products',
    'MARICO.NS': 'Marico Limited',
    'COLPAL.NS': 'Colgate-Palmolive India',
    
    # Automobiles
    'MARUTI.NS': 'Maruti Suzuki India Limited',
    'TATAMOTORS.NS': 'Tata Motors Limited',
    'M&M.NS': 'Mahindra & Mahindra Limited',
    'BAJAJ-AUTO.NS': 'Bajaj Auto Limited',
    'HEROMOTOCO.NS': 'Hero MotoCorp Limited',
    'EICHERMOT.NS': 'Eicher Motors Limited',
    'ASHOKLEY.NS': 'Ashok Leyland Limited',
    
    # Pharmaceuticals
    'SUNPHARMA.NS': 'Sun Pharmaceutical Industries',
    'DRREDDY.NS': 'Dr. Reddy\'s Laboratories',
    'CIPLA.NS': 'Cipla Limited',
    'BIOCON.NS': 'Biocon Limited',
    'AUROPHARMA.NS': 'Aurobindo Pharma Limited',
    'LUPIN.NS': 'Lupin Limited',
    'DIVISLAB.NS': 'Divi\'s Laboratories Limited',
    
    # Telecom
    'BHARTIARTL.NS': 'Bharti Airtel Limited',
    'IDEA.NS': 'Vodafone Idea Limited',
    
    # Metals & Mining
    'TATASTEEL.NS': 'Tata Steel Limited',
    'JSWSTEEL.NS': 'JSW Steel Limited',
    'HINDALCO.NS': 'Hindalco Industries Limited',
    'COALINDIA.NS': 'Coal India Limited',
    'VEDL.NS': 'Vedanta Limited',
    'NMDC.NS': 'NMDC Limited',
    
    # Construction & Infrastructure
    'LT.NS': 'Larsen & Toubro Limited',
    'ULTRACEMCO.NS': 'UltraTech Cement Limited',
    'SHREECEM.NS': 'Shree Cement Limited',
    'ACC.NS': 'ACC Limited',
    'GRASIM.NS': 'Grasim Industries Limited',
    
    # Power & Utilities
    'POWERGRID.NS': 'Power Grid Corporation',
    'NTPC.NS': 'NTPC Limited',
    'TATAPOWER.NS': 'Tata Power Company',
    
    # Consumer Durables
    'TITAN.NS': 'Titan Company Limited',
    'ASIANPAINT.NS': 'Asian Paints Limited',
    'PIDILITIND.NS': 'Pidilite Industries Limited',
    'VOLTAS.NS': 'Voltas Limited',
    'HAVELLS.NS': 'Havells India Limited',
}

@st.cache_data(ttl=300)
def get_symbol_currency(symbol):
    """Resolve currency code for a given symbol using yfinance fast_info/info."""
    try:
        ticker = yf.Ticker(symbol)
        currency = None
        # Prefer fast_info
        try:
            currency = getattr(ticker, 'fast_info', {}).get('currency')
        except Exception:
            currency = None
        if not currency:
            try:
                info = ticker.get_info() if hasattr(ticker, 'get_info') else {}
            except Exception:
                info = {}
            currency = info.get('currency') or info.get('financialCurrency')
        return (currency or 'INR').upper()
    except Exception:
        return 'INR'

def currency_symbol_for(symbol):
    code = get_symbol_currency(symbol)
    return CURRENCY_SYMBOLS.get(code, CURRENCY_SYMBOL)

def format_price(symbol, value):
    return f"{currency_symbol_for(symbol)}{value:.2f}"

@st.cache_data(ttl=LIVE_REFRESH_SECONDS)
def get_live_quote(symbol):
    """Fetch near-real-time quote using yfinance; no API key required.
    Returns dict: price, prev_close, change_pct, ts, currency.
    """
    data = {
        'price': None,
        'prev_close': None,
        'change_pct': None,
        'ts': None,
        'currency': get_symbol_currency(symbol)
    }
    try:
        t = yf.Ticker(symbol)
        # Try fast_info first
        fi = getattr(t, 'fast_info', {}) or {}
        price = fi.get('last_price') or fi.get('lastPrice') or fi.get('regular_market_price') or fi.get('last_close')
        prev_close = fi.get('previous_close') or fi.get('previousClose') or fi.get('last_close')
        # Fallback to info
        if price is None or prev_close is None:
            try:
                info = t.get_info() if hasattr(t, 'get_info') else {}
            except Exception:
                info = {}
            price = price or info.get('currentPrice') or info.get('regularMarketPrice')
            prev_close = prev_close or info.get('previousClose') or info.get('regularMarketPreviousClose')
        # Fallback to 1m history last bar
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
    except Exception:
        pass
    return data

@st.cache_data(ttl=300)
def search_symbols(query, max_results=20):
    """Search global symbols using Yahoo Finance's public search endpoint.
    No API key required.
    """
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/search"
        params = {
            'q': query,
            'quotesCount': max_results,
            'newsCount': 0,
            'listsCount': 0,
            'enableFuzzyQuery': True,
        }
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        js = r.json()
        quotes = js.get('quotes', [])
        results = []
        for q in quotes:
            symbol = q.get('symbol')
            shortname = q.get('shortname') or q.get('longname') or ''
            exch = q.get('exchDisp') or q.get('exchange') or ''
            currency = q.get('currency') or ''
            quote_type = q.get('quoteType') or ''
            if not symbol:
                continue
            results.append({
                'symbol': symbol,
                'label': f"{shortname} ({symbol}) - {exch} {('['+currency+']') if currency else ''}",
                'currency': currency,
                'exchange': exch,
                'quote_type': quote_type,
            })
        return results
    except Exception:
        return []

def show_animated_header():
    """Display animated header"""
    header_html = """
    <div style="text-align: center; padding: 2rem;">
        <h1 class="main-header">📈 Indian Stock Price Prediction System</h1>
        <p style="font-size: 1.2rem; color: #666; margin-top: -1rem;">
            AI-Powered Stock Analysis & Future Price Prediction
        </p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def create_custom_metric(title, value, delta=None, color="#1f77b4"):
    """Create a custom metric card"""
    delta_html = ""
    if delta:
        delta_color = "#2ca02c" if delta.startswith("+") else "#d62728"
        delta_html = f'<p style="color: {delta_color}; font-size: 0.9rem; margin-top: 0.5rem;">{delta}</p>'
    
    metric_html = f"""
    <div style="
        background: linear-gradient(135deg, {color}20, {color}40);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border-left: 4px solid {color};
        margin: 0.5rem 0;
    ">
        <h3 style="margin: 0; color: {color};">{title}</h3>
        <h2 style="margin: 0.5rem 0; color: #333;">{value}</h2>
        {delta_html}
    </div>
    """
    return metric_html

def main():
    """Main Streamlit application"""

    # Initialize sidebar state
    if 'sidebar_visible' not in st.session_state:
        st.session_state.sidebar_visible = True

    # Initialize first-time user flag
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True

    # Animated Header
    show_animated_header()

    # Welcome Message for First-Time Users
    if st.session_state.first_visit:
        st.markdown("""
        <div class="info-box" style="animation: pulse 2s ease-in-out;">
            <h3>👋 Welcome to the Premium Stock Prediction Platform!</h3>
            <p><strong>Quick Tips to Get Started:</strong></p>
            <ul style="text-align: left; margin: 1rem 0;">
                <li>🎨 <strong>Dark Mode Available</strong>: Click the toggle button at the top-right</li>
                <li>📱 <strong>Mobile Friendly</strong>: Works perfectly on all devices</li>
                <li>🚀 <strong>Quick Start</strong>: Use the sidebar to select a stock and start analyzing</li>
                <li>💡 <strong>Beginner?</strong> Expand "New to Stock Prediction?" in the sidebar</li>
                <li>📊 <strong>Popular Stocks</strong>: Click TCS, Reliance, or HDFC Bank to start quickly</li>
            </ul>
            <p style="margin-top: 1rem;"><em>🎯 Tip: Select all 3 AI models for the most accurate predictions!</em></p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("✅ Got it!", use_container_width=True, key="dismiss_welcome"):
                st.session_state.first_visit = False
                st.rerun()
    
    # Add JavaScript-based sidebar toggle
    st.markdown("""
    <script>
        // Function to toggle sidebar visibility
        function toggleSidebarJS() {
            const sidebar = document.querySelector('[data-testid="stSidebar"]') || 
                           document.querySelector('.css-1d391kg') ||
                           document.querySelector('.css-1lcbmhc');
            if (sidebar) {
                const currentDisplay = sidebar.style.display || getComputedStyle(sidebar).display;
                if (currentDisplay === 'none') {
                    sidebar.style.display = 'block';
                    sidebar.style.visibility = 'visible';
                    console.log('Sidebar shown via JavaScript');
                } else {
                    sidebar.style.display = 'none';
                    sidebar.style.visibility = 'hidden';
                    console.log('Sidebar hidden via JavaScript');
                }
            } else {
                console.log('Sidebar element not found');
            }
        }
        // Add keyboard shortcut
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'S') {
                e.preventDefault();
                toggleSidebarJS();
            }
        });
    </script>
    """, unsafe_allow_html=True)
    
    # Remove Sidebar Controls and Sidebar Control Panel sections
    # (Removed: st.markdown("### 🔧 Sidebar Controls"), button groups, and status indicators)
    
    # Add floating sidebar toggle button with enhanced functionality
    st.markdown("""
    <div class="sidebar-toggle-btn" onclick="toggleSidebar()" title="Toggle Sidebar (Ctrl+Shift+S)">
        📊
    </div>
    
    <script>
        function toggleSidebar() {
            // Try multiple selectors to find the sidebar
            const sidebarSelectors = [
                '.css-1d391kg',           // Common Streamlit sidebar selector
                '[data-testid="stSidebar"]', // Streamlit test ID
                '.css-1lcbmhc',           // Alternative selector
                '.css-1d391kg',           // Another common one
                'aside[data-testid="stSidebar"]', // Semantic selector
                '.css-1d391kg'            // Fallback
            ];
            
            let sidebar = null;
            for (let selector of sidebarSelectors) {
                sidebar = document.querySelector(selector);
                if (sidebar) break;
            }
            
            if (sidebar) {
                const currentDisplay = sidebar.style.display || getComputedStyle(sidebar).display;
                
                if (currentDisplay === 'none') {
                    sidebar.style.display = 'block';
                    sidebar.style.visibility = 'visible';
                    document.title = '📊 Sidebar Visible';
                    hideShowSidebarBanner();
                    console.log('Sidebar shown');
                } else {
                    sidebar.style.display = 'none';
                    sidebar.style.visibility = 'hidden';
                    document.title = '📊 Sidebar Hidden';
                    showSidebarBanner();
                    console.log('Sidebar hidden');
                }
            } else {
                console.log('Sidebar not found, trying alternative method...');
                // Alternative method: try to toggle using Streamlit's internal state
                try {
                    // Try to trigger a click on the hamburger menu if it exists
                    const hamburger = document.querySelector('[data-testid="collapsedControl"]');
                    if (hamburger) {
                        hamburger.click();
                        console.log('Hamburger menu clicked');
                    } else {
                        console.log('Hamburger menu not found');
                    }
                } catch (e) {
                    console.log('Alternative method failed:', e);
                }
            }
        }
        
        function showSidebarBanner() {
            const banner = document.getElementById('show-sidebar-banner');
            if (banner) {
                banner.style.display = 'block';
            }
        }
        
        function hideShowSidebarBanner() {
            const banner = document.getElementById('show-sidebar-banner');
            if (banner) {
                banner.style.display = 'none';
            }
        }
        
        // Add keyboard shortcut (Ctrl+Shift+S or Cmd+Shift+S)
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'S') {
                e.preventDefault();
                toggleSidebar();
            }
        });
        
        // Check sidebar state on page load and periodically
        function checkSidebarState() {
            const sidebarSelectors = [
                '.css-1d391kg',
                '[data-testid="stSidebar"]',
                '.css-1lcbmhc',
                'aside[data-testid="stSidebar"]'
            ];
            
            let sidebar = null;
            for (let selector of sidebarSelectors) {
                sidebar = document.querySelector(selector);
                if (sidebar) break;
            }
            
            if (sidebar) {
                const currentDisplay = sidebar.style.display || getComputedStyle(sidebar).display;
                if (currentDisplay === 'none') {
                    showSidebarBanner();
                } else {
                    hideShowSidebarBanner();
                }
            }
        }
        
        // Check on load and periodically
        window.addEventListener('load', function() {
            setTimeout(checkSidebarState, 1000);
            // Check every 2 seconds
            setInterval(checkSidebarState, 2000);
        });
        
        // Also check when DOM changes
        const observer = new MutationObserver(checkSidebarState);
        observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """, unsafe_allow_html=True)
    
    # Add prominent "Show Sidebar" button when sidebar is collapsed
    st.markdown("""
    <div id="show-sidebar-banner" style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        display: none;
    ">
        <h3 style="margin: 0 0 10px 0;">📊 Sidebar Hidden</h3>
        <p style="margin: 0 0 15px 0;">Click the floating button (📊) in the top-left corner or use <strong>Ctrl+Shift+S</strong> to show the sidebar again!</p>
        <button onclick="toggleSidebar()" style="
            background: white;
            color: #667eea;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            cursor: pointer;
            font-size: 16px;
        ">📊 Show Sidebar</button>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Control Panel removed per request
    
    # Enhanced Sidebar with improved UI/UX for beginners
    with st.sidebar:
        # Welcome header with helpful intro
        st.markdown("""
        <div style='text-align: center; padding: 10px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0;'>🎯 Stock Prediction Hub</h2>
            <p style='color: white; margin: 5px 0 0 0; font-size: 14px;'>AI-powered stock analysis made simple</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick start guide for beginners
        with st.expander("🚀 New to Stock Prediction? Start Here!", expanded=False):
            st.markdown("""
            **Quick Guide:**
            1. **Choose a stock** you're interested in
            2. **Select time period** (1 year recommended for beginners)
            3. **Pick AI models** (all 3 selected gives best results)
            4. **Click 'Start Analysis'** and let AI do the work!
            
            💡 **Tip**: Start with popular stocks like TCS or Reliance for reliable predictions.
            """)
        
        # Stock Selection Section with better guidance
        st.markdown("### 📊 Step 1: Choose Your Stock")
        
        # Popular stocks shortcut
        st.markdown("**🔥 Popular Stocks (Click to select):**")
        popular_cols = st.columns(3)
        popular_stocks = ["TCS.NS", "RELIANCE.NS", "HDFCBANK.NS"]
        popular_names = ["TCS", "Reliance", "HDFC Bank"]
        
        for i, (stock, name) in enumerate(zip(popular_stocks, popular_names)):
            with popular_cols[i]:
                # Add custom class to the button for styling
                st.markdown(f'<div class="popular-stock-btn">', unsafe_allow_html=True)
                if st.button(name, key=f"popular_{i}", use_container_width=True):
                    st.session_state.quick_select = stock
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Search functionality with better UX
        st.markdown("**🔍 Or Search for Any Stock:**")
        search_term = st.text_input(
            "",
            placeholder="Type stock name or symbol (e.g., TCS, Infosys, HDFC, AAPL, MSFT)",
            help="💡 For Indian stocks, you can just type the company name!"
        )
        global_search = st.checkbox("Search globally (Yahoo)", value=False, help="Search all markets via Yahoo's public search")
        
        # Handle quick selection
        if 'quick_select' in st.session_state:
            selected_stock = st.session_state.quick_select
            st.success(f"✅ Selected: {EXTENDED_INDIAN_STOCKS.get(selected_stock, selected_stock)}")
            del st.session_state.quick_select
        else:
            if search_term and global_search:
                results = search_symbols(search_term)
                if results:
                    labels = [r['label'] for r in results]
                    choice = st.selectbox(
                        "Available matches:",
                        options=labels,
                        index=0,
                        help="Select from global search results"
                    )
                    match = next((r for r in results if r['label'] == choice), None)
                    selected_stock = match['symbol'] if match else "TCS.NS"
                else:
                    st.warning("❌ No global matches found. Try a different search term.")
                    # Fallback to Indian list
                    selected_stock = "TCS.NS"
            else:
                if search_term:
                    # Filter stocks based on search
                    filtered_stocks = {k: v for k, v in EXTENDED_INDIAN_STOCKS.items() 
                                     if search_term.lower() in k.lower() or search_term.lower() in v.lower()}
                    stock_options = list(filtered_stocks.keys())
                else:
                    stock_options = list(EXTENDED_INDIAN_STOCKS.keys())
                
                if stock_options:
                    selected_stock = st.selectbox(
                        "Available matches:",
                        options=stock_options,
                        format_func=lambda x: f"📈 {EXTENDED_INDIAN_STOCKS.get(x, 'Unknown')} ({x})",
                        index=0,
                        help="Select from the filtered results"
                    )
                else:
                    if search_term:
                        st.warning("❌ No stocks found. Try a different search term.")
                    selected_stock = "TCS.NS"
        
        # Custom stock input with better guidance
        st.markdown("**📝 Custom Stock Symbol:**")
        custom_stock = st.text_input(
            "",
            placeholder="Enter any stock symbol (e.g., GOOGL, AAPL, MSFT)",
            help="🌍 For Indian stocks add .NS (e.g., WIPRO.NS), for US stocks use direct symbol"
        )
        
        if custom_stock:
            selected_stock = custom_stock.upper()
            if not custom_stock.endswith('.NS') and not any(c in custom_stock for c in ['.', ':']):
                st.info("💡 For Indian stocks, consider adding '.NS' at the end")
        
        st.markdown("---")

        # Live snapshot for selected symbol
        st.markdown("### ⏱️ Live Snapshot")
        quote = get_live_quote(selected_stock)
        if quote and quote.get('price') is not None:
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric(
                    label=f"{selected_stock} Price",
                    value=format_price(selected_stock, quote['price']),
                    delta=f"{quote['change_pct']:+.2f}%" if quote.get('change_pct') is not None else None
                )
            with col_b:
                ts = quote.get('ts')
                ts_str = ts.strftime('%Y-%m-%d %H:%M:%S') if ts else '—'
                st.caption(f"As of: {ts_str} | Currency: {get_symbol_currency(selected_stock)}")
        else:
            st.info("Live quote not available right now.")
        if st.button("🔄 Refresh live quote", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        # Time Period Selection with beginner-friendly explanations
        st.markdown("### 📅 Step 2: Choose Time Period")
        
        period_info = {
            '3mo': {'name': '3 Months', 'desc': 'Short-term trends', 'icon': '⚡', 'level': 'Quick'},
            '6mo': {'name': '6 Months', 'desc': 'Medium-term patterns', 'icon': '📊', 'level': 'Balanced'},
            '1y': {'name': '1 Year', 'desc': 'Full market cycle', 'icon': '🎯', 'level': 'Recommended'},
            '2y': {'name': '2 Years', 'desc': 'Long-term trends', 'icon': '📈', 'level': 'Comprehensive'},
            '5y': {'name': '5 Years', 'desc': 'Historical patterns', 'icon': '🏛️', 'level': 'Deep Analysis'}
        }
        
        selected_period = st.selectbox(
            "Select analysis period:",
            options=list(period_info.keys()),
            format_func=lambda x: f"{period_info[x]['icon']} {period_info[x]['name']} - {period_info[x]['level']}",
            index=2,  # Default to 1 year
            help="💡 1 Year is recommended for beginners as it captures seasonal patterns"
        )
        
        # Show period description
        period_data = period_info[selected_period]
        st.markdown(f"📋 **{period_data['name']}**: {period_data['desc']}")
        
        st.markdown("---")
        
        # AI Models Selection with clear explanations
        st.markdown("### 🤖 Step 3: Choose AI Models")
        
        st.markdown("💡 **Beginner Tip**: Select all models for most accurate predictions!")
        
        # Model selection with visual indicators
        col1, col2 = st.columns([3, 1])
        
        with col1:
            use_linear = st.checkbox("📊 Linear Regression", value=True)
        with col2:
            st.markdown("🟢 **Fast**")
        
        if use_linear:
            st.markdown("   └─ *Great for identifying basic trends and patterns*")
        
        with col1:
            use_lstm = st.checkbox("🧠 LSTM Neural Network", value=True)
        with col2:
            st.markdown("🟡 **Smart**")
        
        if use_lstm:
            st.markdown("   └─ *Advanced AI that learns complex market patterns*")
        
        with col1:
            use_prophet = st.checkbox("📈 Prophet Time Series", value=True)
        with col2:
            st.markdown("🔵 **Seasonal**")
        
        if use_prophet:
            st.markdown("   └─ *Excellent at predicting seasonal market behavior*")
        
        # Model recommendation based on selection
        selected_models = sum([use_linear, use_lstm, use_prophet])
        if selected_models == 0:
            st.error("⚠️ Please select at least one AI model!")
        elif selected_models == 1:
            st.warning("📢 Consider selecting more models for better accuracy!")
        elif selected_models >= 2:
            st.success("✅ Great choice! Multiple models provide better predictions.")
        
        st.markdown("---")
        
        # Advanced Settings (collapsed by default for beginners)
        st.markdown("### ⚙️ Step 4: Fine-tune (Optional)")
        
        with st.expander("🔧 Advanced Settings", expanded=False):
            st.markdown("*For experienced users - beginners can skip this*")
            
            prediction_days = st.slider(
                "📅 Prediction horizon (days):",
                7, 90, 30,
                help="How many days into the future to predict"
            )
            
            if use_lstm:
                lstm_epochs = st.slider(
                    "🧠 LSTM training intensity:",
                    10, 100, 50,
                    help="Higher values = better learning but slower processing"
                )
            else:
                lstm_epochs = 50  # Default value when LSTM not selected
            
            st.markdown("**📊 Risk Analysis Level:**")
            risk_tolerance = st.select_slider(
                "",
                options=["Conservative", "Moderate", "Aggressive"],
                value="Moderate",
                help="Affects confidence intervals in predictions"
            )
            
            risk_descriptions = {
                "Conservative": "🛡️ Safer predictions with wider confidence ranges",
                "Moderate": "⚖️ Balanced approach with reasonable confidence",
                "Aggressive": "🚀 Bold predictions with tighter confidence ranges"
            }
            st.markdown(f"*{risk_descriptions[risk_tolerance]}*")
        
        # Set default values when advanced settings are collapsed
        if 'prediction_days' not in locals():
            prediction_days = 30
        if 'lstm_epochs' not in locals():
            lstm_epochs = 50
        if 'risk_tolerance' not in locals():
            risk_tolerance = "Moderate"
        
        st.markdown("---")
        
        # Action Buttons with better UX
        st.markdown("### 🎬 Ready to Analyze?")
        
        # Pre-analysis validation
        can_analyze = True
        validation_messages = []
        
        if not any([use_linear, use_lstm, use_prophet]):
            can_analyze = False
            validation_messages.append("❌ Select at least one AI model")
        
        if not selected_stock:
            can_analyze = False
            validation_messages.append("❌ Choose a stock symbol")
        
        # Display validation messages
        if validation_messages:
            for msg in validation_messages:
                st.error(msg)
        else:
            st.success("✅ Ready to analyze!")
        
        # Action buttons
        col1, col2 = st.columns([2, 1])
        
        with col1:
            start_analysis = st.button(
                "🚀 Start AI Analysis",
                type="primary",
                use_container_width=True,
                disabled=not can_analyze,
                help="Begin the stock prediction analysis with your selected settings"
            )
        
        with col2:
            clear_cache = st.button(
                "🗑️ Reset",
                use_container_width=True,
                help="Clear cache and reset the application"
            )
        
        # Handle button clicks
        if clear_cache:
            st.cache_data.clear()
            st.success("🔄 Cache cleared!")
            st.rerun()
        
        if start_analysis:
            if can_analyze:
                # Show loading message
                with st.spinner('🔄 Initializing AI analysis...'):
                    st.session_state.run_analysis = True
                    st.session_state.selected_stock = selected_stock
                    st.session_state.selected_period = selected_period
                    st.session_state.models = {
                        'linear_regression': use_linear,
                        'lstm': use_lstm,
                        'prophet': use_prophet
                    }
                    st.session_state.prediction_days = prediction_days
                    st.session_state.lstm_epochs = lstm_epochs
                    st.session_state.risk_tolerance = risk_tolerance
                
                st.success(f"🎯 Analyzing {EXTENDED_INDIAN_STOCKS.get(selected_stock, selected_stock)}...")
        
        # Footer with helpful tips
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; padding: 10px; background-color: #0E1117; border-radius: 5px; margin-top: 10px;'>
            <small>
            💡 <strong>Pro Tip</strong>: Stock predictions are estimates based on historical data.<br>
            Always do your own research before making investment decisions!
            </small>
        </div>
        """, unsafe_allow_html=True)
        
    # Main content area
    if hasattr(st.session_state, 'run_analysis') and st.session_state.run_analysis:
        run_stock_analysis()
    else:
        show_welcome_screen()

def show_welcome_screen():
    """Display enhanced welcome screen"""
    
    # Hero section
    st.markdown("""
    <div class="success-box">
        <h2>🎯 Welcome to Advanced Stock Prediction!</h2>
        <p style="font-size: 1.1rem; margin-bottom: 1rem;">
            Harness the power of AI to predict Indian stock prices with multiple machine learning models.
        </p>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
            <div style="text-align: center;">
                <h3>📊 Linear Regression</h3>
                <p>Traditional statistical approach for trend analysis</p>
            </div>
            <div style="text-align: center;">
                <h3>🧠 LSTM Networks</h3>
                <p>Deep learning for complex pattern recognition</p>
            </div>
            <div style="text-align: center;">
                <h3>📈 Prophet</h3>
                <p>Facebook's time-series forecasting with seasonality</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_custom_metric("🏢 Available Stocks", f"{len(EXTENDED_INDIAN_STOCKS)}", color="#1f77b4"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_custom_metric("🤖 AI Models", "3", color="#ff7f0e"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_custom_metric("📊 Sectors Covered", "15+", color="#2ca02c"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_custom_metric("⚡ Prediction Speed", "< 60s", color="#d62728"), unsafe_allow_html=True)
    
    # Feature highlights
    st.markdown("### ✨ Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h4>🎯 Advanced Analytics</h4>
            <ul>
                <li>Multiple ML model comparison</li>
                <li>Technical indicator analysis</li>
                <li>Risk assessment metrics</li>
                <li>Trading signal generation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <h4>📊 Interactive Visualizations</h4>
            <ul>
                <li>Real-time price charts</li>
                <li>Prediction comparisons</li>
                <li>Technical indicators overlay</li>
                <li>Performance metrics dashboard</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Available stocks showcase
    st.markdown("### 📈 Featured Stocks")
    
    # Create tabs for different sectors
    tab1, tab2, tab3, tab4 = st.tabs(["🏦 Banking", "💻 IT", "🏭 Industrial", "🛒 Consumer"])
    
    with tab1:
        banking_stocks = {k: v for k, v in EXTENDED_INDIAN_STOCKS.items() if any(word in v.lower() for word in ['bank', 'finance'])}
        display_stock_grid(banking_stocks)
    
    with tab2:
        it_stocks = {k: v for k, v in EXTENDED_INDIAN_STOCKS.items() if any(word in v.lower() for word in ['tech', 'info', 'software', 'system'])}
        display_stock_grid(it_stocks)
    
    with tab3:
        industrial_stocks = {k: v for k, v in EXTENDED_INDIAN_STOCKS.items() if any(word in v.lower() for word in ['steel', 'cement', 'power', 'construction', 'larsen'])}
        display_stock_grid(industrial_stocks)
    
    with tab4:
        consumer_stocks = {k: v for k, v in EXTENDED_INDIAN_STOCKS.items() if any(word in v.lower() for word in ['consumer', 'unilever', 'itc', 'titan', 'paint'])}
        display_stock_grid(consumer_stocks)
    
    # Getting started guide
    st.markdown("### 🚀 Getting Started")
    
    st.markdown("""
    <div class="warning-box">
        <h4>📋 Quick Start Guide</h4>
        <ol>
            <li><strong>Select a Stock:</strong> Choose from 50+ Indian stocks or enter a custom symbol</li>
            <li><strong>Pick Time Period:</strong> Select from 3 months to 5 years of historical data</li>
            <li><strong>Choose Models:</strong> Enable the AI models you want to use</li>
            <li><strong>Configure Settings:</strong> Adjust prediction days and model parameters</li>
            <li><strong>Start Analysis:</strong> Click the "Start Analysis" button and wait for results</li>
        </ol>
        <p><strong>💡 Tip:</strong> For best results, use 1-2 years of data with all three models enabled!</p>
    </div>
    """, unsafe_allow_html=True)

def display_stock_grid(stocks_dict):
    """Display stocks in a grid format"""
    if not stocks_dict:
        st.info("No stocks available in this category.")
        return
    
    # Create a DataFrame for better display
    stock_data = []
    for symbol, name in list(stocks_dict.items())[:8]:  # Show first 8
        try:
            # Get basic info (cached to avoid repeated API calls)
            stock_info = get_basic_stock_info(symbol)
            stock_data.append({
                'Symbol': symbol,
                'Company': name[:30] + "..." if len(name) > 30 else name,
                'Current Price': stock_info.get('price', 'N/A'),
                'Change %': stock_info.get('change', 'N/A')
            })
        except:
            stock_data.append({
                'Symbol': symbol,
                'Company': name[:30] + "..." if len(name) > 30 else name,
                'Current Price': 'Loading...',
                'Change %': 'Loading...'
            })
    
    if stock_data:
        df = pd.DataFrame(stock_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_basic_stock_info(symbol):
    """Get basic stock information with caching"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="2d")
        if len(hist) >= 2:
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change_pct = ((current_price - prev_price) / prev_price) * 100
            return {
                'price': format_price(symbol, current_price),
                'change': f"{change_pct:+.1f}%"
            }
    except:
        pass
    return {'price': 'N/A', 'change': 'N/A'}

def run_stock_analysis():
    """Run the complete stock analysis with enhanced UI"""
    
    stock = st.session_state.selected_stock
    period = st.session_state.selected_period
    models = st.session_state.models
    prediction_days = st.session_state.prediction_days
    lstm_epochs = st.session_state.lstm_epochs
    risk_tolerance = st.session_state.get('risk_tolerance', 'Moderate')
    
    # Create analysis header
    st.markdown(f"""
    <div class="success-box">
        <h2>🔍 Analyzing {stock}</h2>
        <p>Running AI-powered analysis with {sum(models.values())} models over {period} period</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress tracking with enhanced UI
    progress_container = st.container()
    status_container = st.container()
    
    with progress_container:
        # Full-width progress bar and text
        progress_bar = st.progress(0)
        progress_text = st.empty()
    
    with status_container:
        status_text = st.empty()
        current_step = st.empty()
    
    try:
        # Initialize predictor
        current_step.markdown("**Step 1/7:** 🚀 Initializing AI system...")
        status_text.info("Setting up the prediction engine...")
        progress_bar.progress(10)
        progress_text.markdown("10%")
        time.sleep(1)
        
        predictor = IndianStockPredictor(symbol=stock, period=period)
        
        # Fetch data
        current_step.markdown("**Step 2/7:** 📡 Fetching market data...")
        status_text.info(f"Downloading {period} of historical data for {stock}...")
        progress_bar.progress(20)
        progress_text.markdown("20%")
        
        data = predictor.fetch_data()
        if data is None:
            st.error("❌ Failed to fetch data. Please check the stock symbol and try again.")
            return
        
        # Prepare data
        current_step.markdown("**Step 3/7:** 🔧 Engineering features...")
        status_text.info("Processing data and calculating technical indicators...")
        progress_bar.progress(30)
        progress_text.markdown("30%")
        
        predictor.prepare_data()
        
        # Display stock info with enhanced cards
        display_enhanced_stock_info(data, stock)
        
        # Train models
        results = {}
        current_progress = 40
        model_count = sum(models.values())
        progress_per_model = 40 // model_count if model_count > 0 else 0
        
        if models['linear_regression']:
            current_step.markdown("**Step 4/7:** 🤖 Training Linear Regression...")
            status_text.info("Training traditional statistical model...")
            progress_bar.progress(current_progress)
            progress_text.markdown(f"{current_progress}%")
            
            predictor.train_linear_regression()
            current_progress += progress_per_model
        
        if models['lstm']:
            current_step.markdown("**Step 5/7:** 🧠 Training LSTM Neural Network...")
            status_text.info(f"Training deep learning model ({lstm_epochs} epochs)...")
            progress_bar.progress(current_progress)
            progress_text.markdown(f"{current_progress}%")
            
            predictor.train_lstm(epochs=lstm_epochs)
            current_progress += progress_per_model
        
        if models['prophet']:
            current_step.markdown("**Step 6/7:** 📊 Training Prophet Model...")
            status_text.info("Training time-series forecasting model...")
            progress_bar.progress(current_progress)
            progress_text.markdown(f"{current_progress}%")
            
            predictor.train_prophet()
            current_progress += progress_per_model
        
        # Evaluate models
        current_step.markdown("**Step 7/7:** 📊 Evaluating models & generating predictions...")
        status_text.info("Comparing model performance and generating forecasts...")
        progress_bar.progress(90)
        progress_text.markdown("90%")
        
        results = predictor.evaluate_models()
        
        # Generate predictions
        future_pred, future_dates = predictor.predict_future(days=prediction_days)
        
        progress_bar.progress(100)
        progress_text.markdown("100%")
        current_step.markdown("**✅ Analysis Complete!**")
        status_text.success("🎉 All models trained successfully! Scroll down to see results.")
        
        time.sleep(2)
        
        # Clear progress indicators
        progress_container.empty()
        status_container.empty()
        
        # Display results with enhanced visualizations
        display_enhanced_results(predictor, results, future_pred, future_dates, risk_tolerance)
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        with st.expander("🔍 Error Details", expanded=False):
            st.exception(e)

def display_enhanced_stock_info(data, stock):
    """Display enhanced stock information with beautiful cards"""
    
    st.markdown("### 📊 Stock Overview")
    
    current_price = data['Close'].iloc[-1]
    prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
    price_change = current_price - prev_price
    price_change_pct = (price_change / prev_price) * 100
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        delta_text = f"{price_change:+.2f} ({price_change_pct:+.1f}%)"
        st.metric(
            "Current Price",
            format_price(stock, current_price),
            delta=delta_text
        )
    
    with col2:
        high_52w = data['High'].max()
        st.metric("52W High", f"₹{high_52w:.2f}")
    
    with col3:
        low_52w = data['Low'].min()
        st.metric("52W Low", f"₹{low_52w:.2f}")
    
    with col4:
        avg_volume = data['Volume'].tail(30).mean()
        current_volume = data['Volume'].iloc[-1]
        volume_change = ((current_volume - avg_volume) / avg_volume) * 100
        st.metric(
            "Volume", 
            f"{current_volume:,.0f}",
            delta=f"{volume_change:+.1f}% vs 30D avg"
        )
    
    with col5:
        volatility = data['Close'].pct_change().std() * np.sqrt(252) * 100
        st.metric("Annual Volatility", f"{volatility:.1f}%")
    
    # Price chart
    st.markdown("### 📈 Price Chart")
    
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Price'
    ))
    
    fig.update_layout(
        title=f'{stock} - Price History',
        yaxis_title=f"Price ({currency_symbol_for(stock)})",
        xaxis_title='Date',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_enhanced_results(predictor, results, future_pred, future_dates, risk_tolerance):
    """Display enhanced analysis results"""
    
    # Model comparison with enhanced styling
    st.markdown("### 🏆 Model Performance Comparison")
    
    if results:
        results_df = pd.DataFrame(results).T
        results_df = results_df.round(4)
        
        # Find best model
        best_model = results_df['RMSE'].idxmin()
        
        # Create performance cards
        col1, col2, col3 = st.columns(3)
        
        for i, (model_name, metrics) in enumerate(results.items()):
            col = [col1, col2, col3][i % 3]
            
            with col:
                is_best = model_name == best_model
                card_color = "#2ca02c" if is_best else "#1f77b4"
                crown = "👑 " if is_best else ""
                
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, {card_color}20, {card_color}40);
                    padding: 1.5rem;
                    border-radius: 15px;
                    border: 2px solid {card_color};
                    margin: 0.5rem 0;
                ">
                    <h3 style="color: {card_color}; margin: 0;">{crown}{model_name.upper()}</h3>
                    <hr style="border-color: {card_color};">
                    <p><strong>RMSE:</strong> {currency_symbol_for(predictor.symbol)}{metrics['RMSE']:.2f}</p>
                    <p><strong>R²:</strong> {metrics['R²']:.4f}</p>
                    <p><strong>MAPE:</strong> {metrics['MAPE']:.1f}%</p>
                    <p><strong>Direction Accuracy:</strong> {metrics['Directional_Accuracy']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed comparison table
        with st.expander("📊 Detailed Model Comparison", expanded=False):
            st.dataframe(results_df, use_container_width=True)
    
    # Predictions visualization
    st.markdown("### 📊 Model Predictions vs Actual")
    plot_enhanced_predictions(predictor)
    
    # Future predictions
    st.markdown("### 🔮 Future Price Predictions")
    display_enhanced_future_predictions(future_pred, future_dates, predictor, risk_tolerance)
    
    # Technical analysis
    st.markdown("### 📈 Technical Analysis")
    plot_enhanced_technical_indicators(predictor)
    
    # Trading signals
    st.markdown("### 🎯 Trading Signals & Recommendations")
    display_enhanced_trading_signals(predictor, risk_tolerance)
    
    # Download section
    st.markdown("### 💾 Export Results")
    provide_download_options(predictor, future_pred, future_dates)

def plot_enhanced_predictions(predictor):
    """Create enhanced prediction plots"""
    
    tabs = st.tabs([f"📊 {name.upper()}" for name in predictor.predictions.keys()])
    
    for i, (model_name, pred_data) in enumerate(predictor.predictions.items()):
        with tabs[i]:
            fig = go.Figure()
            
            # Actual prices
            fig.add_trace(go.Scatter(
                x=pred_data['test_dates'],
                y=pred_data['test_actual'],
                mode='lines',
                name='Actual Price',
                line=dict(color='#2E86AB', width=3),
                hovertemplate=f"<b>Actual</b><br>Date: %{{x}}<br>Price: {currency_symbol_for(predictor.symbol)}%{{y:.2f}}<extra></extra>"
            ))
            
            # Predicted prices
            fig.add_trace(go.Scatter(
                x=pred_data['test_dates'],
                y=pred_data['test_pred'],
                mode='lines',
                name='Predicted Price',
                line=dict(color='#F24236', width=3, dash='dash'),
                hovertemplate=f"<b>Predicted</b><br>Date: %{{x}}<br>Price: {currency_symbol_for(predictor.symbol)}%{{y:.2f}}<extra></extra>"
            ))
            
            # Calculate metrics for display
            rmse = np.sqrt(np.mean((pred_data['test_actual'] - pred_data['test_pred'])**2))
            r2 = 1 - (np.sum((pred_data['test_actual'] - pred_data['test_pred'])**2) / 
                      np.sum((pred_data['test_actual'] - np.mean(pred_data['test_actual']))**2))
            mape = np.mean(np.abs((pred_data['test_actual'] - pred_data['test_pred']) / pred_data['test_actual'])) * 100
            
            fig.update_layout(
                title=f"{model_name.upper()} - Prediction Performance<br><sub>RMSE: {currency_symbol_for(predictor.symbol)}{rmse:.2f} | R²: {r2:.4f} | MAPE: {mape:.1f}%</sub>",
                xaxis_title='Date',
                yaxis_title=f"Price ({currency_symbol_for(predictor.symbol)})",
                hovermode='x unified',
                template='plotly_white',
                height=500,
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)

def display_enhanced_future_predictions(future_pred, future_dates, predictor, risk_tolerance):
    """Display enhanced future predictions"""
    
    if not future_pred:
        st.warning("⚠️ No future predictions available.")
        return
    
    # Create predictions dataframe
    pred_df = pd.DataFrame(future_pred, index=future_dates)
    current_price = predictor.processed_data['Close'].iloc[-1]
    
    # Interactive plot
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, (model_name, predictions) in enumerate(future_pred.items()):
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=predictions,
            mode='lines+markers',
            name=model_name,
            line=dict(width=3, color=colors[i % len(colors)]),
            marker=dict(size=6),
            hovertemplate=f"<b>{model_name}</b><br>Date: %{{x}}<br>Price: {currency_symbol_for(predictor.symbol)}%{{y:.2f}}<extra></extra>"
        ))
    
    # Add current price line
    fig.add_hline(
        y=current_price, 
        line_dash="dot", 
        line_color="gray",
        annotation_text=f"Current Price: {currency_symbol_for(predictor.symbol)}{current_price:.2f}",
        annotation_position="top right"
    )
    
    fig.update_layout(
        title='🔮 Future Price Predictions',
        xaxis_title='Date',
        yaxis_title=f'Predicted Price ({currency_symbol_for(predictor.symbol)})',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Predictions summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Prediction Summary")
        
        # Calculate average prediction and confidence
        if len(future_pred) > 1:
            avg_predictions = []
            for i in range(len(list(future_pred.values())[0])):
                day_preds = [model_preds[i] for model_preds in future_pred.values()]
                avg_predictions.append(np.mean(day_preds))
            
            # Show key predictions
            pred_summary = []
            key_days = [1, 7, 15, 30] if len(avg_predictions) >= 30 else [1, 7, min(15, len(avg_predictions)-1)]
            
            for day in key_days:
                if day <= len(avg_predictions):
                    pred_price = avg_predictions[day-1]
                    change = ((pred_price - current_price) / current_price) * 100
                    pred_summary.append({
                        'Period': f'{day} Day{"s" if day > 1 else ""}',
                        'Avg Prediction': f'₹{pred_price:.2f}',
                        'Change': f'{change:+.1f}%',
                        'Direction': '📈' if change > 0 else '📉' if change < 0 else '➡️'
                    })
            
            if pred_summary:
                summary_df = pd.DataFrame(pred_summary)
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### 💡 Investment Recommendation")
        
        # Calculate consensus
        if len(future_pred) > 1:
            # Get 7-day and 30-day predictions
            day_7_preds = [preds[6] if len(preds) > 6 else preds[-1] for preds in future_pred.values()]
            day_30_preds = [preds[29] if len(preds) > 29 else preds[-1] for preds in future_pred.values()]
            
            avg_7_change = np.mean([(p - current_price) / current_price * 100 for p in day_7_preds])
            avg_30_change = np.mean([(p - current_price) / current_price * 100 for p in day_30_preds])
            
            # Determine recommendation based on risk tolerance
            risk_multiplier = {'Conservative': 0.5, 'Moderate': 1.0, 'Aggressive': 1.5}[risk_tolerance]
            threshold = 2.0 * risk_multiplier
            
            if avg_7_change > threshold and avg_30_change > threshold:
                recommendation = "🟢 **BUY**"
                reason = f"Models predict {avg_30_change:.1f}% growth over 30 days"
                color = "#2ca02c"
            elif avg_7_change < -threshold and avg_30_change < -threshold:
                recommendation = "🔴 **SELL**"
                reason = f"Models predict {avg_30_change:.1f}% decline over 30 days"
                color = "#d62728"
            else:
                recommendation = "🟡 **HOLD**"
                reason = "Mixed signals or sideways movement predicted"
                color = "#ff7f0e"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {color}20, {color}40);
                padding: 1.5rem;
                border-radius: 15px;
                border: 2px solid {color};
                text-align: center;
            ">
                <h3 style="color: {color}; margin: 0;">{recommendation}</h3>
                <p style="margin: 0.5rem 0;"><strong>Risk Level:</strong> {risk_tolerance}</p>
                <p style="margin: 0;"><em>{reason}</em></p>
            </div>
            """, unsafe_allow_html=True)
        
        # Model consensus
        st.markdown("#### 🤝 Model Consensus")
        consensus_data = []
        for model_name, predictions in future_pred.items():
            week_change = ((predictions[6] if len(predictions) > 6 else predictions[-1]) - current_price) / current_price * 100
            trend = "Bullish" if week_change > 1 else "Bearish" if week_change < -1 else "Neutral"
            consensus_data.append({
                'Model': model_name,
                '7D Change': f'{week_change:+.1f}%',
                'Trend': trend
            })
        
        if consensus_data:
            consensus_df = pd.DataFrame(consensus_data)
            st.dataframe(consensus_df, use_container_width=True, hide_index=True)
    
    # Detailed predictions table
    with st.expander("📋 Detailed Daily Predictions", expanded=False):
        display_df = pred_df.head(14).round(2)  # Show first 14 days
        display_df.index = display_df.index.date
        
        # Add change columns
        for col in display_df.columns:
            change_col = f'{col}_Change'
            display_df[change_col] = ((display_df[col] - current_price) / current_price * 100).round(1)
        
        st.dataframe(display_df, use_container_width=True)

def plot_enhanced_technical_indicators(predictor):
    """Plot enhanced technical indicators"""
    
    if predictor.processed_data is None:
        return
    
    df = predictor.processed_data.tail(200)  # Last 200 days
    
    # Create subplots
    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=('Price & Moving Averages', 'RSI', 'MACD', 'Volume'),
        vertical_spacing=0.08,
        row_heights=[0.4, 0.2, 0.2, 0.2]
    )
    
    # Price and Moving Averages
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'], 
        name='Close Price', 
        line=dict(width=2, color='#1f77b4')
    ), row=1, col=1)
    
    if 'MA_20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MA_20'], 
            name='MA 20', 
            line=dict(width=1, color='#ff7f0e'),
            opacity=0.8
        ), row=1, col=1)
    
    if 'MA_50' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MA_50'], 
            name='MA 50', 
            line=dict(width=1, color='#2ca02c'),
            opacity=0.8
        ), row=1, col=1)
    
    # Bollinger Bands
    if all(col in df.columns for col in ['BB_upper', 'BB_lower', 'BB_middle']):
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_upper'], 
            name='BB Upper',
            line=dict(width=1, color='rgba(128,128,128,0.5)'),
            showlegend=False
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_lower'], 
            name='BB Lower',
            line=dict(width=1, color='rgba(128,128,128,0.5)'),
            fill='tonexty',
            fillcolor='rgba(128,128,128,0.1)',
            showlegend=False
        ), row=1, col=1)
    
    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['RSI'], 
            name='RSI', 
            line=dict(color='purple')
        ), row=2, col=1)
        
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.7, row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.7, row=2, col=1)
    
    # MACD
    if all(col in df.columns for col in ['MACD', 'MACD_signal']):
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MACD'], 
            name='MACD', 
            line=dict(color='blue')
        ), row=3, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MACD_signal'], 
            name='Signal', 
            line=dict(color='red')
        ), row=3, col=1)
        
        if 'MACD_histogram' in df.columns:
            colors = ['green' if val >= 0 else 'red' for val in df['MACD_histogram']]
            fig.add_trace(go.Bar(
                x=df.index, y=df['MACD_histogram'], 
                name='MACD Histogram',
                marker_color=colors,
                opacity=0.6
            ), row=3, col=1)
    
    # Volume
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'], 
        name='Volume',
        marker_color='lightblue',
        opacity=0.7
    ), row=4, col=1)
    
    if 'Volume_MA' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Volume_MA'], 
            name='Volume MA',
            line=dict(color='red')
        ), row=4, col=1)
    
    fig.update_layout(
        height=1000, 
        template='plotly_white', 
        showlegend=True,
        title_text="Technical Indicators Analysis"
    )
    
    # Update y-axes
    fig.update_yaxes(title_text=f"Price ({currency_symbol_for(predictor.symbol)})", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="Volume", row=4, col=1)
    
    st.plotly_chart(fig, use_container_width=True)

def display_enhanced_trading_signals(predictor, risk_tolerance):
    """Display enhanced trading signals"""
    
    try:
        signals = predictor.generate_trading_signals()
        recent_signal = signals.iloc[-1] if len(signals) > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Current signal
            if recent_signal == 1:
                signal_text = "🟢 **BUY**"
                signal_color = "#2ca02c"
                signal_desc = "Technical indicators suggest buying opportunity"
            elif recent_signal == -1:
                signal_text = "🔴 **SELL**"
                signal_color = "#d62728"
                signal_desc = "Technical indicators suggest selling opportunity"
            else:
                signal_text = "🟡 **HOLD**"
                signal_color = "#ff7f0e"
                signal_desc = "No clear trading signal from technical indicators"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {signal_color}20, {signal_color}40);
                padding: 1.5rem;
                border-radius: 15px;
                border: 2px solid {signal_color};
                text-align: center;
            ">
                <h3 style="color: {signal_color}; margin: 0;">Current Signal</h3>
                <h2 style="color: {signal_color}; margin: 0.5rem 0;">{signal_text}</h2>
                <p style="margin: 0;"><em>{signal_desc}</em></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Signal distribution
            if len(signals) > 0:
                signal_counts = signals.value_counts()
                signal_labels = {1: 'Buy Signals', -1: 'Sell Signals', 0: 'Hold/Neutral'}
                
                fig = px.pie(
                    values=signal_counts.values,
                    names=[signal_labels.get(idx, f'Signal {idx}') for idx in signal_counts.index],
                    title="Historical Signal Distribution",
                    color_discrete_map={
                        'Buy Signals': '#2ca02c',
                        'Sell Signals': '#d62728',
                        'Hold/Neutral': '#ff7f0e'
                    }
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Recent signals
            st.markdown("#### 📅 Recent Signals")
            if len(signals) > 0:
                recent_signals = signals.tail(10)
                signal_df = pd.DataFrame({
                    'Date': recent_signals.index.date,
                    'Signal': recent_signals.map({1: '🟢 Buy', -1: '🔴 Sell', 0: '🟡 Hold'})
                })
                st.dataframe(signal_df, use_container_width=True, hide_index=True)
            else:
                st.info("No trading signals generated")
        
        # Trading strategy suggestions
        st.markdown("#### 💡 Trading Strategy Suggestions")
        
        strategy_col1, strategy_col2 = st.columns(2)
        
        with strategy_col1:
            st.markdown(f"""
            <div class="info-box">
                <h4>📊 For {risk_tolerance} Investors</h4>
                <ul>
                    <li><strong>Entry Strategy:</strong> {'Wait for stronger confirmation' if risk_tolerance == 'Conservative' else 'Consider gradual position building' if risk_tolerance == 'Moderate' else 'Can take larger positions on signals'}</li>
                    <li><strong>Stop Loss:</strong> {2 if risk_tolerance == 'Conservative' else 3 if risk_tolerance == 'Moderate' else 5}% below entry</li>
                    <li><strong>Position Size:</strong> {'Small (1-2% of portfolio)' if risk_tolerance == 'Conservative' else 'Medium (3-5% of portfolio)' if risk_tolerance == 'Moderate' else 'Large (5-10% of portfolio)'}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with strategy_col2:
            # Risk metrics
            if len(signals) > 0:
                buy_signals = (signals == 1).sum()
                sell_signals = (signals == -1).sum()
                total_signals = buy_signals + sell_signals
                
                if total_signals > 0:
                    signal_frequency = len(signals) / total_signals if total_signals > 0 else 0
                    
                    st.markdown(f"""
                    <div class="warning-box">
                        <h4>⚠️ Risk Assessment</h4>
                        <p><strong>Signal Frequency:</strong> 1 signal every {signal_frequency:.0f} days</p>
                        <p><strong>Buy/Sell Ratio:</strong> {buy_signals}/{sell_signals}</p>
                        <p><strong>Activity Level:</strong> {'High' if signal_frequency < 10 else 'Medium' if signal_frequency < 30 else 'Low'}</p>
                        <p><strong>Recommendation:</strong> {'Active monitoring required' if signal_frequency < 10 else 'Moderate monitoring' if signal_frequency < 30 else 'Long-term holding suitable'}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error generating trading signals: {e}")

def provide_download_options(predictor, future_pred, future_dates):
    """Provide download options for results"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download predictions
        if future_pred:
            pred_df = pd.DataFrame(future_pred, index=future_dates)
            csv = pred_df.to_csv()
            st.download_button(
                label="📥 Download Predictions",
                data=csv,
                file_name=f"{predictor.symbol}_predictions.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        # Download processed data
        if predictor.processed_data is not None:
            processed_csv = predictor.processed_data.to_csv()
            st.download_button(
                label="📥 Download Processed Data",
                data=processed_csv,
                file_name=f"{predictor.symbol}_processed_data.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col3:
        # Download trading signals
        try:
            signals = predictor.generate_trading_signals()
            if len(signals) > 0:
                signals_df = pd.DataFrame({
                    'Date': signals.index,
                    'Signal': signals.values,
                    'Signal_Text': signals.map({1: 'Buy', -1: 'Sell', 0: 'Hold'})
                })
                signals_csv = signals_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Trading Signals",
                    data=signals_csv,
                    file_name=f"{predictor.symbol}_trading_signals.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        except:
            st.info("Trading signals not available")

if __name__ == "__main__":
    main()
