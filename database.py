"""
Database Operations
Semua operasi CRUD database JSON
"""

import json
import os
from config import DB_FILE, DEFAULT_DB

# Global database
db = {}


def load_database():
    """Load database dari file JSON"""
    global db
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            db = json.load(f)
    else:
        db = DEFAULT_DB.copy()
        save_database()
    return db


def save_database():
    """Simpan database ke file JSON"""
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)


def get_user(username):
    """Get user tertentu"""
    return db.get("users", {}).get(username)


def add_user(username, user_data):
    """Tambah user baru"""
    if "users" not in db:
        db["users"] = {}
    db["users"][username] = user_data
    save_database()


def user_exists(username):
    """Cek apakah username sudah ada"""
    return username in db.get("users", {})


def get_user_wallet(username):
    """Get wallet user"""
    user = get_user(username)
    if user:
        return user.get("wallets", {})
    return {}


def update_user_wallet(username, wallet_data):
    """Update wallet user"""
    if username in db.get("users", {}):
        db["users"][username]["wallets"] = wallet_data
        save_database()
        return True
    return False


def get_market_prices():
    """Get harga pasar"""
    return db.get("market_prices", {})


def update_market_price(symbol, price):
    """Update harga pasar"""
    if "market_prices" not in db:
        db["market_prices"] = {}
    db["market_prices"][symbol] = price
    save_database()


def get_local_coins():
    """Get koin lokal"""
    return db.get("local_coins", [])


def add_local_coin(coin_data):
    """Tambah koin lokal"""
    if "local_coins" not in db:
        db["local_coins"] = []
    db["local_coins"].append(coin_data)
    save_database()


def update_local_coin(symbol, updates):
    """Update koin lokal"""
    for coin in db.get("local_coins", []):
        if coin["symbol"] == symbol:
            coin.update(updates)
            save_database()
            return True
    return False


def delete_local_coin(symbol):
    """Hapus koin lokal"""
    local_coins = db.get("local_coins", [])
    db["local_coins"] = [c for c in local_coins if c["symbol"] != symbol]
    
    # Hapus dari market_prices juga
    if symbol in db.get("market_prices", {}):
        del db["market_prices"][symbol]
    
    save_database()
    return True


def get_transactions():
    """Get semua transaksi"""
    return db.get("transactions", [])


def add_transaction(transaction_data):
    """Tambah transaksi baru"""
    if "transactions" not in db:
        db["transactions"] = []
    db["transactions"].append(transaction_data)
    save_database()


def get_coin_by_symbol(symbol):
    """Get koin berdasarkan symbol"""
    for coin in db.get("local_coins", []):
        if coin["symbol"] == symbol:
            return coin
    return None


def coin_symbol_exists(symbol):
    """Cek apakah symbol sudah ada"""
    for coin in db.get("local_coins", []):
        if coin["symbol"] == symbol:
            return True
    return symbol in db.get("market_prices", {})