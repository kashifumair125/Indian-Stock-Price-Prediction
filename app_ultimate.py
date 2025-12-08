"""
🚀 ULTIMATE STOCK MARKET ANALYSIS PLATFORM
Professional-Grade Trading & Investment Platform

Features:
- Multi-Market Support (Indian NSE, US, Global)
- AI-Powered Predictions
- Real-Time Data
- Backtesting Engine
- News Sentiment Analysis
- Smart Alerts System
- Fundamental Analysis
- Portfolio Management

Author: Umair Kashif
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import time
import sys

# Add modules
sys.path.append('.')
try:
    from stock_predictor import IndianStockPredictor
    from backtesting_engine import BacktestingEngine
    from news_sentiment import NewsSentimentAnalyzer
    from alerts_system import AlertsSystem
    from fundamental_data import FundamentalAnalyzer
except ImportError as e:
    st.error(f"Module import error: {e}")

# Page config
st.set_page_config(
    page_title="Ultimate Stock Analysis Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SESSION STATE ====================
def init_session_state():
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = ['TCS.NS', 'RELIANCE.NS', 'AAPL', 'GOOGL']
    if 'alerts_system' not in st.session_state:
        st.session_state.alerts_system = AlertsSystem()
    if 'market_region' not in st.session_state:
        st.session_state.market_region = 'India (NSE)'

init_session_state()

# ==================== STOCK DATABASES ====================
INDIAN_STOCKS = {
    'TCS.NS': {'name': 'Tata Consultancy Services', 'sector': 'IT', 'region': 'India'},
    'INFY.NS': {'name': 'Infosys Limited', 'sector': 'IT', 'region': 'India'},
    'RELIANCE.NS': {'name': 'Reliance Industries', 'sector': 'Energy', 'region': 'India'},
    'HDFCBANK.NS': {'name': 'HDFC Bank', 'sector': 'Banking', 'region': 'India'},
    'ICICIBANK.NS': {'name': 'ICICI Bank', 'sector': 'Banking', 'region': 'India'},
    'SBIN.NS': {'name': 'State Bank of India', 'sector': 'Banking', 'region': 'India'},
    'WIPRO.NS': {'name': 'Wipro Limited', 'sector': 'IT', 'region': 'India'},
    'ITC.NS': {'name': 'ITC Limited', 'sector': 'FMCG', 'region': 'India'},
}

US_STOCKS = {
    'AAPL': {'name': 'Apple Inc.', 'sector': 'Technology', 'region': 'US'},
    'GOOGL': {'name': 'Alphabet Inc.', 'sector': 'Technology', 'region': 'US'},
    'MSFT': {'name': 'Microsoft Corporation', 'sector': 'Technology', 'region': 'US'},
    'AMZN': {'name': 'Amazon.com Inc.', 'sector': 'Consumer', 'region': 'US'},
    'TSLA': {'name': 'Tesla Inc.', 'sector': 'Automotive', 'region': 'US'},
    'META': {'name': 'Meta Platforms Inc.', 'sector': 'Technology', 'region': 'US'},
    'NVDA': {'name': 'NVIDIA Corporation', 'sector': 'Technology', 'region': 'US'},
    'JPM': {'name': 'JPMorgan Chase & Co.', 'sector': 'Banking', 'region': 'US'},
}

GLOBAL_STOCKS = {
    **INDIAN_STOCKS,
    **US_STOCKS,
    '0700.HK': {'name': 'Tencent Holdings', 'sector': 'Technology', 'region': 'HK'},
    'BABA': {'name': 'Alibaba Group', 'sector': 'E-commerce', 'region': 'China'},
    'SAP': {'name': 'SAP SE', 'sector': 'Software', 'region': 'Germany'},
}

def get_stocks_by_region(region):
    if region == 'India (NSE)':
        return INDIAN_STOCKS
    elif region == 'US (NYSE/NASDAQ)':
        return US_STOCKS
    else:
        return GLOBAL_STOCKS

# ==================== THEME CSS - PROPERLY FIXED ====================
def apply_custom_css():
    theme = st.session_state.theme

    if theme == 'dark':
        # Dark theme colors
        bg_primary = "#0E1117"
        bg_secondary = "#262730"
        text_primary = "#FAFAFA"
        text_secondary = "#B0B0B0"
        border_color = "#404040"
        accent_color = "#667eea"
    else:
        # Light theme colors
        bg_primary = "#FFFFFF"
        bg_secondary = "#F8F9FA"
        text_primary = "#1E1E1E"
        text_secondary = "#505050"
        border_color = "#DEDEDE"
        accent_color = "#4facfe"

    css = f"""
    <style>
        /* Force theme colors */
        .stApp, .main, .block-container {{
            background-color: {bg_primary} !important;
        }}

        /* All text elements */
        .stApp, .stApp * {{
            color: {text_primary} !important;
        }}

        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: {text_primary} !important;
        }}

        /* Markdown */
        .stMarkdown, .stMarkdown * {{
            color: {text_primary} !important;
        }}

        /* Metrics */
        [data-testid="stMetricValue"] {{
            color: {text_primary} !important;
        }}

        [data-testid="stMetricLabel"] {{
            color: {text_secondary} !important;
        }}

        /* Dataframes */
        .dataframe {{
            background-color: {bg_secondary} !important;
            color: {text_primary} !important;
        }}

        .dataframe th {{
            background-color: {accent_color} !important;
            color: white !important;
        }}

        .dataframe td {{
            background-color: {bg_secondary} !important;
            color: {text_primary} !important;
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {bg_secondary} !important;
        }}

        [data-testid="stSidebar"] * {{
            color: {text_primary} !important;
        }}

        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {accent_color}, #764ba2) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: transform 0.2s !important;
        }}

        .stButton > button:hover {{
            transform: translateY(-2px) !important;
        }}

        /* Input fields */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stNumberInput > div > div > input {{
            background-color: {bg_secondary} !important;
            color: {text_primary} !important;
            border: 1px solid {border_color} !important;
        }}

        /* Expanders */
        .streamlit-expanderHeader {{
            background-color: {bg_secondary} !important;
            color: {text_primary} !important;
        }}

        .streamlit-expanderContent {{
            background-color: {bg_primary} !important;
        }}

        /* Radio buttons */
        .stRadio > label {{
            color: {text_primary} !important;
        }}

        /* Checkboxes */
        .stCheckbox > label {{
            color: {text_primary} !important;
        }}

        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}

        /* Custom cards */
        .custom-card {{
            background: {bg_secondary};
            padding: 20px;
            border-radius: 10px;
            border: 1px solid {border_color};
            margin: 10px 0;
        }}

        /* Success/Warning/Error boxes */
        .stSuccess, .stWarning, .stError, .stInfo {{
            color: white !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

apply_custom_css()

# ==================== UTILITY FUNCTIONS ====================
@st.cache_data(ttl=30)
def get_live_quote(symbol):
    try:
        t = yf.Ticker(symbol)
        fi = getattr(t, 'fast_info', {}) or {}
        price = fi.get('last_price') or fi.get('lastPrice')
        prev_close = fi.get('previous_close') or fi.get('previousClose')

        if price is None:
            hist = t.history(period="1d", interval="1m")
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
                prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else price

        data = {
            'price': float(price) if price else None,
            'prev_close': float(prev_close) if prev_close else None,
            'change_pct': None
        }

        if data['price'] and data['prev_close']:
            data['change_pct'] = ((data['price'] - data['prev_close']) / data['prev_close']) * 100

        return data
    except:
        return {'price': None, 'prev_close': None, 'change_pct': None}

def format_large_number(num):
    if num >= 1e12:
        return f"${num/1e12:.2f}T"
    elif num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    else:
        return f"${num:,.2f}"

# ==================== PAGE: DASHBOARD ====================
def render_dashboard():
    st.title("📊 Market Dashboard")

    # Quick stats
    col1, col2, col3, col4 = st.columns(4)

    stocks = get_stocks_by_region(st.session_state.market_region)

    with col1:
        st.metric("Total Stocks", len(stocks), "Tracked")

    with col2:
        st.metric("Watchlist", len(st.session_state.watchlist), "Active")

    with col3:
        portfolio_value = sum([p.get('current_value', 0) for p in st.session_state.portfolio])
        st.metric("Portfolio Value", f"${portfolio_value:,.2f}")

    with col4:
        active_alerts = len(st.session_state.alerts_system.get_active_alerts())
        st.metric("Active Alerts", active_alerts, "Monitoring")

    # Live ticker
    st.markdown("### 📊 Live Market Ticker")
    ticker_cols = st.columns(min(len(st.session_state.watchlist), 5))

    for idx, symbol in enumerate(st.session_state.watchlist[:5]):
        quote = get_live_quote(symbol)
        with ticker_cols[idx]:
            if quote and quote.get('price'):
                stock_info = stocks.get(symbol, {'name': symbol})
                st.metric(
                    label=stock_info['name'][:15],
                    value=f"${quote['price']:.2f}",
                    delta=f"{quote.get('change_pct', 0):+.2f}%"
                )

    # Market heatmap
    st.markdown("### 🔥 Market Heatmap by Sector")

    with st.spinner("Loading heatmap..."):
        sector_data = {}
        for symbol, info in stocks.items():
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
                color_continuous_midpoint=0
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE: BACKTESTING ====================
def render_backtesting():
    st.title("📊 Strategy Backtesting")

    st.markdown("""
    Test trading strategies on historical data and analyze performance.
    """)

    col1, col2 = st.columns([2, 1])

    with col1:
        stocks = get_stocks_by_region(st.session_state.market_region)
        selected_stock = st.selectbox("Select Stock", list(stocks.keys()))

    with col2:
        initial_capital = st.number_input("Initial Capital ($)", min_value=1000, value=100000, step=1000)

    col1, col2, col3 = st.columns(3)

    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))

    with col2:
        end_date = st.date_input("End Date", value=datetime.now())

    with col3:
        strategy = st.selectbox(
            "Trading Strategy",
            ['MA_CROSSOVER', 'RSI_OVERSOLD', 'MACD_CROSSOVER', 'BOLLINGER_BANDS']
        )

    if st.button("🚀 Run Backtest", type="primary"):
        with st.spinner("Running backtest..."):
            try:
                engine = BacktestingEngine(
                    selected_stock,
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d'),
                    initial_capital
                )

                engine.load_data()
                trades, equity = engine.run_strategy(strategy)
                metrics = engine.calculate_metrics()

                # Display metrics
                st.markdown("### 📊 Performance Metrics")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Return", f"{metrics['Total Return %']:.2f}%")

                with col2:
                    st.metric("Win Rate", f"{metrics['Win Rate %']:.1f}%")

                with col3:
                    st.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")

                with col4:
                    st.metric("Max Drawdown", f"{metrics['Max Drawdown %']:.2f}%")

                # Results chart
                st.markdown("### 📈 Backtest Results")
                fig = engine.plot_results()
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                # Detailed metrics
                with st.expander("📋 Detailed Metrics"):
                    metrics_df = pd.DataFrame([metrics]).T
                    metrics_df.columns = ['Value']
                    st.dataframe(metrics_df, use_container_width=True)

                # Trade list
                st.markdown("### 📝 Trade List")
                trades_df = engine.get_trade_list()
                if not trades_df.empty:
                    st.dataframe(trades_df, use_container_width=True)

            except Exception as e:
                st.error(f"Backtest error: {str(e)}")

# ==================== PAGE: NEWS & SENTIMENT ====================
def render_news_sentiment():
    st.title("📰 News & Sentiment Analysis")

    stocks = get_stocks_by_region(st.session_state.market_region)
    selected_stock = st.selectbox("Select Stock", list(stocks.keys()))

    if st.button("📰 Fetch News & Analyze Sentiment", type="primary"):
        with st.spinner("Fetching news and analyzing sentiment..."):
            try:
                analyzer = NewsSentimentAnalyzer(selected_stock)
                sentiment_df = analyzer.analyze_sentiment()
                overall = analyzer.get_overall_sentiment()

                # Overall sentiment
                st.markdown("### 😊 Overall Sentiment")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Sentiment",
                        f"{overall['sentiment_label']} {overall['emoji']}",
                        f"Score: {overall['avg_sentiment']:.2f}"
                    )

                with col2:
                    st.metric("Positive", overall['positive_count'], "articles")

                with col3:
                    st.metric("Neutral", overall['neutral_count'], "articles")

                with col4:
                    st.metric("Negative", overall['negative_count'], "articles")

                # Sentiment distribution
                st.markdown("### 📊 Sentiment Distribution")

                dist_data = overall['sentiment_distribution']
                fig = px.pie(
                    values=list(dist_data.values()),
                    names=list(dist_data.keys()),
                    color_discrete_map={'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'}
                )
                st.plotly_chart(fig, use_container_width=True)

                # News articles
                st.markdown("### 📰 Recent News")
                if not sentiment_df.empty:
                    for _, row in sentiment_df.head(10).iterrows():
                        with st.expander(f"{row['emoji']} {row['title']}"):
                            st.markdown(f"**Publisher:** {row['publisher']}")
                            st.markdown(f"**Published:** {row['published']}")
                            st.markdown(f"**Sentiment:** {row['sentiment']} (Score: {row['sentiment_score']:.2f})")
                            if row.get('link'):
                                st.markdown(f"[Read Article]({row['link']})")

            except Exception as e:
                st.error(f"Sentiment analysis error: {str(e)}")
                st.info("Note: News sentiment requires TextBlob. Install with: pip install textblob")

# ==================== PAGE: ALERTS ====================
def render_alerts_dashboard():
    st.title("🔔 Alerts Dashboard")

    tab1, tab2 = st.tabs(["Create Alert", "Active Alerts"])

    with tab1:
        st.markdown("### ➕ Create New Alert")

        stocks = get_stocks_by_region(st.session_state.market_region)

        col1, col2 = st.columns(2)

        with col1:
            alert_symbol = st.selectbox("Stock", list(stocks.keys()))
            alert_type = st.selectbox(
                "Alert Type",
                ['price', 'change_pct', 'volume', 'rsi']
            )

        with col2:
            condition = st.selectbox(
                "Condition",
                ['above', 'below', 'equals']
            )
            value = st.number_input("Threshold Value", value=100.0)

        message = st.text_input("Custom Message (optional)")

        if st.button("➕ Create Alert", type="primary"):
            alert = st.session_state.alerts_system.add_alert(
                alert_symbol, alert_type, condition, value, message
            )
            st.success(f"✅ Alert created! ID: {alert['id']}")

    with tab2:
        st.markdown("### 📋 Active Alerts")

        if st.button("🔍 Check Alerts Now"):
            triggered = st.session_state.alerts_system.check_alerts()
            if triggered:
                for alert in triggered:
                    st.success(f"🔔 {alert['message']}")
            else:
                st.info("No alerts triggered")

        alerts_df = st.session_state.alerts_system.get_alerts_dataframe()

        if not alerts_df.empty:
            st.dataframe(alerts_df, use_container_width=True)
        else:
            st.info("No active alerts. Create one above!")

# ==================== PAGE: FUNDAMENTALS ====================
def render_fundamentals():
    st.title("💼 Fundamental Analysis")

    stocks = get_stocks_by_region(st.session_state.market_region)
    selected_stock = st.selectbox("Select Stock", list(stocks.keys()))

    if st.button("📊 Analyze Fundamentals", type="primary"):
        with st.spinner("Fetching fundamental data..."):
            try:
                analyzer = FundamentalAnalyzer(selected_stock)

                # Company profile
                profile = analyzer.get_company_profile()

                st.markdown("### 🏢 Company Profile")
                st.markdown(f"**{profile['Company Name']}**")
                st.markdown(f"**Sector:** {profile['Sector']} | **Industry:** {profile['Industry']}")
                st.markdown(f"**Country:** {profile['Country']}")

                if profile.get('Business Summary'):
                    with st.expander("📖 Business Summary"):
                        st.write(profile['Business Summary'])

                # Valuation grade
                grade = analyzer.get_valuation_grade()

                st.markdown("### ⭐ Valuation Grade")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Grade", grade['grade'], grade['label'])

                with col2:
                    st.metric("Score", f"{grade['score']:.1f}/100")

                with col3:
                    st.markdown(f"**Color:** {grade['color'].upper()}")

                st.markdown("**Reasons:**")
                for reason in grade['reasons']:
                    st.markdown(f"- {reason}")

                # Key metrics
                st.markdown("### 📊 Key Metrics")

                metrics = analyzer.get_key_metrics()

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**Valuation**")
                    st.write(f"P/E Ratio: {metrics['P/E Ratio']}")
                    st.write(f"P/B Ratio: {metrics['P/B Ratio']}")
                    st.write(f"P/S Ratio: {metrics['P/S Ratio']}")

                with col2:
                    st.markdown("**Profitability**")
                    st.write(f"ROE: {metrics['ROE']}")
                    st.write(f"ROA: {metrics['ROA']}")
                    st.write(f"Profit Margin: {metrics['Profit Margin']}")

                with col3:
                    st.markdown("**Financial Health**")
                    st.write(f"Debt/Equity: {metrics['Debt/Equity']}")
                    st.write(f"Current Ratio: {metrics['Current Ratio']}")
                    st.write(f"Quick Ratio: {metrics['Quick Ratio']}")

                # Financial highlights
                highlights = analyzer.get_financial_highlights()

                with st.expander("💰 Financial Highlights"):
                    col1, col2 = st.columns(2)

                    with col1:
                        for key in list(highlights.keys())[:5]:
                            st.write(f"**{key}:** {highlights[key]}")

                    with col2:
                        for key in list(highlights.keys())[5:]:
                            st.write(f"**{key}:** {highlights[key]}")

            except Exception as e:
                st.error(f"Fundamental analysis error: {str(e)}")

# ==================== MAIN APP ====================
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Navigation")

        # Market region selector
        st.session_state.market_region = st.selectbox(
            "📍 Market Region",
            ['India (NSE)', 'US (NYSE/NASDAQ)', 'Global Markets']
        )

        st.markdown("---")

        # Page selection
        pages = {
            "📊 Dashboard": render_dashboard,
            "📈 Advanced Charts": lambda: st.info("Use Charts page"),
            "🤖 AI Analysis": lambda: st.info("Use AI Analysis page"),
            "🔍 Stock Screener": lambda: st.info("Use Screener page"),
            "💼 Portfolio": lambda: st.info("Use Portfolio page"),
            "📊 Backtesting": render_backtesting,
            "📰 News & Sentiment": render_news_sentiment,
            "🔔 Alerts": render_alerts_dashboard,
            "💼 Fundamentals": render_fundamentals
        }

        page = st.radio("Select Page", list(pages.keys()))

        # Theme toggle
        st.markdown("---")
        theme_icon = "☀️" if st.session_state.theme == 'dark' else "🌙"
        if st.button(f"{theme_icon} Toggle Theme", use_container_width=True):
            st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            st.rerun()

        # Watchlist
        st.markdown("---")
        st.markdown("### ⭐ Watchlist")

        with st.expander("Manage"):
            stocks = get_stocks_by_region(st.session_state.market_region)
            new_stock = st.selectbox("Add Stock", [s for s in stocks.keys() if s not in st.session_state.watchlist])
            if st.button("➕"):
                st.session_state.watchlist.append(new_stock)
                st.rerun()

    # Render selected page
    pages[page]()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <p>Made with ❤️ by Umair Kashif | Ultimate Stock Analysis Platform</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
