# 📈 Indian Stock Price Prediction System

[![HuggingFace Spaces](https://img.shields.io/badge/🤗%20HuggingFace-Spaces-orange)](https://huggingface.co/spaces/kashii1/indian-stock-prediction)
[![Docker](https://img.shields.io/badge/Docker-Hub-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/r/kashii1/indian-stock-prediction)
[![CI/CD](https://github.com/kashifumair125/Indian-Stock-Price-Prediction/actions/workflows/deploy.yml/badge.svg)](https://github.com/kashifumair125/Indian-Stock-Price-Prediction/actions)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)


> **ML-powered price prediction for 30+ Indian NSE stocks** — three scikit-learn models, 30+ engineered features, interactive Streamlit dashboard.

🔗 **[Live Demo HuggingFace →](https://huggingface.co/spaces/kashii1/indian-stock-prediction)**
🔗 **[Live Demo GCP →](https://indian-stock-prediction-1078044545456.asia-south1.run.app)**

---

## ✨ Features

| Feature | Details |
|---|---|
| **ML Models** | Ridge Regression · Random Forest · Gradient Boosting |
| **Features** | RSI · MACD · Bollinger Bands · ATR · Volume ratio · 5 lag features |
| **Forecast** | Up to 60-day future price prediction |
| **Stocks** | 30+ NSE-listed companies across IT, Banking, Energy, FMCG, Auto, Pharma |
| **Charts** | Candlestick · Volume · RSI · MACD · Model comparison |
| **Export** | Download forecast & historical data as CSV |

---

## 🚀 Quick Start

### Run locally
```bash
git clone https://github.com/kashifumair125/Indian-Stock-Price-Prediction.git
cd Indian-Stock-Price-Prediction
pip install -r requirements.txt
streamlit run app.py
```

### Run with Docker
```bash
docker pull kashifumair125/indian-stock-prediction:latest
docker run -p 8080:8080 kashifumair125/indian-stock-prediction:latest
# Open http://localhost:8080
```

---

## 🏗️ Architecture

```
Indian-Stock-Price-Prediction/
├── app.py                          # Streamlit app (single file)
├── requirements.txt                # Lean deps — scikit-learn only
├── Dockerfile                      # Container for Docker Hub & GCP Cloud Run
├── .streamlit/
│   └── config.toml                 # Dark theme + server config
└── .github/
    └── workflows/
        └── deploy.yml              # CI/CD — auto-build Docker on push to main
```

---

## ⚙️ ML Pipeline

```
yfinance API → raw OHLCV data
     ↓
Feature Engineering (30+ features)
  ├── Technical: RSI, MACD, Bollinger Bands, ATR, EMA/SMA
  ├── Volume:    Volume ratio vs 20D avg
  ├── Price:     Returns, log returns, volatility, HL %
  └── Lags:      1, 2, 3, 5, 10 day lookback
     ↓
RobustScaler → Train / Test split (80/20, time-ordered)
     ↓
3 models trained in parallel
  ├── Ridge Regression       (baseline, fast)
  ├── Random Forest          (bagging ensemble)
  └── Gradient Boosting      (boosting ensemble)
     ↓
Best model (lowest RMSE) → iterative future forecast
```

---

## 🌐 Deployment

### HuggingFace Spaces *(live)*
Deployed at: `https://huggingface.co/spaces/kashii1/indian-stock-prediction`

Space config (`README.md` header in the Space repo):
```yaml
---
title: Indian Stock Prediction
emoji: 📈
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: 1.32.0
app_file: app.py
pinned: true
---
```

### Docker Hub
```bash
# Pull
docker pull kashifumair125/indian-stock-prediction:latest

# Run
docker run -p 8080:8080 kashifumair125/indian-stock-prediction:latest
```

Auto-built via GitHub Actions on every push to `main`.

### GCP Cloud Run *(optional next step)*
```bash
gcloud run deploy indian-stock-prediction \
  --image docker.io/kashifumair125/indian-stock-prediction:latest \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --port 8080
```

---

## 📊 Model Performance  *(example — TCS.NS, 1Y)*

| Model | RMSE (₹) | MAE (₹) | R² | MAPE |
|---|---|---|---|---|
| Gradient Boosting | ~18 | ~12 | ~0.97 | ~0.5% |
| Random Forest | ~22 | ~15 | ~0.96 | ~0.6% |
| Ridge Regression | ~45 | ~35 | ~0.89 | ~1.2% |

*Results vary by stock and time period.*

---

## 🛠️ Tech Stack

```
Language    Python 3.11
ML          scikit-learn 1.3+
Data        yfinance, pandas, numpy
Viz         Plotly, Streamlit
Container   Docker
CI/CD       GitHub Actions
Hosting     HuggingFace Spaces · Docker Hub · GCP Cloud Run
```

---

## 👤 Author

**Umair Kashif**
MCA Graduate · Manipal Institute of Technology (2025)

- 🔗 [LinkedIn](https://linkedin.com/in/umair-kashif)
- 🐙 [GitHub](https://github.com/kashifumair125)
- 📄 [Research Paper — Transformer-based Sentiment Analysis (ICIST 2025)](https://huggingface.co/spaces/kashii1/mas-rag)

---

> ⚠️ **Disclaimer:** For educational purposes only. Not financial advice.
