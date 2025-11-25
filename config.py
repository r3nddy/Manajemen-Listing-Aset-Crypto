"""
Configuration & Constants
Konfigurasi dan konstanta global
"""

# ==================== FILE DATABASE ====================
DB_FILE = "crypto_data.json"

# ==================== API COINGECKO ====================
CRYPTO_IDS = ['bitcoin', 'ethereum', 'binancecoin', 'solana', 'cardano', 'ripple', 'dogecoin', 'matic-network']
VS_CURRENCY = 'usd'

CRYPTO_DISPLAY_MAP = {
    'bitcoin': {'name': 'Bitcoin', 'symbol': 'BTC'},
    'ethereum': {'name': 'Ethereum', 'symbol': 'ETH'},
    'binancecoin': {'name': 'BNB', 'symbol': 'BNB'},
    'solana': {'name': 'Solana', 'symbol': 'SOL'},
    'cardano': {'name': 'Cardano', 'symbol': 'ADA'},
    'ripple': {'name': 'XRP', 'symbol': 'XRP'},
    'dogecoin': {'name': 'Dogecoin', 'symbol': 'DOGE'},
    'matic-network': {'name': 'Polygon', 'symbol': 'MATIC'},
}

# ==================== DATABASE DEFAULT ====================
DEFAULT_DB = {
    "users": {
        "rendy": {
            "password": "123456",
            "level": "admin",
            "join_date": "2024-01-01 09:00:00",
            "wallets": {
                "USDT": 10000.00,
                "BTC": 0.5,
                "ETH": 2.0,
                "BNB": 10.0
            }
        }
    },
    "market_prices": {
        "BTC": 43500.00,
        "ETH": 2280.00,
        "BNB": 315.50,
        "SOL": 98.75,
        "ADA": 0.52,
        "XRP": 0.61,
        "DOGE": 0.087,
        "MATIC": 0.89
    },
    "local_coins": [],
    "orders": [],
    "transactions": []
}

# ==================== SECURITY ====================
MIN_USERNAME_LENGTH = 4
MIN_PASSWORD_LENGTH = 6
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_SECONDS = 10

# ==================== BONUS ====================
USER_INITIAL_USDT = 10000.00

# ==================== SESSION ====================
SESSION = {
    'current_user': None,
    'current_level': None
}