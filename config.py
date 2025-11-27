"""
Konfigurasi dan Konstanta Global
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
    "users": {
        "rendy": {
            "password": "123456",
            "level": "admin",
            "tanggal_gabung": "2024-01-01 09:00:00",
            "wallets": {}
        }
    },
    "harga_pasar": {
        "BTC": 43500.00,
        "ETH": 2280.00,
        "BNB": 315.50,
        "SOL": 98.75,
        "ADA": 0.52,
        "XRP": 0.61,
        "DOGE": 0.087,
        "MATIC": 0.89
    },
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
}