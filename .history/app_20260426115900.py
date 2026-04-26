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
    #MainMenu, footer, header { visibility: hidden; }

    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .hero h1 { font-size: 2rem; margin: 0 0 0.4rem 0; }
    .hero p  { font-size: 1rem; margin: 0; opacity: 0.9; }

    .card {
        background: #1e2130;
        border: 1px solid #2d3250;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .card h4 { color: #a78bfa; margin: 0 0 0.3rem 0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .card .val { font-size: 1.6rem; font-weight: 700; color: #f1f5f9; }
    .card .delta { font-size: 0.9rem; margin-top: 0.2rem; }
    .pos { color: #34d399; }
    .neg { color: #f87171; }
    .neu { color: #94a3b8; }

    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.4rem;
    }
    .badge-buy  { background: #064e3b; color: #34d399; }
    .badge-sell { background: #450a0a; color: #f87171; }
    .badge-hold { background: #1c1917; color: #a8a29e; }

    div[data-testid="stSidebar"] {
        background: #0f1117;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        width: 100%;
    }
    .stButton > button:hover { opacity: 0.9; }
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

    # ── Hero ──
    st.markdown(f"""
    <div class="hero">
        <h1>📈 Indian Stock Price Prediction</h1>
        <p>ML-powered analysis for <strong>{STOCKS.get(symbol, symbol)}</strong>
           ({symbol}) · {period} data · {pred_days}-day forecast</p>
    </div>
    """, unsafe_allow_html=True)

    if not run:
        # Welcome state
        cols = st.columns(3)
        infos = [
            ("🤖", "3 ML Models", "Ridge · Random Forest · Gradient Boosting"),
            ("📊", "30+ Features", "RSI · MACD · Bollinger Bands · Lag features"),
            ("🔮", "Future Forecast", f"Up to 60-day price prediction"),
        ]
        for col, (icon, title, desc) in zip(cols, infos):
            with col:
                st.markdown(f"""
                <div class="card" style="text-align:center;">
                    <div style="font-size:2rem;">{icon}</div>
                    <div class="val" style="font-size:1.1rem;margin:0.4rem 0;">{title}</div>
                    <div style="color:#64748b;font-size:0.85rem;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
        st.info("👈  Select a stock and click **Run Analysis** to begin.")
        return

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
    c = df["Close"]
    current  = c.iloc[-1]
    prev     = c.iloc[-2]
    change   = current - prev
    chg_pct  = change / prev * 100
    sign     = "pos" if change >= 0 else "neg"
    arrow    = "▲" if change >= 0 else "▼"

    cols = st.columns(5)
    metrics = [
        ("Current Price",    f"₹{current:,.2f}", f"{arrow} ₹{abs(change):.2f} ({chg_pct:+.2f}%)", sign),
        ("52W High",         f"₹{raw['High'].max():,.2f}", "", "neu"),
        ("52W Low",          f"₹{raw['Low'].min():,.2f}", "", "neu"),
        ("Avg Volume (30D)", f"{int(df['Volume'].tail(30).mean()):,}", "", "neu"),
        ("Volatility (Ann)", f"{df['Returns'].std() * np.sqrt(252) * 100:.1f}%", "", "neu"),
    ]
    for col, (label, val, delta, cls) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="card">
                <h4>{label}</h4>
                <div class="val">{val}</div>
                <div class="delta {cls}">{delta}</div>
            </div>
            """, unsafe_allow_html=True)

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