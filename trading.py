"""
Trading Module
Semua fitur trading: Buy, Sell, Wallet, Market, CRUD Koin
"""

from datetime import datetime
from prettytable import PrettyTable
from tabulate import tabulate
import requests
import time
import random

from config import SESSION, CRYPTO_IDS, VS_CURRENCY, CRYPTO_DISPLAY_MAP
from database import (
    get_user_wallet, update_user_wallet, get_market_prices, 
    update_market_price, get_local_coins, add_local_coin,
    update_local_coin, delete_local_coin, get_coin_by_symbol,
    coin_symbol_exists, add_transaction, get_transactions, save_database
)
from menu import print_header
from utils import clear_screen, pause, format_price_change


# ==================== API FUNCTIONS ====================

def get_crypto_prices_from_api():
    """Mengambil data harga kripto real-time dari API CoinGecko"""
    ids_string = ",".join(CRYPTO_IDS)
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': ids_string,
        'vs_currencies': VS_CURRENCY,
        'include_24hr_change': 'true',
        'include_last_updated_at': 'true'
    }
    
    try:
        print("🔄 Mengambil data harga real-time dari CoinGecko...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error saat mengambil data dari API: {e}")
        print("📊 Menggunakan data harga terakhir dari database...")
        return None


def update_market_prices_from_api():
    """Update harga pasar di database dengan data real-time dari API"""
    api_data = get_crypto_prices_from_api()
    
    if api_data:
        updated = False
        for crypto_id, data in api_data.items():
            symbol = CRYPTO_DISPLAY_MAP.get(crypto_id, {}).get('symbol', '')
            if symbol:
                price = data.get(VS_CURRENCY, 0.0)
                if price > 0:
                    update_market_price(symbol, price)
                    updated = True
        
        if updated:
            print("✓ Harga pasar berhasil diperbarui dari API!")
            return True
    
    return False


# ==================== MARKET FUNCTIONS ====================

def view_market_prices():
    """Lihat harga pasar crypto dengan data real-time"""
    while True:
        clear_screen()
        print_header()
        
        last_updated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("==============================================")
        print("   HARGA PASAR CRYPTOCURRENCY (REAL-TIME)")
        print("==============================================")
        print(f"Data dari: CoinGecko API | Mata Uang: USD")
        print(f"Update Terakhir: {last_updated_time}\n")
        
        # Ambil data real-time dari API
        api_data = get_crypto_prices_from_api()
        
        table_data = []
        
        if api_data:
            for i, (crypto_id, data) in enumerate(api_data.items(), 1):
                display_info = CRYPTO_DISPLAY_MAP.get(crypto_id, {'name': crypto_id.capitalize(), 'symbol': 'N/A'})
                
                name = display_info['name']
                symbol = display_info['symbol']
                price = data.get(VS_CURRENCY, 0.0)
                change_24h = data.get(f'{VS_CURRENCY}_24h_change', 0.0)
                
                if symbol != 'N/A':
                    update_market_price(symbol, price)
                
                change_str = format_price_change(change_24h)
                
                table_data.append([
                    i,
                    name,
                    symbol,
                    f"${price:,.4f}",
                    change_str
                ])
        else:
            for i, (symbol, price) in enumerate(get_market_prices().items(), 1):
                name = symbol
                for crypto_id, info in CRYPTO_DISPLAY_MAP.items():
                    if info['symbol'] == symbol:
                        name = info['name']
                        break
                
                change = random.uniform(-10, 10)
                change_str = format_price_change(change)
                
                table_data.append([
                    i,
                    name,
                    symbol,
                    f"${price:,.4f}",
                    change_str + " (simulasi)"
                ])
        
        # Tambahkan koin lokal
        for coin in get_local_coins():
            current_price = coin.get("price", 0)
            price_24h_ago = coin.get("price_24h_ago", current_price)
            
            if price_24h_ago > 0:
                change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
                change_str = format_price_change(change_24h)
            else:
                change_str = "0.00%"
            
            table_data.append([
                len(table_data) + 1,
                coin["name"],
                coin["symbol"],
                f"${current_price:,.4f}",
                change_str + " (Lokal)"
            ])
        
        print(tabulate(table_data, 
                      headers=["No", "Nama", "Simbol", "Harga (USD)", "24h Change"],
                      tablefmt="grid"))
        
        print("\n" + "="*46)
        print("1. Refresh Manual")
        print("2. Auto-Refresh (30 detik)")
        print("0. Kembali ke Menu Utama")
        print("="*46)
        
        choice = input("\nPilih menu: ").strip()
        
        if choice == "1":
            continue
        elif choice == "2":
            auto_refresh_prices()
            break
        elif choice == "0":
            break
        else:
            print("\n✗ Pilihan tidak valid!")
            time.sleep(1)


def auto_refresh_prices():
    """Auto-refresh harga setiap 30 detik"""
    try:
        refresh_count = 0
        while True:
            clear_screen()
            print_header()
            
            last_updated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print("==============================================")
            print("   AUTO-REFRESH MODE (Tekan Ctrl+C untuk Stop)")
            print("==============================================")
            print(f"Update Terakhir: {last_updated_time}")
            print(f"Refresh ke-{refresh_count + 1}\n")
            
            api_data = get_crypto_prices_from_api()
            
            table_data = []
            
            if api_data:
                for i, (crypto_id, data) in enumerate(api_data.items(), 1):
                    display_info = CRYPTO_DISPLAY_MAP.get(crypto_id, {'name': crypto_id.capitalize(), 'symbol': 'N/A'})
                    
                    name = display_info['name']
                    symbol = display_info['symbol']
                    price = data.get(VS_CURRENCY, 0.0)
                    change_24h = data.get(f'{VS_CURRENCY}_24h_change', 0.0)
                    
                    if symbol != 'N/A':
                        update_market_price(symbol, price)
                    
                    change_str = format_price_change(change_24h)
                    
                    table_data.append([
                        i,
                        name,
                        symbol,
                        f"${price:,.4f}",
                        change_str
                    ])
            
            # Tambahkan koin lokal
            for coin in get_local_coins():
                current_price = coin.get("price", 0)
                price_24h_ago = coin.get("price_24h_ago", current_price)
                
                if price_24h_ago > 0:
                    change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
                    change_str = format_price_change(change_24h)
                else:
                    change_str = "0.00%"
                
                table_data.append([
                    len(table_data) + 1,
                    coin["name"],
                    coin["symbol"],
                    f"${current_price:,.4f}",
                    change_str + " (Lokal)"
                ])
            
            print(tabulate(table_data, 
                          headers=["No", "Nama", "Simbol", "Harga (USD)", "24h Change"],
                          tablefmt="grid"))
            
            print("\nMenunggu 30 detik untuk refresh berikutnya...")
            print("Tekan Ctrl+C untuk kembali ke menu")
            
            time.sleep(30)
            refresh_count += 1
            
    except KeyboardInterrupt:
        print("\n\n✓ Auto-refresh dihentikan")
        pause()


# ==================== WALLET FUNCTIONS ====================

def view_wallet():
    """Lihat wallet dan saldo"""
    clear_screen()
    print_header()
    print("=== EXCHANGE & WALLET ===\n")
    
    wallet = get_user_wallet(SESSION['current_user'])
    
    table_data = []
    total_usd = 0
    
    for i, (crypto, balance) in enumerate(wallet.items(), 1):
        if crypto == "USDT":
            value_usd = balance
        else:
            price = get_market_prices().get(crypto, 0)
            value_usd = balance * price
        
        total_usd += value_usd
        
        table_data.append([
            i,
            crypto,
            f"{balance:.8f}",
            f"${value_usd:,.2f}"
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
    
    choice = input("\nPilih menu: ").strip()
    
    if choice == "1":
        deposit_usdt()
    elif choice == "2":
        withdraw()


def deposit_usdt():
    """Deposit USDT ke wallet"""
    print("\n=== DEPOSIT USDT ===")
    try:
        amount = float(input("Jumlah USDT: $"))
        if amount > 0:
            wallet = get_user_wallet(SESSION['current_user'])
            wallet["USDT"] = wallet.get("USDT", 0) + amount
            update_user_wallet(SESSION['current_user'], wallet)
            print(f"\n✓ Berhasil deposit ${amount:,.2f} USDT")
        else:
            print("\n✗ Jumlah harus lebih dari 0")
    except ValueError:
        print("\n✗ Input tidak valid!")
    
    pause()
    view_wallet()


def withdraw():
    """Withdraw dari wallet"""
    print("\n=== WITHDRAW ===")
    
    wallet = get_user_wallet(SESSION['current_user'])
    crypto = input("Aset yang ingin di-withdraw: ").upper().strip()
    
    if crypto not in wallet:
        print(f"\n✗ Anda tidak memiliki {crypto}")
        pause()
        return
    
    try:
        amount = float(input(f"Jumlah {crypto}: "))
        
        if amount <= 0:
            print("\n✗ Jumlah harus lebih dari 0")
        elif amount > wallet[crypto]:
            print(f"\n✗ Saldo tidak cukup! Saldo Anda: {wallet[crypto]:.8f} {crypto}")
        else:
            wallet[crypto] -= amount
            update_user_wallet(SESSION['current_user'], wallet)
            print(f"\n✓ Berhasil withdraw {amount:.8f} {crypto}")
    except ValueError:
        print("\n✗ Input tidak valid!")
    
    pause()
    view_wallet()


# ==================== BUY/SELL FUNCTIONS ====================

def create_buy_order():
    """Buat order beli dengan tampilan market prices yang menarik"""
    clear_screen()
    print_header()
    
    # Header
    header = PrettyTable()
    header.field_names = ["💰 BUY ORDER - INSTANT PURCHASE 💰"]
    header.add_row(["Beli cryptocurrency dengan harga pasar terkini"])
    print(header)
    print()
    
    # Update harga dari API
    print("🔄 Mengambil data harga real-time dari CoinGecko...")
    update_result = update_market_prices_from_api()
    if update_result:
        print("✓ Harga pasar berhasil diperbarui dari API!\n")
    else:
        print("⚠️ Menggunakan harga terakhir dari database\n")
    
    # Tampilkan harga pasar dengan PrettyTable
    market_table = PrettyTable()
    market_table.field_names = ["No", "Crypto", "Symbol", "Price (USD)", "Status"]
    market_table.hrules = 1
    
    # Tambahkan crypto dari API
    coin_list = []
    for i, (symbol, price) in enumerate(list(get_market_prices().items())[:8], 1):
        # Cari nama lengkap
        crypto_name = symbol
        for crypto_id, info in CRYPTO_DISPLAY_MAP.items():
            if info['symbol'] == symbol:
                crypto_name = info['name']
                break
        
        market_table.add_row([
            i,
            crypto_name,
            symbol,
            f"${price:,.4f}",
            "🟢 Live"
        ])
        coin_list.append(symbol)
    
    # Tambahkan koin lokal
    for coin in get_local_coins():
        i += 1
        market_table.add_row([
            i,
            coin["name"],
            coin["symbol"],
            f"${coin.get('price', 0):,.4f}",
            "🔵 Local"
        ])
        coin_list.append(coin["symbol"])
    
    market_table.align["No"] = "c"
    market_table.align["Crypto"] = "l"
    market_table.align["Symbol"] = "c"
    market_table.align["Price (USD)"] = "r"
    market_table.align["Status"] = "c"
    
    print(market_table)
    print()
    
    # Info Wallet
    wallet = get_user_wallet(SESSION['current_user'])
    usdt_balance = wallet.get("USDT", 0)
    
    wallet_info = PrettyTable()
    wallet_info.field_names = ["💼 YOUR WALLET"]
    wallet_info.hrules = 1
    wallet_info.add_row([f"USDT Balance: ${usdt_balance:,.2f}"])
    print(wallet_info)
    print()
    
    # Input
    print("─" * 60)
    crypto = input("🪙 Crypto yang ingin dibeli (Symbol): ").upper().strip()
    
    if crypto not in coin_list:
        print(f"\n❌ {crypto} tidak tersedia di pasar")
        pause()
        return
    
    try:
        amount = float(input(f"📦 Jumlah {crypto}: "))
        
        if amount <= 0:
            print("\n❌ Jumlah harus lebih dari 0!")
            pause()
            return
        
        price = get_market_prices().get(crypto, 0)
        total_cost = amount * price
        
        # Preview Order dengan PrettyTable
        print()
        preview = PrettyTable()
        preview.field_names = ["📋 ORDER SUMMARY", ""]
        preview.hrules = 1
        preview.add_row(["Crypto", crypto])
        preview.add_row(["Amount", f"{amount:.8f} {crypto}"])
        preview.add_row(["Price", f"${price:,.4f}"])
        preview.add_row(["─────────", "─────────"])
        preview.add_row(["💳 Total Cost", f"${total_cost:,.2f} USDT"])
        preview.add_row(["💰 Your Balance", f"${usdt_balance:,.2f} USDT"])
        
        if total_cost <= usdt_balance:
            remaining = usdt_balance - total_cost
            preview.add_row(["✅ Remaining", f"${remaining:,.2f} USDT"])
        else:
            deficit = total_cost - usdt_balance
            preview.add_row(["❌ Deficit", f"${deficit:,.2f} USDT"])
        
        preview.align["📋 ORDER SUMMARY"] = "l"
        preview.align[""] = "r"
        print(preview)
        print()
        
        # Validasi saldo
        if total_cost > usdt_balance:
            error = PrettyTable()
            error.field_names = ["❌ INSUFFICIENT BALANCE"]
            error.hrules = 1
            error.add_row([f"You need ${total_cost - usdt_balance:,.2f} more USDT"])
            error.add_row(["Please deposit or reduce amount"])
            print(error)
            pause()
            return
        
        # Konfirmasi
        confirm = input("✅ Konfirmasi order BUY? (y/n): ").lower()
        
        if confirm == 'y':
            # Eksekusi order
            wallet["USDT"] -= total_cost
            wallet[crypto] = wallet.get(crypto, 0) + amount
            update_user_wallet(SESSION['current_user'], wallet)
            
            transaction = {
                "id": len(get_transactions()) + 1,
                "user": SESSION['current_user'],
                "type": "BUY",
                "crypto": crypto,
                "amount": amount,
                "price": price,
                "total": total_cost,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "COMPLETED"
            }
            
            add_transaction(transaction)
            
            # Success message
            print()
            success = PrettyTable()
            success.field_names = ["✅ ORDER EXECUTED SUCCESSFULLY"]
            success.hrules = 1
            success.add_row([f"Bought {amount:.8f} {crypto}"])
            success.add_row([f"Total: ${total_cost:,.2f} USDT"])
            success.add_row([f"Transaction ID: #{transaction['id']}"])
            print(success)
        else:
            print()
            cancel = PrettyTable()
            cancel.field_names = ["❌ ORDER CANCELLED"]
            cancel.hrules = 1
            cancel.add_row(["Transaction has been cancelled"])
            print(cancel)
            
    except ValueError:
        print("\n❌ Input tidak valid!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    pause()


def create_sell_order():
    """Buat order jual dengan tampilan portfolio yang menarik"""
    clear_screen()
    print_header()
    
    # Header
    header = PrettyTable()
    header.field_names = ["💸 SELL ORDER - INSTANT SELL 💸"]
    header.add_row(["Jual cryptocurrency Anda dengan harga pasar terkini"])
    print(header)
    print()
    
    # Update harga dari API
    print("🔄 Mengambil data harga real-time dari CoinGecko...")
    update_result = update_market_prices_from_api()
    if update_result:
        print("✓ Harga pasar berhasil diperbarui dari API!\n")
    else:
        print("⚠️ Menggunakan harga terakhir dari database\n")
    
    wallet = get_user_wallet(SESSION['current_user'])
    
    # Tampilkan portfolio (aset yang dimiliki)
    portfolio_table = PrettyTable()
    portfolio_table.field_names = ["No", "Crypto", "Your Balance", "Current Price", "Total Value"]
    portfolio_table.hrules = 1
    
    available_cryptos = []
    portfolio_items = []
    
    for crypto, balance in wallet.items():
        if crypto != "USDT" and balance > 0:
            price = get_market_prices().get(crypto, 0)
            total_value = balance * price
            portfolio_items.append((crypto, balance, price, total_value))
            available_cryptos.append(crypto)
    
    if not available_cryptos:
        print("❌ Anda tidak memiliki cryptocurrency untuk dijual")
        print("💡 Silakan beli terlebih dahulu di menu BUY\n")
        pause()
        return
    
    # Sort by total value (highest first)
    portfolio_items.sort(key=lambda x: x[3], reverse=True)
    
    for i, (crypto, balance, price, total_value) in enumerate(portfolio_items, 1):
        portfolio_table.add_row([
            i,
            crypto,
            f"{balance:.8f}",
            f"${price:,.4f}",
            f"${total_value:,.2f}"
        ])
    
    portfolio_table.align["No"] = "c"
    portfolio_table.align["Crypto"] = "c"
    portfolio_table.align["Your Balance"] = "r"
    portfolio_table.align["Current Price"] = "r"
    portfolio_table.align["Total Value"] = "r"
    
    print(portfolio_table)
    
    # Total portfolio value
    total_crypto_value = sum(item[3] for item in portfolio_items)
    usdt_balance = wallet.get("USDT", 0)
    total_portfolio = total_crypto_value + usdt_balance
    
    print()
    summary = PrettyTable()
    summary.field_names = ["💼 PORTFOLIO SUMMARY", "VALUE"]
    summary.hrules = 1
    summary.add_row(["Crypto Assets", f"${total_crypto_value:,.2f}"])
    summary.add_row(["USDT Balance", f"${usdt_balance:,.2f}"])
    summary.add_row(["─────────────", "─────────────"])
    summary.add_row(["💰 Total Portfolio", f"${total_portfolio:,.2f}"])
    summary.align["💼 PORTFOLIO SUMMARY"] = "l"
    summary.align["VALUE"] = "r"
    print(summary)
    print()
    
    # Input
    print("─" * 60)
    crypto = input("🪙 Crypto yang ingin dijual (Symbol): ").upper().strip()
    
    if crypto not in available_cryptos:
        print(f"\n❌ Anda tidak memiliki {crypto} atau saldo 0")
        pause()
        return
    
    try:
        current_balance = wallet[crypto]
        print(f"📦 Saldo {crypto} Anda: {current_balance:.8f}")
        
        amount = float(input(f"📦 Jumlah {crypto} yang dijual: "))
        
        if amount <= 0:
            print("\n❌ Jumlah harus lebih dari 0!")
            pause()
            return
        
        if amount > current_balance:
            print(f"\n❌ Saldo tidak cukup! Maksimal: {current_balance:.8f} {crypto}")
            pause()
            return
        
        price = get_market_prices().get(crypto, 0)
        total_receive = amount * price
        
        # Preview Order dengan PrettyTable
        print()
        preview = PrettyTable()
        preview.field_names = ["📋 SELL ORDER SUMMARY", ""]
        preview.hrules = 1
        preview.add_row(["Crypto", crypto])
        preview.add_row(["Amount to Sell", f"{amount:.8f} {crypto}"])
        preview.add_row(["Current Price", f"${price:,.4f}"])
        preview.add_row(["─────────────", "─────────────"])
        preview.add_row(["💵 You Will Receive", f"${total_receive:,.2f} USDT"])
        preview.add_row(["📊 Remaining Balance", f"{current_balance - amount:.8f} {crypto}"])
        preview.add_row(["💰 New USDT Balance", f"${usdt_balance + total_receive:,.2f}"])
        
        preview.align["📋 SELL ORDER SUMMARY"] = "l"
        preview.align[""] = "r"
        print(preview)
        print()
        
        # Konfirmasi
        confirm = input("✅ Konfirmasi order SELL? (y/n): ").lower()
        
        if confirm == 'y':
            # Eksekusi order
            wallet[crypto] -= amount
            wallet["USDT"] = wallet.get("USDT", 0) + total_receive
            update_user_wallet(SESSION['current_user'], wallet)
            
            transaction = {
                "id": len(get_transactions()) + 1,
                "user": SESSION['current_user'],
                "type": "SELL",
                "crypto": crypto,
                "amount": amount,
                "price": price,
                "total": total_receive,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "COMPLETED"
            }
            
            add_transaction(transaction)
            
            # Success message
            print()
            success = PrettyTable()
            success.field_names = ["✅ ORDER EXECUTED SUCCESSFULLY"]
            success.hrules = 1
            success.add_row([f"Sold {amount:.8f} {crypto}"])
            success.add_row([f"Received: ${total_receive:,.2f} USDT"])
            success.add_row([f"Transaction ID: #{transaction['id']}"])
            print(success)
        else:
            print()
            cancel = PrettyTable()
            cancel.field_names = ["❌ ORDER CANCELLED"]
            cancel.hrules = 1
            cancel.add_row(["Transaction has been cancelled"])
            print(cancel)
            
    except ValueError:
        print("\n❌ Input tidak valid!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    pause()


# ==================== CRUD KOIN LOKAL ====================

def manage_local_coins():
    """Menu manajemen koin lokal (CRUD)"""
    while True:
        clear_screen()
        print_header()
        
        # Buat tabel menu CRUD
        table = PrettyTable()
        table.field_names = ["No", "Menu CRUD Koin Lokal"]
        table.align["No"] = "c"
        table.align["Menu CRUD Koin Lokal"] = "l"
        table.hrules = 1
        
        table.add_row(["1", "➕ Tambah Koin Baru (Create)"])
        table.add_row(["2", "✏️  Update Harga Koin (Update)"])
        table.add_row(["3", "🗑️  Hapus Koin (Delete)"])
        table.add_row(["4", "🔄 Reset 24h Change"])
        table.add_row(["0", "🔙 Kembali ke Menu Utama"])
        
        print(table)
        
        choice = input("\n    🎯 Pilih menu: ").strip()
        
        if choice == "1":
            add_local_coin_menu()
        elif choice == "2":
            update_local_coin_menu()
        elif choice == "3":
            delete_local_coin_menu()
        elif choice == "4":
            reset_24h_change_menu()
        elif choice == "0":
            break
        else:
            print("\n    ✗ Pilihan tidak valid!")
            pause()


def add_local_coin_menu():
    """Tambah koin lokal baru"""
    clear_screen()
    print_header()
    print("=== TAMBAH KOIN LOKAL BARU ===\n")
    
    try:
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
        if coin_symbol_exists(symbol):
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
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            new_coin = {
                "name": name,
                "symbol": symbol,
                "price": price,
                "price_24h_ago": price,
                "description": description,
                "created_by": SESSION['current_user'],
                "created_date": current_time,
                "last_updated": current_time
            }
            
            add_local_coin(new_coin)
            update_market_price(symbol, price)
            
            print(f"\n    ✓ Koin {name} ({symbol}) berhasil ditambahkan!")
        else:
            print("\n    ✗ Penambahan koin dibatalkan")
            
    except ValueError:
        print("\n    ✗ Input harga tidak valid!")
    except Exception as e:
        print(f"\n    ✗ Terjadi error: {e}")
    
    pause()


def update_local_coin_menu():
    """Update harga koin lokal"""
    clear_screen()
    print_header()
    print("=== UPDATE HARGA KOIN LOKAL ===\n")
    
    if not get_local_coins():
        print("    Belum ada koin lokal yang dapat diupdate.")
        pause()
        return
    
    # Tampilkan daftar koin lokal
    print("Koin Lokal yang Tersedia:\n")
    for i, coin in enumerate(get_local_coins(), 1):
        current_price = coin.get("price", 0)
        print(f"    {i}. {coin['symbol']:6s} - {coin['name']:15s} ${current_price:>10,.4f}")
    
    print()
    symbol = input("    Masukkan symbol koin yang akan diupdate: ").upper().strip()
    
    # Cari koin
    coin_found = get_coin_by_symbol(symbol)
    
    if not coin_found:
        print(f"\n    ✗ Koin dengan symbol {symbol} tidak ditemukan!")
        pause()
        return
    
    try:
        current_price = coin_found.get("price", 0)
        price_24h_ago = coin_found.get("price_24h_ago", current_price)
        
        print(f"\n{'='*50}")
        print(f"Koin          : {coin_found['name']} ({symbol})")
        print(f"Harga Saat Ini: ${current_price:,.4f}")
        print(f"Harga 24h Lalu: ${price_24h_ago:,.4f}")
        print(f"{'='*50}\n")
        
        new_price = float(input("    Harga baru (USD): $"))
        
        if new_price <= 0:
            print("\n    ✗ Harga harus lebih dari 0!")
            pause()
            return
        
        # Preview perubahan
        price_diff = new_price - current_price
        price_diff_pct = ((new_price - current_price) / current_price) * 100 if current_price > 0 else 0
        
        if price_24h_ago > 0:
            new_change_24h = ((new_price - price_24h_ago) / price_24h_ago) * 100
        else:
            new_change_24h = 0.0
        
        print(f"\n{'='*50}")
        print("PREVIEW PERUBAHAN:")
        print(f"Harga Lama       : ${current_price:,.4f}")
        print(f"Harga Baru       : ${new_price:,.4f}")
        print(f"Selisih          : ${price_diff:+,.4f} ({price_diff_pct:+.2f}%)")
        print(f"24h Change Baru  : {new_change_24h:+.2f}%")
        print(f"{'='*50}")
        
        confirm = input("\n    Konfirmasi update? (y/n): ").lower()
        
        if confirm == 'y':
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            updates = {
                "price": new_price,
                "last_updated": current_time
            }
            
            update_local_coin(symbol, updates)
            update_market_price(symbol, new_price)
            
            print(f"\n    ✓ Harga {coin_found['name']} ({symbol}) berhasil diupdate!")
            print(f"      Harga: ${current_price:,.4f} → ${new_price:,.4f}")
            print(f"      24h Change: {new_change_24h:+.2f}%")
        else:
            print("\n    ✗ Update dibatalkan")
            
    except ValueError:
        print("\n    ✗ Input harga tidak valid!")
    except Exception as e:
        print(f"\n    ✗ Terjadi error: {e}")
    
    pause()


def delete_local_coin_menu():
    """Hapus koin lokal"""
    clear_screen()
    print_header()
    print("=== HAPUS KOIN LOKAL ===\n")
    
    if not get_local_coins():
        print("    Belum ada koin lokal yang dapat dihapus.")
        pause()
        return
    
    # Tampilkan daftar koin lokal
    print("Koin Lokal yang Tersedia:\n")
    for i, coin in enumerate(get_local_coins(), 1):
        print(f"    {i}. {coin['symbol']:6s} - {coin['name']:15s} ${coin.get('price', 0):>10,.4f}")
    
    print()
    symbol = input("    Masukkan symbol koin yang akan dihapus: ").upper().strip()
    
    # Cari koin
    coin_found = get_coin_by_symbol(symbol)
    
    if not coin_found:
        print(f"\n    ✗ Koin dengan symbol {symbol} tidak ditemukan!")
        pause()
        return
    
    # Konfirmasi penghapusan
    print(f"\n{'='*50}")
    print(f"KONFIRMASI HAPUS:")
    print(f"Nama        : {coin_found['name']}")
    print(f"Symbol      : {coin_found['symbol']}")
    print(f"Harga       : ${coin_found.get('price', 0):,.4f}")
    print(f"Dibuat oleh : {coin_found.get('created_by', '-')}")
    print(f"{'='*50}")
    
    confirm = input("\n    Yakin ingin menghapus koin ini? (y/n): ").lower()
    
    if confirm == 'y':
        delete_local_coin(symbol)
        print(f"\n    ✓ Koin {coin_found['name']} ({symbol}) berhasil dihapus!")
    else:
        print("\n    ✗ Penghapusan dibatalkan")
    
    pause()


def reset_24h_change_menu():
    """Reset 24h change koin lokal"""
    clear_screen()
    print_header()
    print("=== RESET 24H CHANGE ===\n")
    
    if not get_local_coins():
        print("    Belum ada koin lokal.")
        pause()
        return
    
    print("Fitur ini akan me-reset 24h change dengan")
    print("mengupdate 'price_24h_ago' ke harga saat ini.\n")
    
    # Tampilkan koin lokal
    print("Koin Lokal:\n")
    for i, coin in enumerate(get_local_coins(), 1):
        current_price = coin.get("price", 0)
        price_24h_ago = coin.get("price_24h_ago", current_price)
        
        if price_24h_ago > 0:
            change = ((current_price - price_24h_ago) / price_24h_ago) * 100
        else:
            change = 0.0
        
        print(f"    {i}. {coin['symbol']:6s} - {coin['name']:15s} ${current_price:>10,.4f} ({change:+.2f}%)")
    
    print("\nOpsi:")
    print("    1. Reset semua koin")
    print("    2. Reset satu koin")
    print("    0. Batal")
    
    choice = input("\n    Pilih: ").strip()
    
    if choice == "1":
        confirm = input("\n    Reset semua koin? (y/n): ").lower()
        if confirm == 'y':
            for coin in get_local_coins():
                updates = {"price_24h_ago": coin.get("price", 0)}
                update_local_coin(coin["symbol"], updates)
            print("\n    ✓ Semua koin berhasil di-reset!")
            print("      Sekarang 24h change = 0% untuk semua koin lokal")
        else:
            print("\n    ✗ Dibatalkan")
            
    elif choice == "2":
        symbol = input("\n    Symbol koin: ").upper().strip()
        coin_found = get_coin_by_symbol(symbol)
        
        if coin_found:
            old_24h = coin_found.get("price_24h_ago", 0)
            updates = {"price_24h_ago": coin_found.get("price", 0)}
            update_local_coin(symbol, updates)
            print(f"\n    ✓ {symbol} berhasil di-reset!")
            print(f"      price_24h_ago: ${old_24h:,.4f} → ${coin_found['price']:,.4f}")
        else:
            print(f"\n    ✗ Koin {symbol} tidak ditemukan!")
    
    pause()


# ==================== TRANSACTION HISTORY ====================

def view_transaction_history():
    """Lihat riwayat transaksi - Admin lihat semua, User lihat miliknya"""
    clear_screen()
    print_header()
    
    # ADMIN: Lihat semua transaksi
    if SESSION['current_level'] == "admin":
        print("=== SEMUA RIWAYAT TRANSAKSI (ALL USERS) ===\n")
        
        if not get_transactions():
            print("    📭 Belum ada transaksi dari semua user")
        else:
            table_data = []
            for trans in reversed(get_transactions()[-50:]):  # 50 transaksi terakhir
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
            
            print(f"\n📊 Total Transaksi: {len(get_transactions())}")
    
    # USER: Lihat transaksi miliknya sendiri
    else:
        print("=== RIWAYAT TRANSAKSI SAYA ===\n")
        
        user_transactions = [t for t in get_transactions() if t["user"] == SESSION['current_user']]
        
        if not user_transactions:
            print("    📭 Belum ada transaksi")
        else:
            table_data = []
            for trans in reversed(user_transactions[-20:]):  # 20 transaksi terakhir
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
            
            print(f"\n📊 Total Transaksi Anda: {len(user_transactions)}")
    
    pause()