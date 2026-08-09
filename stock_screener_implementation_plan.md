# Implementation Plan: AI/ML-Based Stock Market Screening & Analysis System
**SSG Infotech (Pune) — Assignment 1**

This document outlines the complete architectural, quantitative, and software engineering design for the **AI/ML-Based Stock Market Screening and Analysis System**. The system performs real-time NSE stock screening, calculates SMMA(20) & SMMA(120) indicators, tracks 5m/20m/60m Exchange Traded Quantity (ETQ) & average prices, monitors top-of-book market depth, predicts trade profitability using a Quantitative ML Classifier, and displays real-time updates via a PyQt6 live tabular dashboard and standalone `.exe`.

---

## 1. Core Assumptions & Parameters

- **Broker API Abstraction**: Support for **Angel One SmartAPI** and **Fyers API (v3)** behind a unified broker interface, alongside an offline **Mock / Replay Simulator Engine** for non-trading hours and demo recording.
- **SMMA Aggregation Timeframe**: Ticks are aggregated into **1-minute OHLC bars**. SMMA(20) and SMMA(120) are calculated on bar closing prices to ensure consistent indicator lookback across different stock liquidity profiles.
- **Liquidity Filter**: Filter stocks where **Best Bid Quantity > 10,00,000 (10 Lakhs)** AND **Best Ask Quantity > 10,00,000 (10 Lakhs)**.
- **Price Range Filter**: Include only NSE equity stocks with **₹30 ≤ Last Traded Price (LTP) ≤ ₹500**.
- **SMMA(120) Warm-up**: Seeding initial bar buffers from historical candles to ensure SMMA(120) is active immediately upon system launch.

---

## 2. Architecture & Data Flow

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
                       AI/ML Quantitative Layer
              Features: LTQ 2m/5m Ratio, Depth Imbalance,
                 SMMA Spread, Volume Surge & Momentum
                                   │
                 ┌─────────────────┴─────────────────┐
                 ▼                                   ▼
          Prediction Engine                   Explanatory Engine
       ACCEPTED / REJECTED                  SHAP & Feature Driver
       Confidence Score %                    Natural Language "Why"
                 │                                   │
                 └─────────────────┬─────────────────┘
                                   │
                                   ▼
                     PyQt6 Real-Time Live Dashboard
            Live Table (1 row/stock) + AI Detail Drawer + Chart
```

---

## 3. Data Acquisition & Broker Adapters

Abstract broker interactions using `MarketDataAdapter` base class (`app/data/broker_base.py`):

```python
class MarketDataAdapter(ABC):
    @abstractmethod
    def symbol_universe(self) -> list[str]: ...
    @abstractmethod
    def bulk_quote(self, symbols: list[str]) -> dict[str, Quote]: ...
    @abstractmethod
    def subscribe_ticks(self, symbols: list[str], on_tick: Callable[[Tick], None]) -> None: ...
    @abstractmethod
    def historical_candles(self, symbol: str, interval: str, start, end) -> pd.DataFrame: ...
```

1. **Angel One Adapter (`app/data/angel_one.py`)**:
   - Uses `smartapi-python`, `pyotp`, and `websocket-client`.
   - Authenticates via TOTP & generates session tokens.
   - Fetches Scrip Master for NSE equity tokens (`exch_seg == "NSE"`).
   - Subscribes to `SmartWebSocketV2` mode 3 (SnapQuote) for LTP, LTQ, and top-of-book depth.
2. **Fyers Adapter (`app/data/fyers.py`)**:
   - Uses `fyers-apiv3` SDK.
   - Handles OAuth token refresh and REST quote calls.
   - Subscribes to Fyers WebSockets (`SymbolUpdate` and `DepthUpdate`).
3. **Mock & Replay Engine (`app/data/mock_broker.py`)**:
   - Generates high-fidelity realistic live market ticks, order book depth shifts, LTQ volume bursts, and SMMA crossover events for 50+ popular NSE stocks.
   - Replays historical or simulated tick streams for off-market hours testing and screen recording.

---

## 4. Real-Time Indicator & ETQ Engine

All metrics update in $O(1)$ time per tick update:

- **SMMA Computation** (Wilder's Smoothed Moving Average):
  $$SMMA_1 = SMA_N$$
  $$SMMA_t = \frac{SMMA_{t-1} \times (N - 1) + Price_t}{N}$$
- **Rolling ETQ Engine**:
  - `ETQ_5m`: Volume executed in last 5 minutes.
  - `ETQ_20m`: Volume executed in last 20 minutes.
  - `ETQ_60m`: Volume executed in last 60 minutes.
- **Rolling Average Prices**:
  - `AvgPrice_20m`: Time/Volume-weighted average price over last 20 minutes.
  - `AvgPrice_60m`: Time/Volume-weighted average price over last 60 minutes.
- **LTQ Dynamics**:
  - `LTQ_2m_avg`: Average Last Traded Quantity over last 2 minutes.
  - `LTQ_5m_avg`: Average Last Traded Quantity over last 5 minutes.
  - `LTQ Surge Ratio` = $\frac{\text{LTQ}_{2m\_avg}}{\text{LTQ}_{5m\_avg}}$.

---

## 5. Crossover Detection & Trade Execution Logic

- **Buy Signal**: SMMA(20) crosses above SMMA(120).
- **Sell Signal**: SMMA(20) crosses below SMMA(120).
- **Trade Execution Protocol**:
  - **Buy Trade (Long)**: Enter at LTP on Buy Signal. Exit at LTP on Sell Signal.
    $$\text{Profit/Loss} = \text{Sell LTP} - \text{Buy LTP}$$
  - **Sell Trade (Short)**: Enter at LTP on Sell Signal. Exit at LTP on Buy Signal.
    $$\text{Profit/Loss} = \text{Sell LTP} - \text{Buy LTP}$$
- Consecutive opposite signals form closed trade records with verified P/L calculation.

---

## 6. AI/ML Quantitative Model & Feature Engineering

- **Model Architecture**: `RandomForestClassifier` and `GradientBoostingClassifier` trained on market tick and signal features.
- **Extracted Feature Set**:
  1. `ltq_surge_ratio`: $\text{LTQ}_{2m\_avg} / \text{LTQ}_{5m\_avg}$ (Detects institutional volume bursts).
  2. `bid_ask_qty_ratio`: $\frac{\text{Bid Quantity}}{\text{Ask Quantity}}$ (Measures order book buy/sell pressure).
  3. `etq_growth_rate`: $\text{ETQ}_{5m} / \text{ETQ}_{20m}$ (Accelerating market activity).
  4. `smma_spread_pct`: $\frac{\text{SMMA}_{20} - \text{SMMA}_{120}}{\text{SMMA}_{120}}$ (Crossover slope and trend momentum).
  5. `price_vs_avg20`: $\frac{\text{LTP} - \text{AvgPrice}_{20m}}{\text{AvgPrice}_{20m}}$ (Mean reversion / stretch).
  6. `spread_pct`: $\frac{\text{Ask Price} - \text{Bid Price}}{\text{LTP}}$ (Bid-Ask spread width).
- **Model Output**:
  - `Decision`: **ACCEPTED** (High probability of profit) vs **REJECTED** (High risk of failure / avoid trade).
  - `Confidence`: Model predicted probability (0% to 100%).
  - `AI Explanation`: Human-readable natural language breakdown generated from feature contributions (e.g. *"ACCEPTED: Strong LTQ surge ratio (2.4x) with dominant Bid Depth (>1.2M) supporting upward momentum."*).

---

## 7. PyQt6 Live Tabular Dashboard

A desktop GUI built with **PyQt6** using a modern Dark Mode style (`app/ui/`):

- **Header Metric Cards**: Total Screened Stocks, Active Buy/Sell Signals, AI Win Rate %, Top Volume Gainer.
- **Live Tabular Grid**:
  - Columns: `Symbol`, `LTP (₹)`, `Bid Price`, `Bid Qty (Lakhs)`, `Ask Price`, `Ask Qty (Lakhs)`, `SMMA(20)`, `SMMA(120)`, `Signal`, `5m ETQ`, `20m ETQ`, `60m ETQ`, `20m Avg Price`, `60m Avg Price`, `Liquidity Status`, `AI Decision`, `Confidence (%)`.
- **AI Explanation & Signal Details Drawer**: Panel displaying feature contributions, trade entry/exit history, and natural language rationale.
- **Interactive SMMA Chart Canvas**: Real-time SMMA(20) & SMMA(120) visual chart (`pyqtgraph` / `matplotlib`).
- **Settings Dialog**: Modal to toggle between Angel One API, Fyers API, and Mock Simulator, with credential management.

---

## 8. Executable (.exe) Packaging & Credential Hygiene

- **PyInstaller Packaging**: Standard build script `build_exe.py` compiling the application into `dist/StockMarketScreenerAI.exe`.
- **Security & Hygiene**:
  - All broker API keys, secrets, TOTP seeds, and passwords stored in `.env` / `config.ini` (git-ignored).
  - Clean config template provided (`config.template.ini`) with zero secrets exposed.

---

## 9. Project Directory Layout

```
Stock Market Screening and Analysis System/
├── app/
│   ├── __init__.py
│   ├── config.py             # App configurations, thresholds, styling constants
│   ├── data/
│   │   ├── __init__.py
│   │   ├── broker_base.py    # MarketDataAdapter abstract base class
│   │   ├── angel_one.py      # Angel One SmartAPI client implementation
│   │   ├── fyers.py          # Fyers API v3 client implementation
│   │   ├── mock_broker.py    # High-fidelity live market tick simulator
│   │   └── data_feed.py      # Real-time tick & market depth aggregator
│   ├── indicators/
│   │   ├── __init__.py
│   │   ├── smma.py           # Streaming SMMA (20, 120) computation engine
│   │   ├── etq_engine.py     # Rolling ETQ (5m, 20m, 60m) & Avg Price engine
│   │   └── screener.py       # Stock price (₹30-₹500) & liquidity (>10L Bid/Ask Qty) screener
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── feature_extractor.py # LTQ ratios, depth ratios, SMMA spread, momentum features
│   │   ├── model.py          # Scikit-learn Classifier (Random Forest / Gradient Boosting)
│   │   └── explainer.py      # Feature contribution & natural language explanation engine
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── styles.py         # Modern dark mode QSS theme
│   │   ├── dashboard.py      # Main PyQt6 Live Dashboard Window
│   │   ├── components/       # Metric cards, Stock table, AI drawer, Chart widget
│   │   └── settings_dialog.py # Broker credentials & simulation settings modal
│   └── main.py               # Application entry point
├── tests/
│   ├── test_indicators.py    # Unit tests for SMMA, ETQ, and Screener
│   ├── test_ml.py            # Unit tests for Feature Extractor and ML Model
│   └── test_broker.py        # Unit tests for broker data feeds and simulation
├── build_exe.py              # Script to build standalone Windows .exe using PyInstaller
├── requirements.txt          # Python dependencies
└── README.md                 # Setup, broker configuration, and usage guide
```

---

## 10. Execution & Verification Checklist

1. **Unit & Integration Tests**: Run `pytest tests/` to verify indicator math, screening logic, feature extraction, and ML classifier predictions.
2. **Dashboard Verification**: Launch `python app/main.py` in Mock Simulator mode to verify real-time table auto-refresh, SMMA crossovers, AI explanations, and chart updates.
3. **Broker Connection**: Test credential input and session handshake for Angel One SmartAPI and Fyers API v3.
4. **Executable Compilation**: Run `python build_exe.py` to generate `StockMarketScreenerAI.exe` and test launch.
