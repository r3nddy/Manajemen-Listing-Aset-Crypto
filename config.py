"""
<<<<<<< HEAD
Konfigurasi dan Konstanta Global
Configuration & Constants
"""

# ==================== FILE DATABASE ====================
file_database = "crypto_data.json"

# ==================== API COINGECKO ====================
id_kripto = ['bitcoin', 'ethereum', 'binancecoin', 'solana', 'cardano', 'ripple', 'dogecoin', 'matic-network']
mata_uang = 'usd'

peta_tampilan_kripto = {
    'bitcoin': {'nama': 'Bitcoin', 'symbol': 'BTC'},
    'ethereum': {'nama': 'Ethereum', 'symbol': 'ETH'},
    'binancecoin': {'nama': 'BNB', 'symbol': 'BNB'},
    'solana': {'nama': 'Solana', 'symbol': 'SOL'},
    'cardano': {'nama': 'Cardano', 'symbol': 'ADA'},
    'ripple': {'nama': 'XRP', 'symbol': 'XRP'},
    'dogecoin': {'nama': 'Dogecoin', 'symbol': 'DOGE'},
    'matic-network': {'nama': 'Polygon', 'symbol': 'MATIC'},
}

# ==================== DATABASE DEFAULT ====================
database_default = {
=======
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
>>>>>>> 21a3df592df0354eed3dfa9e6d6437cbc0e0a374
    "users": {
        "rendy": {
            "password": "123456",
            "level": "admin",
<<<<<<< HEAD
            "tanggal_gabung": "2024-01-01 09:00:00",
=======
            "join_date": "2024-01-01 09:00:00",
>>>>>>> 21a3df592df0354eed3dfa9e6d6437cbc0e0a374
            "wallets": {
                "USDT": 10000.00,
                "BTC": 0.5,
                "ETH": 2.0,
                "BNB": 10.0
            }
        }
    },
<<<<<<< HEAD
    "harga_pasar": {
=======
    "market_prices": {
>>>>>>> 21a3df592df0354eed3dfa9e6d6437cbc0e0a374
        "BTC": 43500.00,
        "ETH": 2280.00,
        "BNB": 315.50,
        "SOL": 98.75,
        "ADA": 0.52,
        "XRP": 0.61,
        "DOGE": 0.087,
        "MATIC": 0.89
    },
<<<<<<< HEAD
    "koin_lokal": [],
    "orders": [],
    "transaksi": []
}

# ==================== SECURITY ====================
min_panjang_username = 4
min_panjang_password = 6
max_percobaan_login = 3
detik_lockout = 10

# ==================== BONUS ====================
usdt_awal_user = 10000.00

SESSION = {
    'current_user': None,
    'current_level': None,
    'market_data': {},
    'market_loaded': False,
    'market_timestamp': None
=======
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
>>>>>>> 21a3df592df0354eed3dfa9e6d6437cbc0e0a374
}