"""
Global Application Configurations and Constants.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables if .env exists
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Screener Thresholds
MIN_LTP = 30.0         # Minimum Last Traded Price in INR
MAX_LTP = 500.0        # Maximum Last Traded Price in INR
MIN_BID_QTY = 1000000  # Minimum Bid Quantity (10 Lakhs = 1,000,000)
MIN_ASK_QTY = 1000000  # Minimum Ask Quantity (10 Lakhs = 1,000,000)

# Technical Indicators Config
SMMA_SHORT_PERIOD = 20   # Fast SMMA period
SMMA_LONG_PERIOD = 120   # Slow SMMA period

# ETQ & Rolling Windows (in seconds)
ETQ_5M_SECONDS = 300     # 5 minutes
ETQ_20M_SECONDS = 1200   # 20 minutes
ETQ_60M_SECONDS = 3600   # 60 minutes

AVG_PRICE_20M_SECONDS = 1200
AVG_PRICE_60M_SECONDS = 3600

LTQ_FAST_WINDOW_SECONDS = 120  # 2 minutes for fast LTQ average
LTQ_SLOW_WINDOW_SECONDS = 300  # 5 minutes for slow LTQ average

# UI Refresh Settings
UI_REFRESH_INTERVAL_MS = 1000  # Live Dashboard table refresh frequency

# Broker Defaults & Mode
DEFAULT_MODE = "MOCK"  # "MOCK", "ANGEL_ONE", "FYERS"

# Angel One Credentials
ANGEL_API_KEY = os.getenv("ANGEL_API_KEY", "")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE", "")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD", "")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET", "")

# Fyers Credentials
FYERS_CLIENT_ID = os.getenv("FYERS_CLIENT_ID", "")
FYERS_SECRET_KEY = os.getenv("FYERS_SECRET_KEY", "")
FYERS_REDIRECT_URI = os.getenv("FYERS_REDIRECT_URI", "http://127.0.0.1:5000/login")
FYERS_ACCESS_TOKEN = os.getenv("FYERS_ACCESS_TOKEN", "")

# Machine Learning Config
MODEL_FILE_PATH = BASE_DIR / "app" / "ml" / "trained_model.joblib"
ACCEPTANCE_THRESHOLD_CONFIDENCE = 0.55  # Minimum probability to accept crossover signal

# Sample stock universe for mock simulation mode
MOCK_STOCK_UNIVERSE = [
    {"symbol": "TATAMOTORS", "company": "Tata Motors Ltd", "base_ltp": 445.50},
    {"symbol": "SBIN", "company": "State Bank of India", "base_ltp": 485.20},
    {"symbol": "YESBANK", "company": "Yes Bank Ltd", "base_ltp": 38.40},
    {"symbol": "IDEA", "company": "Vodafone Idea Ltd", "base_ltp": 34.10},
    {"symbol": "ZOMATO", "company": "Zomato Ltd", "base_ltp": 165.80},
    {"symbol": "PNB", "company": "Punjab National Bank", "base_ltp": 98.60},
    {"symbol": "TATASTEEL", "company": "Tata Steel Ltd", "base_ltp": 142.30},
    {"symbol": "ITC", "company": "ITC Ltd", "base_ltp": 420.75},
    {"symbol": "GAIL", "company": "GAIL (India) Ltd", "base_ltp": 185.30},
    {"symbol": "BEL", "company": "Bharat Electronics Ltd", "base_ltp": 275.40},
    {"symbol": "NHPC", "company": "NHPC Ltd", "base_ltp": 88.90},
    {"symbol": "SJVN", "company": "SJVN Ltd", "base_ltp": 115.20},
    {"symbol": "IRFC", "company": "Indian Railway Finance Corp", "base_ltp": 158.40},
    {"symbol": "BHEL", "company": "Bharat Heavy Electricals", "base_ltp": 290.10},
    {"symbol": "UNIONBANK", "company": "Union Bank of India", "base_ltp": 132.50},
    {"symbol": "NMDC", "company": "NMDC Ltd", "base_ltp": 225.80},
    {"symbol": "BANKBARODA", "company": "Bank of Baroda", "base_ltp": 245.90},
    {"symbol": "IOB", "company": "Indian Overseas Bank", "base_ltp": 62.30},
    {"symbol": "CENTRALBK", "company": "Central Bank of India", "base_ltp": 58.70},
    {"symbol": "SUZLON", "company": "Suzlon Energy Ltd", "base_ltp": 68.50},
    {"symbol": "EXIDEIND", "company": "Exide Industries Ltd", "base_ltp": 480.20},
    {"symbol": "SUBEX", "company": "Subex Ltd", "base_ltp": 35.80},
    {"symbol": "SOUTHBANK", "company": "South Indian Bank", "base_ltp": 31.40},
    {"symbol": "UCOBANK", "company": "UCO Bank", "base_ltp": 49.60},
    {"symbol": "IDFCFIRSTB", "company": "IDFC First Bank Ltd", "base_ltp": 78.30},
    {"symbol": "HINDPETRO", "company": "Hindustan Petroleum Corp", "base_ltp": 385.60},
    {"symbol": "GMRINFRA", "company": "GMR Airports Infrastructure", "base_ltp": 92.10},
    {"symbol": "MANAPPURAM", "company": "Manappuram Finance Ltd", "base_ltp": 195.40},
    {"symbol": "NATIONALUM", "company": "National Aluminium Co", "base_ltp": 178.90},
    {"symbol": "RENUKA", "company": "Shree Renuka Sugars Ltd", "base_ltp": 44.70},
]
