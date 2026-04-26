"""
Indian Stock Price Prediction System
Author: Umair Kashif
Live Demo: https://huggingface.co/spaces/kashii1/indian-stock-prediction

Lite version: scikit-learn only (no TensorFlow/Prophet)
Deployable on HuggingFace Spaces, Docker, GCP Cloud Run
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Indian Stock Prediction | Umair Kashif",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    #MainMenu, footer, header { visibility: hidden; }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Sidebar ── */
    div[data-testid="stSidebar"] {
        background: #0a0d14;
        border-right: 1px solid #1a1f2e;
    }

    /* ── App bg ── */
    .stApp { background: #080b12; }
    .block-container { padding-top: 1.2rem !important; }

    /* ── Hero balance card (Sequence-style) ── */
    .hero-card {
        background: linear-gradient(135deg, #0d4a3a 0%, #0a3328 60%, #061f1a 100%);
        border: 1px solid #1a4a3a;
        border-radius: 20px;
        padding: 2rem 2.4rem;
        position: relative;
        overflow: hidden;
        margin-bottom: 1.2rem;
    }
    .hero-card::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 200px; height: 200px;
        background: radial-gradient(circle, rgba(16,185,129,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-card::after {
        content: '';
        position: absolute;
        bottom: -40px; left: 30%;
        width: 160px; height: 160px;
        background: radial-gradient(circle, rgba(102,126,234,0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-label { font-size: 0.78rem; font-weight: 500; color: #6ee7b7; letter-spacing: 0.08em; text-transform: uppercase; margin: 0; }
    .hero-price { font-size: 2.8rem; font-weight: 700; color: #f0fdf4; margin: 0.3rem 0 0.1rem; line-height: 1; }
    .hero-delta-pos { color: #34d399; font-size: 1rem; font-weight: 600; }
    .hero-delta-neg { color: #f87171; font-size: 1rem; font-weight: 600; }
    .hero-sub  { font-size: 0.82rem; color: #6ee7b7; opacity: 0.7; margin-top: 0.3rem; }

    /* ── Account/metric cards (Sequence row) ── */
    .acc-card {
        background: #0f1520;
        border: 1px solid #1a2035;
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 0.8rem;
        transition: border-color 0.2s;
    }
    .acc-card:hover { border-color: #2d3a5a; }
    .acc-label { font-size: 0.72rem; font-weight: 500; color: #4b5680; text-transform: uppercase; letter-spacing: 0.07em; margin: 0 0 0.5rem; }
    .acc-val   { font-size: 1.45rem; font-weight: 700; color: #e2e8f0; margin: 0 0 0.25rem; }
    .acc-delta { font-size: 0.78rem; font-weight: 500; }
    .acc-comp  { font-size: 0.72rem; color: #3d4a6b; margin-top: 0.15rem; }

    /* ── Stat pill badges ── */
    .pill {
        display: inline-flex; align-items: center; gap: 4px;
        padding: 0.18rem 0.6rem;
        border-radius: 999px;
        font-size: 0.72rem; font-weight: 600;
    }
    .pill-up   { background: #052e1c; color: #34d399; }
    .pill-down { background: #2d0a0a; color: #f87171; }
    .pill-neu  { background: #141a2e; color: #64748b; }

    /* ── Generic dark card ── */
    .card {
        background: #0f1520;
        border: 1px solid #1a2035;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
    }
    .card h4 { color: #4b5680; margin: 0 0 0.3rem; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.07em; }
    .card .val { font-size: 1.5rem; font-weight: 700; color: #e2e8f0; }
    .card .delta { font-size: 0.85rem; margin-top: 0.2rem; }

    /* ── Trade table row (Adatra-style) ── */
    .trade-row {
        display: flex; align-items: center;
        padding: 0.65rem 0;
        border-bottom: 1px solid #111827;
        font-size: 0.82rem;
    }
    .trade-row:last-child { border-bottom: none; }
    .trade-dot {
        width: 8px; height: 8px; border-radius: 50%;
        margin-right: 10px; flex-shrink: 0;
    }
    .dot-buy  { background: #34d399; }
    .dot-sell { background: #f87171; }
    .trade-sym  { font-weight: 600; color: #e2e8f0; min-width: 90px; }
    .trade-name { color: #3d4a6b; flex: 1; }
    .trade-px   { color: #94a3b8; min-width: 80px; text-align: right; }
    .trade-chg  { min-width: 75px; text-align: right; font-weight: 600; }
    .trade-pnl  { min-width: 55px; text-align: right; font-size: 0.75rem; color: #4b5680; }

    /* ── Section header ── */
    .sec-head {
        font-size: 0.72rem; font-weight: 600; color: #3d4a6b;
        text-transform: uppercase; letter-spacing: 0.1em;
        margin: 1.4rem 0 0.7rem;
    }

    /* ── Greeting banner (Adatra-style) ── */
    .greeting {
        font-size: 1.55rem; font-weight: 700; color: #e2e8f0;
        margin: 0 0 0.25rem;
    }
    .greeting-sub { font-size: 0.85rem; color: #3d4a6b; margin: 0; }

    /* ── Signal badges ── */
    .badge { display: inline-block; padding: 0.22rem 0.7rem; border-radius: 999px; font-size: 0.75rem; font-weight: 700; }
    .badge-buy  { background: #052e1c; color: #34d399; border: 1px solid #064e3b; }
    .badge-sell { background: #2d0a0a; color: #f87171; border: 1px solid #450a0a; }
    .badge-hold { background: #141a2e; color: #64748b; border: 1px solid #1e2a4a; }

    /* ── Pos / neg colours ── */
    .pos { color: #34d399; }
    .neg { color: #f87171; }
    .neu { color: #64748b; }

    /* ── Streamlit button ── */
    .stButton > button {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white; border: none; border-radius: 8px;
        font-weight: 600; padding: 0.5rem 1.5rem; width: 100%;
        font-size: 0.85rem;
    }
    .stButton > button:hover { opacity: 0.88; }

    /* ── Input / select ── */
    .stSelectbox > div > div,
    .stSlider { color: #e2e8f0 !important; }

    /* scrollbar */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: #080b12; }
    ::-webkit-scrollbar-thumb { background: #1a2035; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
STOCKS = {
    # IT
    "TCS.NS":       "Tata Consultancy Services",
    "INFY.NS":      "Infosys",
    "WIPRO.NS":     "Wipro",
    "HCLTECH.NS":   "HCL Technologies",
    "TECHM.NS":     "Tech Mahindra",
    # Banking
    "HDFCBANK.NS":  "HDFC Bank",
    "ICICIBANK.NS": "ICICI Bank",
    "SBIN.NS":      "State Bank of India",
    "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "AXISBANK.NS":  "Axis Bank",
    # Energy
    "RELIANCE.NS":  "Reliance Industries",
    "ONGC.NS":      "ONGC",
    "IOC.NS":       "Indian Oil Corp",
    # FMCG
    "HINDUNILVR.NS":"Hindustan Unilever",
    "ITC.NS":       "ITC",
    "NESTLEIND.NS": "Nestle India",
    "BRITANNIA.NS": "Britannia",
    # Auto
    "MARUTI.NS":    "Maruti Suzuki",
    "TATAMOTORS.NS":"Tata Motors",
    "BAJAJ-AUTO.NS":"Bajaj Auto",
    # Pharma
    "SUNPHARMA.NS": "Sun Pharma",
    "DRREDDY.NS":   "Dr. Reddy's",
    "CIPLA.NS":     "Cipla",
    # Metals
    "TATASTEEL.NS": "Tata Steel",
    "JSWSTEEL.NS":  "JSW Steel",
    # Infra
    "LT.NS":        "Larsen & Toubro",
    "ULTRACEMCO.NS":"UltraTech Cement",
    # Consumer
    "TITAN.NS":     "Titan",
    "ASIANPAINT.NS":"Asian Paints",
    "BAJFINANCE.NS":"Bajaj Finance",
}

PERIODS = {
    "6 Months": "6mo",
    "1 Year":   "1y",
    "2 Years":  "2y",
    "5 Years":  "5y",
}

MODELS = {
    "Ridge Regression":       Ridge(alpha=1.0),
    "Random Forest":          RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
    "Gradient Boosting":      GradientBoostingRegressor(n_estimators=200, random_state=42),
}

# ─────────────────────────────────────────────
# DATA & FEATURE ENGINEERING
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_data(symbol: str, period: str) -> pd.DataFrame:
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    if df.empty:
        return df
    df.index = df.index.tz_localize(None)
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    c = df["Close"].copy()

    # Moving averages
    for w in [5, 10, 20, 50]:
        df[f"MA_{w}"] = c.rolling(w).mean()
        df[f"EMA_{w}"] = c.ewm(span=w).mean()

    # Bollinger Bands
    ma20 = c.rolling(20).mean()
    std20 = c.rolling(20).std()
    df["BB_upper"] = ma20 + 2 * std20
    df["BB_lower"] = ma20 - 2 * std20
    df["BB_pct"]   = (c - df["BB_lower"]) / (df["BB_upper"] - df["BB_lower"] + 1e-9)

    # RSI
    delta = c.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / (loss + 1e-9)
    df["RSI"] = 100 - 100 / (1 + rs)

    # MACD
    ema12 = c.ewm(span=12).mean()
    ema26 = c.ewm(span=26).mean()
    df["MACD"]        = ema12 - ema26
    df["MACD_signal"] = df["MACD"].ewm(span=9).mean()
    df["MACD_hist"]   = df["MACD"] - df["MACD_signal"]

    # ATR
    high, low = df["High"], df["Low"]
    tr = pd.concat([
        high - low,
        (high - c.shift()).abs(),
        (low  - c.shift()).abs(),
    ], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(14).mean()

    # Volume ratio
    df["Vol_ratio"] = df["Volume"] / (df["Volume"].rolling(20).mean() + 1e-9)

    # Price features
    df["Returns"]    = c.pct_change()
    df["Log_return"] = np.log(c / c.shift())
    df["Volatility"] = df["Returns"].rolling(10).std()
    df["HL_pct"]     = (high - low) / (c + 1e-9)

    # Lag features
    for lag in [1, 2, 3, 5, 10]:
        df[f"Lag_{lag}"] = c.shift(lag)

    # Target: next day close
    df["Target"] = c.shift(-1)

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    return df


FEATURE_COLS = [
    "MA_5","MA_10","MA_20","MA_50",
    "EMA_5","EMA_10","EMA_20","EMA_50",
    "BB_upper","BB_lower","BB_pct",
    "RSI","MACD","MACD_signal","MACD_hist",
    "ATR","Vol_ratio",
    "Returns","Log_return","Volatility","HL_pct",
    "Lag_1","Lag_2","Lag_3","Lag_5","Lag_10",
    "Open","High","Low","Volume",
]


def split_and_scale(df, test_ratio=0.2):
    X = df[FEATURE_COLS]
    y = df["Target"]
    split = int(len(df) * (1 - test_ratio))
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]
    scaler = RobustScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)
    return X_train_s, X_test_s, y_train, y_test, X_test.index, scaler


def train_models(X_train, X_test, y_train, y_test):
    results = {}
    for name, model in MODELS.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        rmse  = np.sqrt(mean_squared_error(y_test, preds))
        mae   = mean_absolute_error(y_test, preds)
        r2    = r2_score(y_test, preds)
        mape  = np.mean(np.abs((y_test.values - preds) / (y_test.values + 1e-9))) * 100
        results[name] = {
            "model": model,
            "preds": preds,
            "rmse": rmse,
            "mae":  mae,
            "r2":   r2,
            "mape": mape,
        }
    return results


def predict_future(model, scaler, df, days=30):
    last_row = df[FEATURE_COLS].iloc[-1:].copy()
    preds, prices = [], []
    current_close = df["Close"].iloc[-1]

    for _ in range(days):
        X_s = scaler.transform(last_row)
        p   = model.predict(X_s)[0]
        preds.append(p)

        # Shift lag features
        new_row = last_row.copy()
        for lag in [10, 5, 3, 2, 1]:
            if f"Lag_{lag}" in new_row.columns and lag > 1:
                prev_lag = f"Lag_{lag-1}" if f"Lag_{lag-1}" in new_row.columns else "Lag_1"
                new_row[f"Lag_{lag}"] = last_row[prev_lag].values
        new_row["Lag_1"] = p
        new_row["Returns"]    = (p - current_close) / (current_close + 1e-9)
        new_row["Log_return"] = np.log(p / (current_close + 1e-9))
        last_row = new_row
        current_close = p

    last_date = df.index[-1]
    future_dates = [last_date + timedelta(days=i+1) for i in range(days)]
    return future_dates, preds


def trading_signals(df):
    """Legacy single-signal — kept for backward compatibility."""
    sig = pd.Series(0, index=df.index)
    if "MA_5" in df and "MA_20" in df:
        cross_up   = (df["MA_5"] > df["MA_20"]) & (df["MA_5"].shift() <= df["MA_20"].shift())
        cross_down = (df["MA_5"] < df["MA_20"]) & (df["MA_5"].shift() >= df["MA_20"].shift())
        sig[cross_up]   = 1
        sig[cross_down] = -1
    if "RSI" in df:
        sig[df["RSI"] < 30] = 1
        sig[df["RSI"] > 70] = -1
    return sig


def short_term_signal(df):
    """
    Short-term signal (1–10 day horizon).
    Indicators: RSI(14), MACD crossover, MA5 vs MA10.
    Returns: dict with signal, score, reasons, indicator values.
    """
    score = 0          # range: -3 to +3
    reasons = []

    rsi = df["RSI"].iloc[-1]
    macd     = df["MACD"].iloc[-1]
    macd_sig = df["MACD_signal"].iloc[-1]
    macd_prev     = df["MACD"].iloc[-2]
    macd_sig_prev = df["MACD_signal"].iloc[-2]

    # RSI
    if rsi < 30:
        score += 1
        reasons.append(f"RSI {rsi:.1f} — oversold (bullish)")
    elif rsi > 70:
        score -= 1
        reasons.append(f"RSI {rsi:.1f} — overbought (bearish)")
    else:
        reasons.append(f"RSI {rsi:.1f} — neutral zone")

    # MACD crossover
    if macd > macd_sig and macd_prev <= macd_sig_prev:
        score += 1
        reasons.append("MACD just crossed above signal (bullish crossover)")
    elif macd < macd_sig and macd_prev >= macd_sig_prev:
        score -= 1
        reasons.append("MACD just crossed below signal (bearish crossover)")
    elif macd > macd_sig:
        score += 0.5
        reasons.append("MACD above signal line (bullish momentum)")
    else:
        score -= 0.5
        reasons.append("MACD below signal line (bearish momentum)")

    # MA5 vs MA10
    if "MA_5" in df.columns and "MA_10" in df.columns:
        ma5  = df["MA_5"].iloc[-1]
        ma10 = df["MA_10"].iloc[-1]
        if ma5 > ma10:
            score += 0.5
            reasons.append("MA5 above MA10 — short-term uptrend")
        else:
            score -= 0.5
            reasons.append("MA5 below MA10 — short-term downtrend")

    # Volume confirmation
    if "Vol_ratio" in df.columns:
        vol_ratio = df["Vol_ratio"].iloc[-1]
        if vol_ratio > 1.5:
            reasons.append(f"Volume {vol_ratio:.1f}× average — strong move confirmation")
        else:
            reasons.append(f"Volume {vol_ratio:.1f}× average — low conviction")

    if score >= 1:
        signal, badge = "BUY",  "badge-buy"
    elif score <= -1:
        signal, badge = "SELL", "badge-sell"
    else:
        signal, badge = "HOLD", "badge-hold"

    return {
        "signal": signal, "badge": badge, "score": round(score, 1),
        "reasons": reasons,
        "rsi": rsi, "macd": macd, "macd_sig": macd_sig,
    }


def long_term_signal(df, raw):
    """
    Long-term signal (20–90 day horizon).
    Indicators: MA20/MA50 golden cross, Bollinger Band position, 52W range, trend strength.
    Returns: dict with signal, score, reasons, indicator values.
    """
    score = 0
    reasons = []
    close = df["Close"].iloc[-1]

    # MA20 vs MA50 golden/death cross
    if "MA_20" in df.columns and "MA_50" in df.columns:
        ma20 = df["MA_20"].iloc[-1]
        ma50 = df["MA_50"].iloc[-1]
        ma20_prev = df["MA_20"].iloc[-2]
        ma50_prev = df["MA_50"].iloc[-2]

        if ma20 > ma50 and ma20_prev <= ma50_prev:
            score += 2
            reasons.append("🟡 Golden Cross: MA20 just crossed above MA50 (strong bullish)")
        elif ma20 < ma50 and ma20_prev >= ma50_prev:
            score -= 2
            reasons.append("💀 Death Cross: MA20 just crossed below MA50 (strong bearish)")
        elif ma20 > ma50:
            score += 1
            reasons.append("MA20 above MA50 — sustained uptrend")
        else:
            score -= 1
            reasons.append("MA20 below MA50 — sustained downtrend")

    # Bollinger Band position
    if "BB_pct" in df.columns:
        bb_pct = df["BB_pct"].iloc[-1]
        if bb_pct < 0.2:
            score += 1
            reasons.append(f"Price near lower Bollinger Band ({bb_pct:.0%}) — mean-reversion buy zone")
        elif bb_pct > 0.8:
            score -= 1
            reasons.append(f"Price near upper Bollinger Band ({bb_pct:.0%}) — overbought territory")
        else:
            reasons.append(f"Price at {bb_pct:.0%} of Bollinger Band — neutral")

    # 52-week range position
    high_52w = raw["High"].max()
    low_52w  = raw["Low"].min()
    pos_52w  = (close - low_52w) / (high_52w - low_52w + 1e-9)

    if pos_52w < 0.25:
        score += 1
        reasons.append(f"Near 52W low (bottom {pos_52w:.0%} of range) — value zone")
    elif pos_52w > 0.85:
        score -= 0.5
        reasons.append(f"Near 52W high (top {pos_52w:.0%} of range) — caution at resistance")
    else:
        reasons.append(f"At {pos_52w:.0%} of 52W range — mid-range")

    # Trend strength via ATR
    if "ATR" in df.columns:
        atr     = df["ATR"].iloc[-1]
        atr_pct = atr / close * 100
        reasons.append(f"ATR {atr_pct:.1f}% of price — {'high' if atr_pct > 2 else 'moderate'} volatility environment")

    if score >= 1.5:
        signal, badge = "BUY",  "badge-buy"
    elif score <= -1.5:
        signal, badge = "SELL", "badge-sell"
    else:
        signal, badge = "HOLD", "badge-hold"

    return {
        "signal": signal, "badge": badge, "score": round(score, 1),
        "reasons": reasons,
        "pos_52w": pos_52w, "high_52w": high_52w, "low_52w": low_52w,
    }


# ─────────────────────────────────────────────
# CHART HELPERS
# ─────────────────────────────────────────────
DARK = "plotly_dark"

def price_chart(df, symbol):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.04, row_heights=[0.75, 0.25])
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="Price",
        increasing_line_color="#34d399", decreasing_line_color="#f87171",
    ), row=1, col=1)

    if "MA_20" in df:
        fig.add_trace(go.Scatter(x=df.index, y=df["MA_20"], name="MA 20",
                                 line=dict(color="#f59e0b", width=1.5)), row=1, col=1)
    if "MA_50" in df:
        fig.add_trace(go.Scatter(x=df.index, y=df["MA_50"], name="MA 50",
                                 line=dict(color="#a78bfa", width=1.5)), row=1, col=1)
    if "BB_upper" in df:
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"],
                                 line=dict(color="rgba(148,163,184,0.4)", width=1),
                                 name="BB Upper", showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"],
                                 line=dict(color="rgba(148,163,184,0.4)", width=1),
                                 fill="tonexty", fillcolor="rgba(148,163,184,0.07)",
                                 name="Bollinger Bands"), row=1, col=1)

    colors = ["#34d399" if c >= o else "#f87171"
              for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume",
                         marker_color=colors, opacity=0.6), row=2, col=1)

    fig.update_layout(template=DARK, height=520, xaxis_rangeslider_visible=False,
                      margin=dict(l=0, r=0, t=30, b=0),
                      title=dict(text=f"{symbol} — Price History", font_size=14))
    fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
    fig.update_yaxes(title_text="Volume",    row=2, col=1)
    return fig


def prediction_chart(df, test_idx, results, future_dates, future_preds, symbol):
    fig = go.Figure()
    # Actual
    fig.add_trace(go.Scatter(
        x=test_idx, y=results[list(results.keys())[0]]["_actual"],
        name="Actual", line=dict(color="#94a3b8", width=2)
    ))
    colors_pred = ["#667eea", "#34d399", "#f59e0b"]
    for i, (name, res) in enumerate(results.items()):
        fig.add_trace(go.Scatter(
            x=test_idx, y=res["preds"],
            name=name, line=dict(width=2, color=colors_pred[i], dash="dash")
        ))
    # Future
    best = min(results, key=lambda k: results[k]["rmse"])
    fig.add_trace(go.Scatter(
        x=future_dates, y=future_preds,
        name=f"Forecast ({best})",
        line=dict(color="#f472b6", width=2.5),
        fill="tozeroy", fillcolor="rgba(244,114,182,0.05)"
    ))
    # add_vline with string dates breaks on some Plotly versions — use add_shape instead
    fig.add_shape(
        type="line",
        x0=test_idx[0], x1=test_idx[0],
        y0=0, y1=1,
        xref="x", yref="paper",
        line=dict(color="rgba(255,255,255,0.3)", width=1, dash="dot"),
    )
    fig.add_annotation(
        x=test_idx[0], y=1,
        xref="x", yref="paper",
        text="Test period →",
        showarrow=False,
        font=dict(size=11, color="rgba(255,255,255,0.5)"),
        xanchor="left", yanchor="bottom",
    )

    fig.update_layout(template=DARK, height=420,
                      margin=dict(l=0, r=0, t=30, b=0),
                      title=dict(text=f"{symbol} — Model Predictions vs Actual", font_size=14),
                      hovermode="x unified")
    fig.update_yaxes(title_text="Price (₹)")
    return fig


def rsi_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
                             line=dict(color="#a78bfa", width=2)))
    fig.add_hline(y=70, line_dash="dash", line_color="#f87171",
                  annotation_text="Overbought 70", annotation_font_size=10)
    fig.add_hline(y=30, line_dash="dash", line_color="#34d399",
                  annotation_text="Oversold 30",   annotation_font_size=10)
    fig.update_layout(template=DARK, height=220,
                      margin=dict(l=0, r=0, t=30, b=0),
                      title=dict(text="RSI (14)", font_size=13),
                      yaxis=dict(range=[0, 100]))
    return fig


def macd_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD",
                             line=dict(color="#667eea", width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD_signal"], name="Signal",
                             line=dict(color="#f59e0b", width=1.5)))
    colors = ["#34d399" if v >= 0 else "#f87171" for v in df["MACD_hist"]]
    fig.add_trace(go.Bar(x=df.index, y=df["MACD_hist"], name="Histogram",
                         marker_color=colors, opacity=0.7))
    fig.update_layout(template=DARK, height=220,
                      margin=dict(l=0, r=0, t=30, b=0),
                      title=dict(text="MACD (12, 26, 9)", font_size=13))
    return fig


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                    padding:1rem 1.2rem;border-radius:10px;margin-bottom:1rem;">
            <h3 style="color:white;margin:0;font-size:1.1rem;">📈 Stock Predictor</h3>
            <p style="color:rgba(255,255,255,0.8);margin:0.3rem 0 0;font-size:0.8rem;">
                by Umair Kashif
            </p>
        </div>
        """, unsafe_allow_html=True)

        symbol = st.selectbox(
            "Select Stock",
            list(STOCKS.keys()),
            format_func=lambda s: f"{s}  —  {STOCKS[s]}",
            index=0,
        )

        period_label = st.select_slider(
            "Historical Period",
            options=list(PERIODS.keys()),
            value="1 Year",
        )
        period = PERIODS[period_label]

        pred_days = st.slider("Forecast Days", 7, 60, 30)

        st.markdown("---")
        run = st.button("🚀 Run Analysis")

        st.markdown("---")
        st.markdown("""
        <div style="font-size:0.75rem;color:#64748b;line-height:1.6;">
        <b style="color:#94a3b8;">Models used</b><br>
        • Ridge Regression<br>
        • Random Forest<br>
        • Gradient Boosting<br><br>
        <b style="color:#94a3b8;">Stack</b><br>
        Python · scikit-learn · yfinance · Streamlit · Plotly<br><br>
        <b style="color:#94a3b8;">Links</b><br>
        <a href="https://github.com/kashifumair125" style="color:#a78bfa;">GitHub</a> ·
        <a href="https://linkedin.com/in/umair-kashif" style="color:#a78bfa;">LinkedIn</a>
        </div>
        """, unsafe_allow_html=True)

    return symbol, period, pred_days, run


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    symbol, period, pred_days, run = render_sidebar()

    # ── Greeting header (Adatra style) ─────────────────────────────────
    hour = datetime.now().hour
    greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 18 else "Good Evening"
    stock_name = STOCKS.get(symbol, symbol)

    if not run:
        # ── WELCOME DASHBOARD ────────────────────────────────────────────
        # Top greeting row
        col_g, col_d = st.columns([3, 1])
        with col_g:
            st.markdown(f"""
            <p class="greeting">{greeting}, welcome back 👋</p>
            <p class="greeting-sub">Select a stock from the sidebar and run analysis to get started.</p>
            """, unsafe_allow_html=True)
        with col_d:
            st.markdown(f"""
            <div style="text-align:right;padding-top:0.3rem;">
                <span style="font-size:0.75rem;color:#3d4a6b;">Today</span><br>
                <span style="font-size:0.95rem;font-weight:600;color:#94a3b8;">
                    {datetime.now().strftime("%d %b %Y")}
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

        # ── Live snapshot cards for 5 popular stocks ─────────────────────
        WATCH = [
            ("TCS.NS",       "Tata Consultancy"),
            ("RELIANCE.NS",  "Reliance Industries"),
            ("HDFCBANK.NS",  "HDFC Bank"),
            ("INFY.NS",      "Infosys"),
            ("ICICIBANK.NS", "ICICI Bank"),
        ]
        st.markdown('<p class="sec-head">Market Watch</p>', unsafe_allow_html=True)
        wcols = st.columns(5)
        for wc, (wsym, wname) in zip(wcols, WATCH):
            with wc:
                try:
                    wd = fetch_data(wsym, "5d")
                    if not wd.empty and len(wd) >= 2:
                        wp  = wd["Close"].iloc[-1]
                        wp2 = wd["Close"].iloc[-2]
                        wch = (wp - wp2) / wp2 * 100
                        pill_cls = "pill-up" if wch >= 0 else "pill-down"
                        arr = "▲" if wch >= 0 else "▼"
                        st.markdown(f"""
                        <div class="acc-card">
                            <p class="acc-label">{wname}</p>
                            <p class="acc-val">₹{wp:,.1f}</p>
                            <span class="pill {pill_cls}">{arr} {abs(wch):.2f}%</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="acc-card"><p class="acc-label">{wname}</p><p class="acc-val">—</p></div>', unsafe_allow_html=True)
                except Exception:
                    st.markdown(f'<div class="acc-card"><p class="acc-label">{wname}</p><p class="acc-val">—</p></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

        # ── Two-column layout: mini chart + feature list ──────────────────
        col_chart, col_feat = st.columns([3, 2], gap="medium")

        with col_chart:
            st.markdown('<p class="sec-head">Market Overview — Nifty 50 ETF (NIFTYBEES.NS)</p>', unsafe_allow_html=True)
            try:
                nd = fetch_data("NIFTYBEES.NS", "3mo")
                if not nd.empty:
                    nclose = nd["Close"]
                    nc0    = nclose.iloc[0]
                    color  = "#10b981" if nclose.iloc[-1] >= nc0 else "#f87171"
                    fill   = "rgba(16,185,129,0.08)" if nclose.iloc[-1] >= nc0 else "rgba(248,113,113,0.08)"
                    fig_mkt = go.Figure()
                    fig_mkt.add_trace(go.Scatter(
                        x=nd.index, y=nclose,
                        fill="tozeroy", fillcolor=fill,
                        line=dict(color=color, width=2),
                        hovertemplate="₹%{y:,.2f}<extra></extra>",
                    ))
                    chg_tot = (nclose.iloc[-1] - nc0) / nc0 * 100
                    fig_mkt.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=240,
                        margin=dict(l=0, r=0, t=10, b=0),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=True,
                                   tickfont=dict(size=10, color="#3d4a6b")),
                        yaxis=dict(showgrid=True, gridcolor="#0f1520", zeroline=False,
                                   tickfont=dict(size=10, color="#3d4a6b"),
                                   tickprefix="₹"),
                        showlegend=False,
                        annotations=[dict(
                            x=0.01, y=0.98, xref="paper", yref="paper",
                            text=f"<b>₹{nclose.iloc[-1]:,.2f}</b>  "
                                 f"<span style='color:{'#34d399' if chg_tot>=0 else '#f87171'}'>"
                                 f"{'▲' if chg_tot>=0 else '▼'} {abs(chg_tot):.2f}% (3M)</span>",
                            showarrow=False, font=dict(size=13, color="#e2e8f0"),
                            align="left",
                        )],
                    )
                    st.plotly_chart(fig_mkt, use_container_width=True)
            except Exception:
                st.info("Market overview unavailable.")

        with col_feat:
            st.markdown('<p class="sec-head">What This App Does</p>', unsafe_allow_html=True)
            features = [
                ("🤖", "3 ML Models",        "Ridge · Random Forest · Gradient Boosting"),
                ("📊", "30+ Features",       "RSI · MACD · Bollinger Bands · ATR · Lag"),
                ("🔮", "60-Day Forecast",    "Iterative future price projection"),
                ("⚡", "Short-Term Signal",  "RSI + MACD + MA crossover scoring"),
                ("📅", "Long-Term Signal",   "Golden cross · 52W range · BB position"),
                ("💾", "CSV Export",         "Download forecast & historical data"),
            ]
            for icon, title, desc in features:
                st.markdown(f"""
                <div style="display:flex;align-items:flex-start;gap:12px;
                            padding:0.65rem 0;border-bottom:1px solid #0f1520;">
                    <span style="font-size:1.2rem;flex-shrink:0;margin-top:1px;">{icon}</span>
                    <div>
                        <div style="font-size:0.85rem;font-weight:600;color:#cbd5e1;">{title}</div>
                        <div style="font-size:0.75rem;color:#3d4a6b;margin-top:1px;">{desc}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ── Top stocks mini watchlist table ───────────────────────────────
        st.markdown('<p class="sec-head">Top Movers — Live</p>', unsafe_allow_html=True)
        MOVERS = [
            ("TCS.NS",        "Tata Consultancy Services", "IT"),
            ("RELIANCE.NS",   "Reliance Industries",       "Energy"),
            ("HDFCBANK.NS",   "HDFC Bank",                 "Banking"),
            ("INFY.NS",       "Infosys",                   "IT"),
            ("MARUTI.NS",     "Maruti Suzuki",              "Auto"),
            ("SUNPHARMA.NS",  "Sun Pharma",                 "Pharma"),
            ("TATASTEEL.NS",  "Tata Steel",                 "Metals"),
            ("BAJFINANCE.NS", "Bajaj Finance",              "Finance"),
        ]

        # Build rows as plain Python list — render via components.v1.html
        # so Streamlit never escapes the HTML
        import streamlit.components.v1 as components

        mover_rows = []
        for msym, mname, msec in MOVERS:
            try:
                md = fetch_data(msym, "5d")
                if not md.empty and len(md) >= 2:
                    mp  = float(md["Close"].iloc[-1])
                    mp2 = float(md["Close"].iloc[-2])
                    mch = (mp - mp2) / mp2 * 100
                    arr = "\u25b2" if mch >= 0 else "\u25bc"
                    sig = "BUY" if mch > 0.5 else "SELL" if mch < -0.5 else "HOLD"
                    mover_rows.append((msym, mname, msec, mp, mch, arr, sig))
                else:
                    mover_rows.append((msym, mname, msec, None, None, "", "\u2014"))
            except Exception:
                mover_rows.append((msym, mname, msec, None, None, "", "\u2014"))

        def _sig_style(sig):
            if sig == "BUY":
                return "background:#052e1c;color:#34d399;border:1px solid #064e3b;"
            if sig == "SELL":
                return "background:#2d0a0a;color:#f87171;border:1px solid #450a0a;"
            return "background:#141a2e;color:#64748b;border:1px solid #1e2a4a;"

        rows_parts = []
        for msym, mname, msec, mp, mch, arr, sig in mover_rows:
            dot_color = "#34d399" if (mch is not None and mch >= 0) else "#f87171"
            chg_color = "#34d399" if (mch is not None and mch >= 0) else "#f87171"
            price_str = f"&#8377;{mp:,.2f}" if mp is not None else "\u2014"
            chg_str   = f"{arr} {abs(mch):.2f}%" if mch is not None else "\u2014"
            ss        = _sig_style(sig)
            rows_parts.append(
                f"<tr>"
                f"<td style=\"padding:10px 8px;\">"
                f"<span style=\"display:inline-block;width:8px;height:8px;border-radius:50%;background:{dot_color};\"></span>"
                f"</td>"
                f"<td style=\"padding:10px 8px;font-weight:600;color:#e2e8f0;white-space:nowrap;\">{msym}</td>"
                f"<td style=\"padding:10px 8px;color:#4b5680;\">{mname}</td>"
                f"<td style=\"padding:10px 8px;text-align:center;color:#3d4a6b;font-size:11px;\">{msec}</td>"
                f"<td style=\"padding:10px 8px;text-align:right;color:#94a3b8;white-space:nowrap;\">{price_str}</td>"
                f"<td style=\"padding:10px 8px;text-align:right;font-weight:600;color:{chg_color};white-space:nowrap;\">{chg_str}</td>"
                f"<td style=\"padding:10px 8px;text-align:right;\">"
                f"<span style=\"display:inline-block;padding:2px 10px;border-radius:999px;font-size:11px;font-weight:700;{ss}\">{sig}</span>"
                f"</td>"
                f"</tr>"
            )

        table_html = (
            "<!DOCTYPE html><html><head><style>"
            "* {box-sizing:border-box;margin:0;padding:0;}"
            "body {background:#0f1520;border:1px solid #1a2035;border-radius:14px;"
            "overflow:hidden;font-family:Inter,-apple-system,sans-serif;}"
            "table {width:100%;border-collapse:collapse;font-size:13px;}"
            "thead tr {border-bottom:1px solid #111827;}"
            "thead th {padding:10px 8px;text-align:left;font-size:10px;font-weight:600;"
            "color:#3d4a6b;text-transform:uppercase;letter-spacing:0.08em;}"
            "tbody tr {border-bottom:1px solid #0d1018;transition:background 0.15s;}"
            "tbody tr:last-child {border-bottom:none;}"
            "tbody tr:hover {background:#111827;}"
            "</style></head><body>"
            "<table><thead><tr>"
            "<th style=\"width:20px;\"></th>"
            "<th>Symbol</th><th>Company</th>"
            "<th style=\"text-align:center;\">Sector</th>"
            "<th style=\"text-align:right;\">Price</th>"
            "<th style=\"text-align:right;\">Change</th>"
            "<th style=\"text-align:right;\">Signal</th>"
            "</tr></thead><tbody>"
            + "".join(rows_parts)
            + "</tbody></table></body></html>"
        )

        components.html(table_html, height=len(mover_rows) * 46 + 52, scrolling=False)


        st.markdown("""
        <div style="text-align:center;padding:1rem 0 0;font-size:0.72rem;color:#1e2a3a;">
            ⚠️ Prices delayed · For educational purposes only · Not financial advice
        </div>
        """, unsafe_allow_html=True)
        return

    # ── ANALYSIS DASHBOARD ───────────────────────────────────────────────
    # Greeting + stock hero card (Sequence style)
    col_g, col_d = st.columns([3, 1])
    with col_g:
        st.markdown(f"""
        <p class="greeting">{greeting}, here's your analysis 📊</p>
        <p class="greeting-sub">Analysing <b style="color:#94a3b8;">{stock_name}</b>
           ({symbol}) &nbsp;·&nbsp; {period} historical data &nbsp;·&nbsp; {pred_days}-day forecast</p>
        """, unsafe_allow_html=True)
    with col_d:
        st.markdown(f"""
        <div style="text-align:right;padding-top:0.3rem;">
            <span style="font-size:0.75rem;color:#3d4a6b;">Date</span><br>
            <span style="font-size:0.95rem;font-weight:600;color:#94a3b8;">
                {datetime.now().strftime("%d %b %Y")}
            </span>
        </div>
        """, unsafe_allow_html=True)

    # ── Fetch & process ──
    with st.spinner(f"Fetching data for {symbol}…"):
        raw = fetch_data(symbol, period)

    if raw.empty:
        st.error("No data returned. Check the symbol or try a different period.")
        return

    with st.spinner("Engineering features…"):
        df = add_features(raw.copy())

    if len(df) < 60:
        st.error("Not enough data after feature engineering. Try a longer period.")
        return

    # ── Live snapshot ──
    c       = df["Close"]
    current = c.iloc[-1]
    prev    = c.iloc[-2]
    change  = current - prev
    chg_pct = change / prev * 100
    arrow   = "▲" if change >= 0 else "▼"
    clr     = "#34d399" if change >= 0 else "#f87171"
    vol_ann = df["Returns"].std() * np.sqrt(252) * 100
    hi52    = raw["High"].max()
    lo52    = raw["Low"].min()
    avg_vol = int(df["Volume"].tail(30).mean())
    pos_52w = (current - lo52) / (hi52 - lo52 + 1e-9) * 100

    # ── Sequence-style hero balance card ─────────────────────────────
    st.markdown(f"""
    <div class="hero-card">
        <p class="hero-label">Current Price · {stock_name} ({symbol})</p>
        <p class="hero-price">₹{current:,.2f}
            <span style="font-size:1rem;font-weight:500;color:{clr};margin-left:0.6rem;">
                {arrow} ₹{abs(change):.2f} &nbsp;({chg_pct:+.2f}%)
            </span>
        </p>
        <p class="hero-sub">Period: {period} &nbsp;·&nbsp; Forecast: {pred_days} days &nbsp;·&nbsp;
           Annual volatility: {vol_ann:.1f}%</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Four account-style cards (Sequence row) ───────────────────────
    m1, m2, m3, m4 = st.columns(4)
    def acc(col, label, val, delta_str, delta_pos):
        pill = f'<span class="pill {"pill-up" if delta_pos else "pill-down"}">{delta_str}</span>' if delta_str else ""
        col.markdown(f"""
        <div class="acc-card">
            <p class="acc-label">{label}</p>
            <p class="acc-val">{val}</p>
            {pill}
        </div>
        """, unsafe_allow_html=True)

    acc(m1, "52W High",          f"₹{hi52:,.2f}",
        f"{'▲' if current >= hi52*0.95 else '●'} near high" if current >= hi52*0.95 else "",
        True)
    acc(m2, "52W Low",           f"₹{lo52:,.2f}",
        f"▲ {((current-lo52)/lo52*100):.1f}% above low", True)
    acc(m3, "52W Range Position",f"{pos_52w:.0f}%",
        "▲ upper half" if pos_52w > 50 else "▼ lower half", pos_52w > 50)
    acc(m4, "Avg Volume (30D)",  f"{avg_vol:,}",
        f"{'▲' if df['Volume'].iloc[-1] > avg_vol else '▼'} vs avg",
        df["Volume"].iloc[-1] > avg_vol)

    # ── Price chart ──
    st.plotly_chart(price_chart(df, symbol), use_container_width=True)

    # ── Train models ──
    with st.spinner("Training ML models…"):
        X_train, X_test, y_train, y_test, test_idx, scaler = split_and_scale(df)
        results = train_models(X_train, X_test, y_train, y_test)
        for name in results:
            results[name]["_actual"] = y_test.values

    # ── Future forecast ──
    best_name = min(results, key=lambda k: results[k]["rmse"])
    best_model = results[best_name]["model"]
    future_dates, future_preds = predict_future(best_model, scaler, df, days=pred_days)

    # ── Prediction chart ──
    st.plotly_chart(
        prediction_chart(df, test_idx, results, future_dates, future_preds, symbol),
        use_container_width=True,
    )

    # ── Model performance cards ──
    st.markdown("### 🏆 Model Performance")
    cols = st.columns(len(results))
    sorted_results = sorted(results.items(), key=lambda x: x[1]["rmse"])
    for col, (name, res) in zip(cols, sorted_results):
        is_best = name == best_name
        border  = "border:2px solid #667eea;" if is_best else ""
        crown   = "👑 " if is_best else ""
        with col:
            st.markdown(f"""
            <div class="card" style="{border}">
                <h4>{crown}{name}</h4>
                <div style="font-size:0.9rem;color:#cbd5e1;line-height:1.9;">
                    RMSE &nbsp; <b style="color:#f1f5f9;">₹{res['rmse']:.2f}</b><br>
                    MAE  &nbsp;&nbsp; <b style="color:#f1f5f9;">₹{res['mae']:.2f}</b><br>
                    R²   &nbsp;&nbsp;&nbsp;&nbsp; <b style="color:#f1f5f9;">{res['r2']:.4f}</b><br>
                    MAPE &nbsp; <b style="color:#f1f5f9;">{res['mape']:.1f}%</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Forecast table ──
    st.markdown(f"### 🔮 {pred_days}-Day Forecast  *(Best model: {best_name})*")
    fc_df = pd.DataFrame({
        "Date":            [d.strftime("%Y-%m-%d") for d in future_dates],
        "Predicted Price": [f"₹{p:,.2f}" for p in future_preds],
        "Change vs Today": [f"{((p - current) / current * 100):+.2f}%" for p in future_preds],
        "Direction":       ["📈" if p > current else "📉" if p < current else "➡️" for p in future_preds],
    })
    st.dataframe(fc_df, use_container_width=True, hide_index=True, height=320)

    # ── Technical indicators ──
    st.markdown("### 📊 Technical Indicators")
    t1, t2 = st.tabs(["RSI", "MACD"])
    with t1:
        st.plotly_chart(rsi_chart(df), use_container_width=True)
    with t2:
        st.plotly_chart(macd_chart(df), use_container_width=True)

    # ── Trading signals ──
    st.markdown("### 🎯 Trading Signals")

    st_sig = short_term_signal(df)
    lt_sig = long_term_signal(df, raw)

    # Score bar helper
    def score_bar(score, max_score=3):
        pct = int(((score + max_score) / (2 * max_score)) * 100)
        pct = max(0, min(100, pct))
        color = "#34d399" if score > 0 else "#f87171" if score < 0 else "#64748b"
        return f"""
        <div style="background:#1e2130;border-radius:999px;height:8px;overflow:hidden;margin:6px 0;">
            <div style="width:{pct}%;height:8px;background:{color};border-radius:999px;"></div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:11px;color:#64748b;">
            <span>Bearish</span><span>Neutral</span><span>Bullish</span>
        </div>"""

    tab_st, tab_lt = st.tabs(["⚡ Short-Term  (1–10 days)", "📅 Long-Term  (20–90 days)"])

    # ── Short-term tab ──
    with tab_st:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <h4>Short-Term Signal</h4>
                <div style="margin:0.8rem 0;">
                    <span class="badge {st_sig['badge']}"
                          style="font-size:1.5rem;padding:0.4rem 1.4rem;border-radius:999px;">
                        {st_sig['signal']}
                    </span>
                </div>
                <div style="font-size:0.82rem;color:#94a3b8;margin-bottom:0.4rem;">
                    Score: <b style="color:#f1f5f9;">{st_sig['score']:+.1f}</b> / 3.0
                </div>
                {score_bar(st_sig['score'])}
                <div style="margin-top:1rem;font-size:0.82rem;color:#64748b;line-height:1.8;text-align:left;">
                    RSI &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b style="color:#f1f5f9;">{st_sig['rsi']:.1f}</b><br>
                    MACD &nbsp;&nbsp; <b style="color:#f1f5f9;">{"Bullish ↑" if st_sig["macd"] > st_sig["macd_sig"] else "Bearish ↓"}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("**Signal breakdown**")
            for r in st_sig["reasons"]:
                icon = "🟢" if any(w in r.lower() for w in ["bullish","oversold","above","uptrend","strong","crossover above"])                        else "🔴" if any(w in r.lower() for w in ["bearish","overbought","below","downtrend","crossover below"])                        else "⚪"
                st.markdown(f"{icon} {r}")

        # Historical signals on price chart
        sigs_hist  = trading_signals(df)
        buy_dates  = df.index[sigs_hist == 1]
        sell_dates = df.index[sigs_hist == -1]
        fig_sig = go.Figure()
        fig_sig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Price",
                                     line=dict(color="#94a3b8", width=1.5)))
        if len(buy_dates):
            fig_sig.add_trace(go.Scatter(x=buy_dates, y=df.loc[buy_dates, "Close"],
                mode="markers", name="Buy signal",
                marker=dict(symbol="triangle-up", size=12, color="#34d399")))
        if len(sell_dates):
            fig_sig.add_trace(go.Scatter(x=sell_dates, y=df.loc[sell_dates, "Close"],
                mode="markers", name="Sell signal",
                marker=dict(symbol="triangle-down", size=12, color="#f87171")))
        fig_sig.update_layout(template=DARK, height=260,
                               margin=dict(l=0, r=0, t=24, b=0),
                               title=dict(text="Historical short-term signals on price", font_size=13),
                               hovermode="x unified")
        st.plotly_chart(fig_sig, use_container_width=True)

    # ── Long-term tab ──
    with tab_lt:
        col1, col2 = st.columns([1, 1])
        with col1:
            pos_pct = int(lt_sig["pos_52w"] * 100)
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <h4>Long-Term Signal</h4>
                <div style="margin:0.8rem 0;">
                    <span class="badge {lt_sig['badge']}"
                          style="font-size:1.5rem;padding:0.4rem 1.4rem;border-radius:999px;">
                        {lt_sig['signal']}
                    </span>
                </div>
                <div style="font-size:0.82rem;color:#94a3b8;margin-bottom:0.4rem;">
                    Score: <b style="color:#f1f5f9;">{lt_sig['score']:+.1f}</b> / 4.0
                </div>
                {score_bar(lt_sig['score'], max_score=4)}
                <div style="margin-top:1rem;font-size:0.82rem;color:#64748b;line-height:1.8;text-align:left;">
                    52W Low  &nbsp; <b style="color:#f1f5f9;">&#8377;{lt_sig['low_52w']:,.2f}</b><br>
                    52W High &nbsp; <b style="color:#f1f5f9;">&#8377;{lt_sig['high_52w']:,.2f}</b><br>
                    In range &nbsp;&nbsp; <b style="color:#f1f5f9;">{pos_pct}% from low</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("**Signal breakdown**")
            for r in lt_sig["reasons"]:
                icon = "🟢" if any(w in r.lower() for w in ["golden","bullish","above","uptrend","buy","value","bottom","reversion"])                        else "🔴" if any(w in r.lower() for w in ["death","bearish","below","downtrend","caution","overbought"])                        else "⚪"
                st.markdown(f"{icon} {r}")

        fig_52w = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=lt_sig["pos_52w"] * 100,
            title={"text": "Position in 52-Week Range (%)", "font": {"size": 13}},
            delta={"reference": 50, "valueformat": ".0f"},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar":  {"color": "#667eea"},
                "steps": [
                    {"range": [0,  25], "color": "#064e3b"},
                    {"range": [25, 75], "color": "#1e2130"},
                    {"range": [75, 100],"color": "#450a0a"},
                ],
                "threshold": {"line": {"color": "#f1f5f9", "width": 2},
                              "thickness": 0.75, "value": lt_sig["pos_52w"] * 100},
            },
            number={"suffix": "%", "font": {"size": 28}},
        ))
        fig_52w.update_layout(template=DARK, height=260,
                               margin=dict(l=20, r=20, t=30, b=10))
        st.plotly_chart(fig_52w, use_container_width=True)

    st.markdown("""
    <div style="background:#1e2130;border:0.5px solid #2d3250;border-radius:10px;
                padding:0.9rem 1.2rem;font-size:0.8rem;color:#64748b;margin-top:0.5rem;">
        ⚠️ <b style="color:#94a3b8;">Disclaimer:</b>
        Signals are generated from historical price data and technical indicators for educational
        purposes only. Not financial advice. Always do your own research.
    </div>
    """, unsafe_allow_html=True)


    # ── Download ──
    st.markdown("### 💾 Export")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Download Forecast CSV",
            data=fc_df.to_csv(index=False),
            file_name=f"{symbol}_forecast_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    with col2:
        st.download_button(
            "📥 Download Historical Data CSV",
            data=df.to_csv(),
            file_name=f"{symbol}_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    # ── Footer ──
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;color:#475569;font-size:0.8rem;padding:0.5rem 0;">
        Built by <b>Umair Kashif</b> · MCA, Manipal Institute of Technology ·
        <a href="https://github.com/kashifumair125" style="color:#a78bfa;">GitHub</a> ·
        <a href="https://linkedin.com/in/umair-kashif" style="color:#a78bfa;">LinkedIn</a>
        <br><br>
        ⚠️ For educational purposes only. Not financial advice.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()