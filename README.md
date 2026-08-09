# AI/ML-Based Stock Market Screening and Analysis System

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-PyQt6-green.svg)](https://www.qt.io/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

A real-time Python desktop application for screening NSE-listed stocks, computing technical indicators (SMMA 20/120), tracking Exchange Traded Quantity (ETQ) & rolling average prices, evaluating crossover signals via a Quantitative ML Classifier, optimizing asset allocations with a Genetic Algorithm, and providing Indian Capital Gains Tax advisory.

---

## 🚀 Key System Capabilities

### 1. Real-Time Stock Screening & Liquidity Funnel
- **Price Filter**: $₹30 \le \text{LTP} \le ₹500$.
- **Liquidity Filter**: Best Bid Quantity $> 10,00,000$ (10 Lakhs) AND Best Ask Quantity $> 10,00,000$ (10 Lakhs).

### 2. Streaming Technical Indicators & Crossover Logic
- Streaming **SMMA (20)** (Smoothed Moving Average) fast line.
- Streaming **SMMA (120)** slow line.
- Automatic Buy/Sell crossover signal detection:
  - **Buy Signal**: SMMA(20) crosses above SMMA(120).
  - **Sell Signal**: SMMA(20) crosses below SMMA(120).
  - Trade P/L formula: $\text{Profit/Loss} = \text{Sell LTP} - \text{Buy LTP}$.

### 3. Exchange Traded Quantity (ETQ) & Average Price Engine
- $O(1)$ rolling time window volume aggregation for **Last 5 minutes**, **Last 20 minutes**, and **Last 60 minutes**.
- Rolling Average Price (LTP) calculation over **Last 20 minutes** and **Last 60 minutes**.
- LTQ dynamics tracker evaluating the ratio of **2-minute average LTQ vs 5-minute average LTQ** to capture institutional volume bursts.

### 4. Quantitative AI/ML Model & Strategy Explainer
- Machine Learning Classifier (`RandomForestClassifier`) trained on crossover dynamics.
- Predicts whether an SMMA crossover signal should be **ACCEPTED** (Profitable) or **REJECTED** (High false crossover risk).
- Reports prediction confidence score % (0 - 100%).
- Generates plain-English natural language rationale explaining key market drivers (LTQ volume surge ratio, Bid/Ask depth support, SMMA gap divergence, ETQ acceleration).

### 5. 🧬 Genetic Algorithm (GA) Portfolio Optimizer
- **Cardinality-Constrained Asset Allocation**: Selects top $K$ optimal assets (e.g. $K=5$) from screened liquid stocks.
- **Risk-Adjusted Maximization**: Maximizes the annualized **Sharpe Ratio** ($\text{Sharpe} = \frac{R_p - R_f}{\sigma_p}$).
- **Key Metrics**: Annualized Return %, Annualized Volatility %, Sharpe Ratio, and exact percentage weight allocation per asset.

### 6. 🏛 Indian Equity Income Tax Advisory
- **Section 111A STCG Tax**: Calculates Short-Term Capital Gains tax @ 20% for trades held $< 12$ months.
- **Section 112A LTCG Tax**: Calculates Long-Term Capital Gains tax @ 12.5% on gains exceeding the ₹1,25,000 exemption limit.
- **STT (Securities Transaction Tax)**: Calculates turnover STT (0.1%).
- **Tax Optimization Advice**: Generates tax-loss harvesting recommendations on closed trades.

### 7. 💬 Natural Language SQL Analytics Agent
- Translates plain-English queries into safe, read-only SQL queries over live market screening data and trade logs.
- Includes preset quick-access queries (*"Top 5 ETQ Volume Stocks"*, *"Active BUY Signals"*, *"Screened Liquid Universe"*).

### 8. PyQt6 Real-Time Live Desktop Dashboard
- Modern Dark Mode aesthetic with auto-refreshing live stock table (1 row per stock).
- KPI Summary Cards bar (Total Universe, Screened Liquid, Active Signals, AI Acceptance Rate).
- **4 Tab Panels**:
  - `🤖 AI Analysis & Strategy`: Feature metrics, AI rationale, and trade execution log.
  - `📈 Live SMMA Chart`: Streaming price curve canvas (`pyqtgraph`).
  - `🧬 GA Portfolio Optimizer`: Asset allocation weights and risk metrics.
  - `📊 NL-SQL Analytics & Tax`: Plain-English search and Indian tax advisory breakdown.

### 9. Multi-Broker Connectors & Offline Replay Simulator
- Native adapters for **Angel One SmartAPI** and **Fyers API (v3)**.
- Built-in **High-Fidelity Mock Simulator** providing realistic live market ticks, order book depth shifts, and SMMA crossovers for off-market hours testing and video demonstrations.

---

## 📐 Architecture & Data Flow

```
                     NSE Universe (~2,000 Equities)
                                   │
                                   ▼
             Stage 1: Coarse REST Screening (Every 2–5 min)
             Filter: ₹30 ≤ LTP ≤ ₹500 & Bid/Ask Qty > 10,00,000
                                   │
                                   ▼
                   Shortlist Universe (~30–150 Stocks)
                                   │
                                   ▼
            Stage 2: Real-Time WebSocket Feed (Ticks & Depth)
       Angel One SmartAPI / Fyers API v3 / High-Fidelity Mock Engine
                                   │
                                   ▼
                          Real-Time Engine
             ┌─────────────────────┼─────────────────────┐
             ▼                     ▼                     ▼
       Indicator Engine     ETQ & Avg Price       Crossover Engine
       SMMA(20) / (120)     5m, 20m, 60m ETQ    SMMA20 × SMMA120 Flip
             │              20m, 60m Avg Price           │
             └─────────────────────┬─────────────────────┘
                                   │
                                   ▼
                        Quantitative AI Layer
              Features: LTQ 2m/5m Ratio, Depth Imbalance,
                 SMMA Spread, Volume Surge & Momentum
                                   │
                 ┌─────────────────┴─────────────────┐
                 ▼                                   ▼
          Prediction Engine                   Explanatory Engine
       ACCEPTED / REJECTED                  Feature Driver Rationale
       Confidence Score %                    Natural Language "Why"
                                   │
                                   ▼
                PyQt6 Live Dashboard & Analytics Tabs
    ┌───────────────────────┬───────────────────────┬───────────────────────┐
    ▼                       ▼                       ▼                       ▼
 Stock Table Grid     AI Drawer & Chart      GA Portfolio Opt       NL-SQL & Tax Engine
```

---

## 📂 Project Directory Structure

```
Stock Market Screening and Analysis System/
├── app/
│   ├── __init__.py
│   ├── config.py             # System thresholds, constants, and parameters
│   ├── data/
│   │   ├── broker_base.py    # Abstract MarketDataAdapter & unified data models (Tick, Quote)
│   │   ├── angel_one.py      # Angel One SmartAPI connector
│   │   ├── fyers.py          # Fyers API v3 connector
│   │   ├── mock_broker.py    # High-fidelity live market tick & depth simulator
│   │   └── data_feed.py      # Data feed manager and tick router
│   ├── indicators/
│   │   ├── smma.py           # Streaming SMMA(20, 120) engine & crossover detector
│   │   ├── etq_engine.py     # Rolling ETQ (5m, 20m, 60m) & Avg Price engine
│   │   └── screener.py       # Stock price & liquidity screening filter
│   ├── ml/
│   │   ├── feature_extractor.py # LTQ ratios, depth balance, SMMA spread feature engine
│   │   ├── model.py          # Random Forest Classifier & confidence predictor
│   │   └── explainer.py      # Human-readable AI trade rationale explainer
│   ├── analytics/
│   │   ├── portfolio_optimizer.py # Genetic Algorithm Portfolio Optimizer
│   │   ├── tax_advisor.py    # Indian Equity Capital Gains Tax Engine (STCG/LTCG/STT)
│   │   └── sql_query_agent.py # Natural Language SQL Query Engine
│   ├── ui/
│   │   ├── styles.py         # PyQt6 modern dark mode QSS theme
│   │   ├── dashboard.py      # Main PyQt6 Live Dashboard Window
│   │   ├── components/       # Table, Metric Cards, AI Drawer, Chart, GA Opt & Tax tabs
│   │   └── settings_dialog.py # Settings modal for broker API credentials
│   └── main.py               # Application entry point
├── tests/
│   ├── test_indicators.py    # Unit tests for SMMA, ETQ, and Screener
│   ├── test_ml.py            # Unit tests for Feature Extractor and ML Predictor
│   ├── test_broker.py        # Unit tests for broker data feeds
│   └── test_analytics.py     # Unit tests for GA Optimizer, Tax Engine & SQL Agent
├── dist/
│   └── StockMarketScreenerAI/
│       └── StockMarketScreenerAI.exe # Standalone Windows Executable
├── build_exe.py              # PyInstaller build script
├── config.template.ini       # Configuration template with placeholder credentials
├── requirements.txt          # Frozen Python dependencies list
└── README.md                 # Project documentation
```

---

## 🛠 Installation & Quick Start

### 1. Initialize Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Application
```bash
python app/main.py
```

---

## 🧪 Running Unit Tests

To execute the automated test suite (13 unit tests):
```bash
pytest tests/ -v
```

---

## 📦 Building Standalone Windows Executable (.exe)

To compile the application into a standalone executable:
```bash
python build_exe.py
```
The compiled binary will be created at: `dist/StockMarketScreenerAI/StockMarketScreenerAI.exe`.

---

## 🔒 Security & Credential Hygiene

All broker API keys, passwords, TOTP secrets, and credentials are kept out of source control. Use `config.template.ini` to set up your environment variables or configure keys via **⚙ Broker Settings** inside the live dashboard.