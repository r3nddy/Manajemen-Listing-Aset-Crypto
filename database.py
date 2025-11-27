"""
Modul Database Operations
Semua operasi CRUD database JSON
"""

import json
import os
from config import file_database, database_default

# Global database
db = {}


def muat_database():
    """Load database dari file JSON"""
    try:
        global db
        if os.path.exists(file_database):
            with open(file_database, 'r') as f:
                db = json.load(f)
        else:
            db = database_default.copy()
            simpan_database()
        return db
    except Exception as e:
        print(f"Error saat memuat database: {e}")
        db = database_default.copy()
        return db


def simpan_database():
    """Simpan database ke file JSON"""
    try:
        with open(file_database, 'w') as f:
            json.dump(db, f, indent=4)
    except Exception as e:
        print(f"Error saat menyimpan database: {e}")


def ambil_pengguna(username):
    """Get user tertentu"""
    try:
        return db.get("users", {}).get(username)
    except Exception as e:
        print(f"Error saat mengambil pengguna: {e}")
        return None


def tambah_pengguna(username, data_pengguna):
    """Tambah user baru"""
    try:
        if "users" not in db:
            db["users"] = {}
        db["users"][username] = data_pengguna
        simpan_database()
    except Exception as e:
        print(f"Error saat menambah pengguna: {e}")


def pengguna_ada(username):
    """Cek apakah username sudah ada"""
    try:
        return username in db.get("users", {})
    except Exception:
        return False


def ambil_dompet_pengguna(username):
    """Get wallet user"""
    try:
        pengguna = ambil_pengguna(username)
        if pengguna:
            return pengguna.get("wallets", {})
        return {}
    except Exception as e:
        print(f"Error saat mengambil dompet pengguna: {e}")
        return {}


def perbarui_dompet_pengguna(username, data_dompet):
    """Update wallet user"""
    try:
        if username in db.get("users", {}):
            db["users"][username]["wallets"] = data_dompet
            simpan_database()
            return True
        return False
    except Exception as e:
        print(f"Error saat memperbarui dompet pengguna: {e}")
        return False


def ambil_harga_pasar():
    """Get harga pasar"""
    try:
        return db.get("harga_pasar", {})
    except Exception as e:
        print(f"Error saat mengambil harga pasar: {e}")
        return {}


def perbarui_harga_pasar(symbol, harga):
    """Update harga pasar"""
    try:
        if "harga_pasar" not in db:
            db["harga_pasar"] = {}
        db["harga_pasar"][symbol] = harga
        simpan_database()
    except Exception as e:
        print(f"Error saat memperbarui harga pasar: {e}")


def ambil_koin_lokal():
    """Get koin lokal"""
    try:
        return db.get("koin_lokal", [])
    except Exception as e:
        print(f"Error saat mengambil koin lokal: {e}")
        return []


def tambah_koin_lokal(data_koin):
    """Tambah koin lokal"""
    try:
        if "koin_lokal" not in db:
            db["koin_lokal"] = []
        db["koin_lokal"].append(data_koin)
        simpan_database()
    except Exception as e:
        print(f"Error saat menambah koin lokal: {e}")


def perbarui_koin_lokal(symbol, pembaruan):
    """Update koin lokal"""
    try:
        for koin in db.get("koin_lokal", []):
            if koin["symbol"] == symbol:
                koin.update(pembaruan)
                simpan_database()
                return True
        return False
    except Exception as e:
        print(f"Error saat memperbarui koin lokal: {e}")
        return False


def hapus_koin_lokal(symbol):
    """Hapus koin lokal"""
    try:
        koin_lokal = db.get("koin_lokal", [])
        db["koin_lokal"] = [k for k in koin_lokal if k["symbol"] != symbol]
        
        # Hapus dari harga_pasar juga
        if symbol in db.get("harga_pasar", {}):
            del db["harga_pasar"][symbol]
        
        simpan_database()
        return True
    except Exception as e:
        print(f"Error saat menghapus koin lokal: {e}")
        return False


def ambil_transaksi():
    """Get semua transaksi"""
    try:
        return db.get("transaksi", [])
    except Exception as e:
        print(f"Error saat mengambil transaksi: {e}")
        return []


def tambah_transaksi(data_transaksi):
    """Tambah transaksi baru"""
    try:
        if "transaksi" not in db:
            db["transaksi"] = []
        db["transaksi"].append(data_transaksi)
        simpan_database()
    except Exception as e:
        print(f"Error saat menambah transaksi: {e}")


def ambil_koin_by_symbol(symbol):
    """Get koin berdasarkan symbol"""
    try:
        for koin in db.get("koin_lokal", []):
            if koin["symbol"] == symbol:
                return koin
        return None
    except Exception as e:
        print(f"Error saat mengambil koin by symbol: {e}")
        return None


def symbol_koin_ada(symbol):
    """Cek apakah symbol sudah ada"""
    try:
        for koin in db.get("koin_lokal", []):
            if koin["symbol"] == symbol:
                return True
        return symbol in db.get("harga_pasar", {})
    except Exception:
        return False