"""
Semua fitur trading: Beli, Jual, Dompet, Pasar, CRUD Koin
"""

from datetime import datetime
from prettytable import PrettyTable
from tabulate import tabulate
import requests
import time

from config import SESSION, id_kripto, mata_uang, peta_tampilan_kripto

from database import (
    ambil_dompet_pengguna, perbarui_dompet_pengguna, ambil_harga_pasar, 
    perbarui_harga_pasar, ambil_koin_lokal, tambah_koin_lokal,
    perbarui_koin_lokal, hapus_koin_lokal, ambil_koin_by_symbol,
    symbol_koin_ada, tambah_transaksi, ambil_transaksi, simpan_database
)

from menu import tampilkan_header
from utils import bersihkan_layar, pause, format_perubahan_harga


# ==================== FUNGSI API ====================

def ambil_harga_crypto_dari_api():
    """Mengambil data harga kripto real-time dari API CoinGecko"""
    try:
        ids_string = ",".join(id_kripto)
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': ids_string,
            'vs_currencies': mata_uang,
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }
        
        print("🔄 Mengambil data harga real-time dari CoinGecko...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error saat mengambil data dari API: {e}")
        print("📊 Menggunakan data harga terakhir dari database...")
        return None
    except Exception as e:
        print(f"Error saat mengambil harga crypto: {e}")
        return None


def update_harga_pasar_dari_api():
    """Update harga pasar di database dengan data real-time dari API"""
    try:
        api_data = ambil_harga_crypto_dari_api()
        
        if api_data:
            berhasil_update = False
            for crypto_id, data in api_data.items():
                symbol = peta_tampilan_kripto.get(crypto_id, {}).get('symbol', '')
                if symbol:
                    harga = data.get(mata_uang, 0.0)
                    if harga > 0:
                        perbarui_harga_pasar(symbol, harga)
                        berhasil_update = True
            
            if berhasil_update:
                print("✓ Harga pasar berhasil diperbarui dari API!")
                return True
        
        return False
    except Exception as e:
        print(f"Error saat update harga pasar: {e}")
        return False

def muat_data_awal_pasar():
    """Muat data pasar saat login (dipanggil 1x saja)"""
    try:
        print("🔄 Memuat data pasar...")
        api_data = ambil_harga_crypto_dari_api()
        
        if api_data:    
            # Simpan ke SESSION
            SESSION['market_data'] = {}
            
            for crypto_id, data in api_data.items():
                symbol = peta_tampilan_kripto.get(crypto_id, {}).get('symbol', '')
                if symbol:
                    harga = data.get(mata_uang, 0.0)     # tambahan
                    perubahan_24j = data.get(f'{mata_uang}_24h_change', 0.0)
                    
                    SESSION['market_data'][symbol] = {
                        'price': harga,
                        'change_24h': perubahan_24j
                    }
                    
                    # Simpan ke database juga
                    if harga > 0:
                        perbarui_harga_pasar(symbol, harga)
            
            SESSION['market_loaded'] = True
            SESSION['market_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"✅ Data pasar berhasil dimuat ({len(SESSION['market_data'])} koin)")
            return True
        else:
            print("⚠️ Gagal memuat dari API, gunakan data database")
            SESSION['market_loaded'] = False
            return False
            
    except Exception as e:
        print(f"❌ Error saat muat data pasar: {e}")
        SESSION['market_loaded'] = False
        return False


def ambil_data_pasar():
    """Ambil data pasar dari SESSION cache"""
    if SESSION.get('market_loaded', False):
        return SESSION.get('market_data', {})  #tambahan
    else:
        # Fallback: ambil dari database
        return {}


# ==================== FUNGSI PASAR ====================

def lihat_harga_pasar():
    """Lihat harga pasar crypto dengan data real-time"""
    try:
        while True:
            try:
                bersihkan_layar()
                tampilkan_header()
                
                waktu_update_terakhir = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print("==============================================")
                print("   HARGA PASAR CRYPTOCURRENCY (REAL-TIME)")
                print("==============================================")
                print(f"Data dari: CoinGecko API | Mata Uang: USD")
                print(f"Update Terakhir: {waktu_update_terakhir}\n")
                
                # Ambil data real-time dari API
                api_data = ambil_data_pasar()
                
                table_data = []
                
                if api_data:
                    for i, (symbol, data) in enumerate(api_data.items(), 1):
                        # Cari nama dari peta_tampilan_kripto
                        name = symbol
                        for crypto_id, info in peta_tampilan_kripto.items():
                            if info['symbol'] == symbol:
                                name = info['nama']
                                break
                        
                        price = data.get('price', 0.0)
                        perubahan_24j = data.get('change_24h', 0.0)
                        str_perubahan = format_perubahan_harga(perubahan_24j)
                        
                        table_data.append([
                            i,
                            name,
                            symbol,
                            f"${price:,.4f}",
                            str_perubahan
                        ])
                else:
                    for i, (symbol, price) in enumerate(ambil_harga_pasar().items(), 1):
                        name = symbol
                        for crypto_id, info in peta_tampilan_kripto.items():
                            if info['symbol'] == symbol:
                                name = info['nama']
                                break
                        
                        str_perubahan = "N/A"
                        
                        table_data.append([
                            i,
                            name,
                            symbol,
                            f"${price:,.4f}",
                            str_perubahan
                        ])
                
                # Tambahkan koin lokal
                for coin in ambil_koin_lokal():
                    harga_sekarang = coin.get("price", 0)
                    harga_24j_lalu = coin.get("price_24h_ago", harga_sekarang)
                    
                    if harga_24j_lalu > 0:
                        perubahan_24j = ((harga_sekarang - harga_24j_lalu) / harga_24j_lalu) * 100
                        str_perubahan = format_perubahan_harga(perubahan_24j)
                    else:
                        str_perubahan = "0.00%"
                    
                    table_data.append([
                        len(table_data) + 1,
                        coin["name"],
                        coin["symbol"],
                        f"${harga_sekarang:,.4f}",
                        str_perubahan + " (Lokal)"
                    ])
                
                print(tabulate(table_data, 
                              headers=["No", "Nama", "Simbol", "Harga (USD)", "24h Change"],
                              tablefmt="grid"))
                
                print("\n" + "="*46)
                print("1. Refresh Manual")
                print("0. Kembali ke Menu Utama")
                print("="*46)
                
                pilihan = input("\nPilih menu: ").strip()
                
                if pilihan == "1":
                    continue
                elif pilihan == "0":
                    break
                else:
                    print("\n✗ Pilihan tidak valid!")
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\nKembali ke menu...")
                break
            except Exception as e:
                print(f"Error di menu harga pasar: {e}")
                input("Tekan Enter untuk lanjut...")
    except Exception as e:
        print(f"Error saat menampilkan harga pasar: {e}")
        pause()




# ==================== FUNGSI DOMPET ====================

def lihat_dompet():
    """Lihat wallet dan saldo"""
    try:
        bersihkan_layar()
        tampilkan_header()
        print("=== EXCHANGE & WALLET ===\n")
        
        wallet = ambil_dompet_pengguna(SESSION['current_user'])
        
        table_data = []
        total_usd = 0
        
        for i, (crypto, balance) in enumerate(wallet.items(), 1):
            if crypto == "USDT":
                nilai_usd = balance
            else:
                price = ambil_harga_pasar().get(crypto, 0)
                nilai_usd = balance * price
            
            total_usd += nilai_usd
            
            table_data.append([
                i,
                crypto,
                f"{balance:.8f}",
                f"${nilai_usd:,.2f}"
            ])
        
        print(tabulate(table_data,
                      headers=["No", "Aset", "Saldo", "Nilai (USD)"],
                      tablefmt="grid"))
        
        print(f"\n{'='*50}")
        print(f"Total Portfolio: ${total_usd:,.2f}")
        print(f"{'='*50}")
        
        print("\n1. Deposit USDT")
        print("2. Withdraw")
        print("0. Kembali")
        
        pilihan = input("\nPilih menu: ").strip()
        
        if pilihan == "1":
            deposit_usdt()
        elif pilihan == "2":
            withdraw()

    except KeyboardInterrupt:
        print("\n\nKembali ke menu...")
    except Exception as e:
        print(f"Error saat menampilkan dompet: {e}")
        pause()


def deposit_usdt():
    """Deposit USDT ke wallet"""
    try:
        print("\n=== DEPOSIT USDT ===")
        amount = float(input("Jumlah USDT: $"))
        
        if amount > 0:
            wallet = ambil_dompet_pengguna(SESSION['current_user'])
            wallet["USDT"] = wallet.get("USDT", 0) + amount
            perbarui_dompet_pengguna(SESSION['current_user'], wallet)
            print(f"\n✓ Berhasil deposit ${amount:,.2f} USDT")
        else:
            print("\n✗ Jumlah harus lebih dari 0")
            
    except KeyboardInterrupt:
        print("\n\nDeposit dibatalkan.")
    except ValueError:
        print("\n✗ Input tidak valid!")
    except Exception as e:
        print(f"Error saat deposit: {e}")
    
    pause()
    lihat_dompet()


def withdraw():
    """Withdraw dari wallet"""
    try:
        print("\n=== WITHDRAW ===")
        
        wallet = ambil_dompet_pengguna(SESSION['current_user'])
        crypto = input("Aset yang ingin di-withdraw: ").upper().strip()
        
        if crypto not in wallet:
            print(f"\n✗ Anda tidak memiliki {crypto}")
            pause()
            return
        
        amount = float(input(f"Jumlah {crypto}: "))
        
        if amount <= 0:
            print("\n✗ Jumlah harus lebih dari 0")
        elif amount > wallet[crypto]:
            print(f"\n✗ Saldo tidak cukup! Saldo Anda: {wallet[crypto]:.8f} {crypto}")
        else:
            wallet[crypto] -= amount
            perbarui_dompet_pengguna(SESSION['current_user'], wallet)
            print(f"\n✓ Berhasil withdraw {amount:.8f} {crypto}")
    except KeyboardInterrupt:
        print("\n\nWithdraw dibatalkan.")
    except ValueError:
        print("\n✗ Input tidak valid!")
    except Exception as e:
        print(f"Error saat withdraw: {e}")
    
    pause()
    lihat_dompet()


# ==================== FUNGSI BELI/JUAL ====================

def buat_order_beli():
    """Buat order beli dengan tampilan market prices yang menarik"""
    try:
        bersihkan_layar()
        tampilkan_header()
        
        # Header
        header = PrettyTable()
        header.field_names = ["💰 ORDER BELI - PEMBELIAN INSTAN 💰"]
        header.add_row(["Beli cryptocurrency dengan harga pasar terkini"])
        print(header)
        print()
        
        # Tampilkan harga pasar dengan PrettyTable
        tabel_pasar = PrettyTable()
        tabel_pasar.field_names = ["No", "Crypto", "Symbol", "Price (USD)", "Status"]
        tabel_pasar.hrules = 1
        
        # Tambahkan crypto dari API
        coin_list = []
        for i, (symbol, price) in enumerate(list(ambil_harga_pasar().items())[:8], 1):
            # Cari nama lengkap
            nama_crypto = symbol
            for crypto_id, info in peta_tampilan_kripto.items():
                if info['symbol'] == symbol:
                    nama_crypto = info['nama']
                    break
            
            tabel_pasar.add_row([
                i,
                nama_crypto,
                symbol,
                f"${price:,.4f}",
                "🟢 Live"
            ])
            coin_list.append(symbol)
        
        # Tambahkan koin lokal
        for coin in ambil_koin_lokal():
            i += 1
            tabel_pasar.add_row([
                i,
                coin["name"],
                coin["symbol"],
                f"${coin.get('price', 0):,.4f}",
                "🔵 Local"
            ])
            coin_list.append(coin["symbol"])
        
        tabel_pasar.align["No"] = "c"
        tabel_pasar.align["Crypto"] = "l"
        tabel_pasar.align["Symbol"] = "c"
        tabel_pasar.align["Price (USD)"] = "r"
        tabel_pasar.align["Status"] = "c"
        
        print(tabel_pasar)
        print()
        
        # Info Wallet
        wallet = ambil_dompet_pengguna(SESSION['current_user'])
        saldo_usdt = wallet.get("USDT", 0)
        
        info_dompet = PrettyTable()
        info_dompet.field_names = ["💼 DOMPET ANDA"]
        info_dompet.hrules = 1
        info_dompet.add_row([f"Saldo USDT: ${saldo_usdt:,.2f}"])
        print(info_dompet)
        print()
        
        # Input
        print("─" * 60)
        crypto = input("🪙 Crypto yang ingin dibeli (Symbol): ").upper().strip()
        
        if crypto not in coin_list:
            print(f"\n❌ {crypto} tidak tersedia di pasar")
            pause()
            return
        
        amount = float(input(f"📦 Jumlah {crypto}: "))
        
        if amount <= 0:
            print("\n❌ Jumlah harus lebih dari 0!")
            pause()
            return
        
        price = ambil_harga_pasar().get(crypto, 0)
        total_biaya = amount * price
        
        
        print()
        bersihkan_layar()  
        tampilkan_header()
    
        # Info Wallet
        wallet = ambil_dompet_pengguna(SESSION['current_user'])
        saldo_usdt = wallet.get("USDT", 0)
        
        info_dompet = PrettyTable()
        info_dompet.field_names = ["💼 DOMPET ANDA"]
        info_dompet.hrules = 1
        info_dompet.add_row([f"Saldo USDT: ${saldo_usdt:,.2f}"])
        print(info_dompet)
        print()

        
        preview = PrettyTable()
        preview.field_names = ["📋 RINGKASAN ORDER", ""]
        preview.hrules = 1
        preview.add_row(["Crypto", crypto])
        preview.add_row(["Jumlah", f"{amount:.8f} {crypto}"])
        preview.add_row(["Harga", f"${price:,.4f}"])
        preview.add_row(["─────────", "─────────"])
        preview.add_row(["💳 Total Biaya", f"${total_biaya:,.2f} USDT"])
        preview.add_row(["💰 Saldo Anda", f"${saldo_usdt:,.2f} USDT"])
        
        if total_biaya <= saldo_usdt:
            sisa = saldo_usdt - total_biaya
            preview.add_row(["✅ Sisa", f"${sisa:,.2f} USDT"])
        else:
            kekurangan = total_biaya - saldo_usdt
            preview.add_row(["❌ Kekurangan", f"${kekurangan:,.2f} USDT"])
        
        preview.align["📋 RINGKASAN ORDER"] = "l"
        preview.align[""] = "r"
        print(preview)
        print()
        
        # Validasi saldo
        if total_biaya > saldo_usdt:
            error = PrettyTable()
            error.field_names = ["❌ SALDO TIDAK CUKUP"]
            error.hrules = 1
            error.add_row([f"Anda membutuhkan ${total_biaya - saldo_usdt:,.2f} USDT lagi"])
            error.add_row(["Silakan deposit atau kurangi jumlah"])
            print(error)
            pause()
            return
        
        # Konfirmasi
        confirm = input("✅ Konfirmasi order BELI? (y/n): ").lower()
        
        if confirm == 'y':
            # Eksekusi order
            wallet["USDT"] -= total_biaya
            wallet[crypto] = wallet.get(crypto, 0) + amount
            perbarui_dompet_pengguna(SESSION['current_user'], wallet)
            
            transaksi = {
                "id": len(ambil_transaksi()) + 1,
                "user": SESSION['current_user'],
                "type": "BUY",
                "crypto": crypto,
                "amount": amount,
                "price": price,
                "total": total_biaya,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "COMPLETED"
            }
            
            tambah_transaksi(transaksi)
            
            # Success message
            print()
            success = PrettyTable()
            success.field_names = ["✅ ORDER BERHASIL DIEKSEKUSI"]
            success.hrules = 1
            success.add_row([f"Membeli {amount:.8f} {crypto}"])
            success.add_row([f"Total: ${total_biaya:,.2f} USDT"])
            success.add_row([f"ID Transaksi: #{transaksi['id']}"])
            print(success)
        else:
            print()
            cancel = PrettyTable()
            cancel.field_names = ["❌ ORDER DIBATALKAN"]
            cancel.hrules = 1
            cancel.add_row(["Transaksi telah dibatalkan"])
            print(cancel)
    except KeyboardInterrupt:
        print("\n\nOrder beli dibatalkan.")
    except ValueError:
        print("\n❌ Input tidak valid!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    pause()


def buat_order_jual():
    """Buat order jual dengan tampilan portfolio yang menarik"""
    try:
        bersihkan_layar()
        tampilkan_header()
        
        # Header
        header = PrettyTable()
        header.field_names = ["💸 ORDER JUAL - PENJUALAN INSTAN 💸"]
        header.add_row(["Jual cryptocurrency Anda dengan harga pasar terkini"])
        print(header)
        print()
        
        wallet = ambil_dompet_pengguna(SESSION['current_user'])
        
        # Tampilkan portfolio (aset yang dimiliki)
        tabel_portfolio = PrettyTable()
        tabel_portfolio.field_names = ["No", "Crypto", "Saldo Anda", "Harga Saat Ini", "Total Nilai"]
        tabel_portfolio.hrules = 1
        
        crypto_tersedia = []
        item_portfolio = []
        
        for crypto, balance in wallet.items():
            if crypto != "USDT" and balance > 0:
                price = ambil_harga_pasar().get(crypto, 0)
                total_nilai = balance * price
                item_portfolio.append((crypto, balance, price, total_nilai))
                crypto_tersedia.append(crypto)
        
        if not crypto_tersedia:
            print("❌ Anda tidak memiliki cryptocurrency untuk dijual")
            print("💡 Silakan beli terlebih dahulu di menu BUY\n")
            pause()
            return
        
        # Sort by total value (tertinggi dulu)
        item_portfolio.sort(key=lambda x: x[3], reverse=True)
        
        for i, (crypto, balance, price, total_nilai) in enumerate(item_portfolio, 1):
            tabel_portfolio.add_row([
                i,
                crypto,
                f"{balance:.8f}",
                f"${price:,.4f}",
                f"${total_nilai:,.2f}"
            ])
        
        tabel_portfolio.align["No"] = "c"
        tabel_portfolio.align["Crypto"] = "c"
        tabel_portfolio.align["Saldo Anda"] = "r"
        tabel_portfolio.align["Harga Saat Ini"] = "r"
        tabel_portfolio.align["Total Nilai"] = "r"
        
        print(tabel_portfolio)
        
        # Total portfolio value
        total_nilai_crypto = sum(item[3] for item in item_portfolio)
        saldo_usdt = wallet.get("USDT", 0)
        total_portfolio = total_nilai_crypto + saldo_usdt
        
        print()
        summary = PrettyTable()
        summary.field_names = ["💼 RINGKASAN PORTFOLIO", "NILAI"]
        summary.hrules = 1
        summary.add_row(["Aset Crypto", f"${total_nilai_crypto:,.2f}"])
        summary.add_row(["Saldo USDT", f"${saldo_usdt:,.2f}"])
        summary.add_row(["─────────────", "─────────────"])
        summary.add_row(["💰 Total Portfolio", f"${total_portfolio:,.2f}"])
        summary.align["💼 RINGKASAN PORTFOLIO"] = "l"
        summary.align["NILAI"] = "r"
        print(summary)
        print()
        
        # Input
        print("─" * 60)
        crypto = input("🪙 Crypto yang ingin dijual (Symbol): ").upper().strip()
        
        if crypto not in crypto_tersedia:
            print(f"\n❌ Anda tidak memiliki {crypto} atau saldo 0")
            pause()
            return
        
        saldo_sekarang = wallet[crypto]
        print(f"📦 Saldo {crypto} Anda: {saldo_sekarang:.8f}")
        
        amount = float(input(f"📦 Jumlah {crypto} yang dijual: "))
        
        if amount <= 0:
            print("\n❌ Jumlah harus lebih dari 0!")
            pause()
            return
        
        if amount > saldo_sekarang:
            print(f"\n❌ Saldo tidak cukup! Maksimal: {saldo_sekarang:.8f} {crypto}")
            pause()
            return
        
        price = ambil_harga_pasar().get(crypto, 0)
        total_terima = amount * price
        
        # Preview Order dengan PrettyTable
        print()
        preview = PrettyTable()
        preview.field_names = ["📋 RINGKASAN ORDER JUAL", ""]
        preview.hrules = 1
        preview.add_row(["Crypto", crypto])
        preview.add_row(["Jumlah Dijual", f"{amount:.8f} {crypto}"])
        preview.add_row(["Harga Saat Ini", f"${price:,.4f}"])
        preview.add_row(["─────────────", "─────────────"])
        preview.add_row(["💵 Anda Akan Terima", f"${total_terima:,.2f} USDT"])
        preview.add_row(["📊 Sisa Saldo", f"{saldo_sekarang - amount:.8f} {crypto}"])
        preview.add_row(["💰 Saldo USDT Baru", f"${saldo_usdt + total_terima:,.2f}"])
        
        preview.align["📋 RINGKASAN ORDER JUAL"] = "l"
        preview.align[""] = "r"
        print(preview)
        print()
        
        # Konfirmasi
        confirm = input("✅ Konfirmasi order JUAL? (y/n): ").lower()
        
        if confirm == 'y':
            # Eksekusi order
            wallet[crypto] -= amount
            wallet["USDT"] = wallet.get("USDT", 0) + total_terima
            perbarui_dompet_pengguna(SESSION['current_user'], wallet)
            
            transaksi = {
                "id": len(ambil_transaksi()) + 1,
                "user": SESSION['current_user'],
                "type": "SELL",
                "crypto": crypto,
                "amount": amount,
                "price": price,
                "total": total_terima,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "COMPLETED"
            }
            
            tambah_transaksi(transaksi)
            
            # Success message
            print()
            success = PrettyTable()
            success.field_names = ["✅ ORDER BERHASIL DIEKSEKUSI"]
            success.hrules = 1
            success.add_row([f"Menjual {amount:.8f} {crypto}"])
            success.add_row([f"Diterima: ${total_terima:,.2f} USDT"])
            success.add_row([f"ID Transaksi: #{transaksi['id']}"])
            print(success)
        else:
            print()
            cancel = PrettyTable()
            cancel.field_names = ["❌ ORDER DIBATALKAN"]
            cancel.hrules = 1
            cancel.add_row(["Transaksi telah dibatalkan"])
            print(cancel)
    except KeyboardInterrupt:
        print("\n\nOrder jual dibatalkan.")
    except ValueError:
        print("\n❌ Input tidak valid!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    pause()


# ==================== CRUD KOIN LOKAL ====================

def kelola_koin_lokal():
    """Menu manajemen koin lokal (CRUD)"""
    try:
        while True:
            try:
                bersihkan_layar()
                tampilkan_header()
                
                # Buat tabel menu CRUD
                table = PrettyTable()
                table.field_names = ["No", "Menu CRUD Koin Lokal"]
                table.align["No"] = "c"
                table.align["Menu CRUD Koin Lokal"] = "l"
                table.hrules = 1
                
                table.add_row(["1", "➕ Tambah Koin Baru (Create)"])
                table.add_row(["2", "✏️  Update Harga Koin (Update)"])
                table.add_row(["3", "🗑️  Hapus Koin (Delete)"])
                table.add_row(["0", "🔙 Kembali ke Menu Utama"])
                
                print(table)
                
                pilihan = input("\n    🎯 Pilih menu: ").strip()
                
                if pilihan == "1":
                    tambah_koin_lokal_menu()
                elif pilihan == "2":
                    update_koin_lokal_menu()
                elif pilihan == "3":
                    hapus_koin_lokal_menu()
                elif pilihan == "0":
                    break
                else:
                    print("\n    ✗ Pilihan tidak valid!")
                    pause()
            except KeyboardInterrupt:
                print("\n\n    Kembali ke menu...")
                break
            except Exception as e:
                print(f"\n    Error di menu koin lokal: {e}")
                pause()
    except Exception as e:
        print(f"Error saat mengelola koin lokal: {e}")
        pause()


def tambah_koin_lokal_menu():
    """Tambah koin lokal"""
    try:
        bersihkan_layar()
        tampilkan_header()
        print("=== TAMBAH KOIN LOKAL BARU ===\n")
        
        name = input("    Nama Koin: ").strip()
        if not name:
            print("\n    ✗ Nama koin tidak boleh kosong!")
            pause()
            return
        
        symbol = input("    Symbol (misal: ABC): ").upper().strip()
        if not symbol:
            print("\n    ✗ Symbol tidak boleh kosong!")
            pause()
            return
        
        # Cek apakah symbol sudah ada
        if symbol_koin_ada(symbol):
            print(f"\n    ✗ Symbol {symbol} sudah ada!")
            pause()
            return
        
        price = float(input("    Harga Awal (USD): $"))
        if price <= 0:
            print("\n    ✗ Harga harus lebih dari 0!")
            pause()
            return
        
        description = input("    Deskripsi (opsional): ").strip()
        
        # Konfirmasi
        print(f"\n{'='*50}")
        print("KONFIRMASI KOIN BARU:")
        print(f"Nama      : {name}")
        print(f"Symbol    : {symbol}")
        print(f"Harga     : ${price:,.4f}")
        print(f"Deskripsi : {description if description else '-'}")
        print(f"{'='*50}")
        
        confirm = input("\n    Tambahkan koin ini? (y/n): ").lower()
        
        if confirm == 'y':
            waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            koin_baru = {
                "name": name,
                "symbol": symbol,
                "price": price,
                "price_24h_ago": price,
                "description": description,
                "created_by": SESSION['current_user'],
                "created_date": waktu_sekarang,
                "last_updated": waktu_sekarang
            }
            
            tambah_koin_lokal(koin_baru)
            perbarui_harga_pasar(symbol, price)
            
            print(f"\n    ✓ Koin {name} ({symbol}) berhasil ditambahkan!")
        else:
            print("\n    ✗ Penambahan koin dibatalkan")
    except KeyboardInterrupt:
        print("\n\n    Penambahan koin dibatalkan.")
    except ValueError:
        print("\n    ✗ Input harga tidak valid!")
    except Exception as e:
        print(f"\n    ✗ Terjadi error: {e}")
    
    pause()


def update_koin_lokal_menu():
    """Update harga koin lokal"""
    try:
        bersihkan_layar()
        tampilkan_header()
        print("=== UPDATE HARGA KOIN LOKAL ===\n")
        
        if not ambil_koin_lokal():
            print("    Belum ada koin lokal yang dapat diupdate.")
            pause()
            return
        
        # Tampilkan daftar koin lokal
        print("Koin Lokal yang Tersedia:\n")
        for i, coin in enumerate(ambil_koin_lokal(), 1):
            harga_sekarang = coin.get("price", 0)
            print(f"    {i}. {coin['symbol']:6s} - {coin['name']:15s} ${harga_sekarang:>10,.4f}")
        
        print()
        symbol = input("    Masukkan symbol koin yang akan diupdate: ").upper().strip()
        
        # Cari koin
        koin_ditemukan = ambil_koin_by_symbol(symbol)
        
        if not koin_ditemukan:
            print(f"\n    ✗ Koin dengan symbol {symbol} tidak ditemukan!")
            pause()
            return
        
        harga_sekarang = koin_ditemukan.get("price", 0)
        harga_24j_lalu = koin_ditemukan.get("price_24h_ago", harga_sekarang)
        
        print(f"\n{'='*50}")
        print(f"Koin          : {koin_ditemukan['name']} ({symbol})")
        print(f"Harga Saat Ini: ${harga_sekarang:,.4f}")
        print(f"Harga 24h Lalu: ${harga_24j_lalu:,.4f}")
        print(f"{'='*50}\n")
        
        harga_baru = float(input("    Harga baru (USD): $"))
        
        if harga_baru <= 0:
            print("\n    ✗ Harga harus lebih dari 0!")
            pause()
            return
        
        # Preview perubahan
        selisih_harga = harga_baru - harga_sekarang
        persen_selisih = ((harga_baru - harga_sekarang) / harga_sekarang) * 100 if harga_sekarang > 0 else 0
        
        if harga_24j_lalu > 0:
            perubahan_24j_baru = ((harga_baru - harga_24j_lalu) / harga_24j_lalu) * 100
        else:
            perubahan_24j_baru = 0.0
        
        print(f"\n{'='*50}")
        print("PREVIEW PERUBAHAN:")
        print(f"Harga Lama       : ${harga_sekarang:,.4f}")
        print(f"Harga Baru       : ${harga_baru:,.4f}")
        print(f"Selisih          : ${selisih_harga:+,.4f} ({persen_selisih:+.2f}%)")
        print(f"24h Change Baru  : {perubahan_24j_baru:+.2f}%")
        print(f"{'='*50}")
        
        confirm = input("\n    Konfirmasi update? (y/n): ").lower()
        
        if confirm == 'y':
            waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            pembaruan = {
                "price": harga_baru,
                "last_updated": waktu_sekarang
            }
            
            perbarui_koin_lokal(symbol, pembaruan)
            perbarui_harga_pasar(symbol, harga_baru)
            
            print(f"\n    ✓ Harga {koin_ditemukan['name']} ({symbol}) berhasil diupdate!")
            print(f"      Harga: ${harga_sekarang:,.4f} → ${harga_baru:,.4f}")
            print(f"      24h Change: {perubahan_24j_baru:+.2f}%")
        else:
            print("\n    ✗ Update dibatalkan")
    except KeyboardInterrupt:
        print("\n\n    Update koin dibatalkan.")
    except ValueError:
        print("\n    ✗ Input harga tidak valid!")
    except Exception as e:
        print(f"\n    ✗ Terjadi error: {e}")
    
    pause()


def hapus_koin_lokal_menu():
    """Hapus koin lokal"""
    try:
        bersihkan_layar()
        tampilkan_header()
        print("=== HAPUS KOIN LOKAL ===\n")
        
        if not ambil_koin_lokal():
            print("    Belum ada koin lokal yang dapat dihapus.")
            pause()
            return
        
        # Tampilkan daftar koin lokal
        print("Koin Lokal yang Tersedia:\n")
        for i, coin in enumerate(ambil_koin_lokal(), 1):
            print(f"    {i}. {coin['symbol']:6s} - {coin['name']:15s} ${coin.get('price', 0):>10,.4f}")
        
        print()
        symbol = input("    Masukkan symbol koin yang akan dihapus: ").upper().strip()
        
        # Cari koin
        koin_ditemukan = ambil_koin_by_symbol(symbol)
        
        if not koin_ditemukan:
            print(f"\n    ✗ Koin dengan symbol {symbol} tidak ditemukan!")
            pause()
            return
        
        # Konfirmasi penghapusan
        print(f"\n{'='*50}")
        print(f"KONFIRMASI HAPUS:")
        print(f"Nama        : {koin_ditemukan['name']}")
        print(f"Symbol      : {koin_ditemukan['symbol']}")
        print(f"Harga       : ${koin_ditemukan.get('price', 0):,.4f}")
        print(f"Dibuat oleh : {koin_ditemukan.get('created_by', '-')}")
        print(f"{'='*50}")
        
        confirm = input("\n    Yakin ingin menghapus koin ini? (y/n): ").lower()
        
        if confirm == 'y':
            hapus_koin_lokal(symbol)
            print(f"\n    ✓ Koin {koin_ditemukan['name']} ({symbol}) berhasil dihapus!")
        else:
            print("\n    ✗ Penghapusan dibatalkan")
    except KeyboardInterrupt:
        print("\n\n    Penghapusan koin dibatalkan.")
    except Exception as e:
        print(f"\n    ✗ Terjadi error: {e}")
    
    pause()


# ==================== RIWAYAT TRANSAKSI ====================

def lihat_riwayat_transaksi():
    """Lihat riwayat transaksi - Admin lihat semua, User lihat miliknya"""
    try:
        bersihkan_layar()
        tampilkan_header()
        
        # ADMIN: Lihat semua transaksi
        if SESSION['current_level'] == "admin":
            print("=== SEMUA RIWAYAT TRANSAKSI (ALL USERS) ===\n")
            
            if not ambil_transaksi():
                print("    📭 Belum ada transaksi dari semua user")
            else:
                table_data = []
                for trans in reversed(ambil_transaksi()[-50:]):  # 50 transaksi terakhir
                    table_data.append([
                        trans["id"],
                        trans["user"],
                        trans["timestamp"],
                        trans["type"],
                        trans["crypto"],
                        f"{trans['amount']:.8f}",
                        f"${trans['price']:,.4f}",
                        f"${trans['total']:,.2f}",
                        trans["status"]
                    ])
                
                print(tabulate(table_data,
                              headers=["ID", "User", "Waktu", "Type", "Crypto", "Amount", "Price", "Total", "Status"],
                              tablefmt="grid"))
                
                print(f"\n📊 Total Transaksi: {len(ambil_transaksi())}")
        
        # USER: Lihat transaksi miliknya sendiri
        else:
            print("=== RIWAYAT TRANSAKSI SAYA ===\n")
            
            transaksi_user = [t for t in ambil_transaksi() if t["user"] == SESSION['current_user']]
            
            if not transaksi_user:
                print("    📭 Belum ada transaksi")
            else:
                table_data = []
                for trans in reversed(transaksi_user[-20:]):  # 20 transaksi terakhir
                    table_data.append([
                        trans["id"],
                        trans["timestamp"],
                        trans["type"],
                        trans["crypto"],
                        f"{trans['amount']:.8f}",
                        f"${trans['price']:,.4f}",
                        f"${trans['total']:,.2f}",
                        trans["status"]
                    ])
                
                print(tabulate(table_data,
                              headers=["ID", "Waktu", "Type", "Crypto", "Amount", "Price", "Total", "Status"],
                              tablefmt="grid"))
                
                print(f"\n📊 Total Transaksi Anda: {len(transaksi_user)}")
    except KeyboardInterrupt:
        print("\n\n    Kembali ke menu...")
    except Exception as e:
        print(f"Error saat menampilkan riwayat transaksi: {e}")
    
    pause()