"""
Menu Module
Semua tampilan menu dan UI
"""

from prettytable import PrettyTable
from datetime import datetime
from config import SESSION
from utils import clear_screen


def print_header():
    """Print header aplikasi"""
    clear_screen()
    print("\n")
    
    now = datetime.now()
    
    main_table = PrettyTable()
    main_table.field_names = ["CRYPTO TRADING TERMINAL - v2.0 💎"]
    main_table.add_row([f"📅 {now.strftime('%A, %d %B %Y')} | ⏰ {now.strftime('%H:%M:%S')}"])
    main_table.align["CRYPTO TRADING TERMINAL - v2.0 💎"] = "c"
    
    print(main_table)
    
    if SESSION['current_user']:
        user_info = PrettyTable()
        user_info.field_names = ["USER INFO"]
        user_info.add_row([f"👤 {SESSION['current_user']} | 🎖️  {SESSION['current_level'].upper()}"])
        print(user_info)
    
    print()


def print_auth_menu():
    """Menu login/register"""
    menu = PrettyTable()
    menu.field_names = ["NO", "MENU", "KETERANGAN"]
    menu.hrules = 1
    menu.add_row(["1", "🔐 LOGIN", "Masuk ke akun Anda"])
    menu.add_row(["2", "📝 REGISTER", "Buat akun baru"])
    menu.add_row(["3", "❌ EXIT", "Keluar dari aplikasi"])
    
    menu.align["NO"] = "c"
    menu.align["MENU"] = "l"
    menu.align["KETERANGAN"] = "l"
    
    print(menu)
    print()


def main_menu():
    """Tampilkan menu utama trading - berbeda untuk admin dan user"""
    print_header()
    
    # Buat tabel menggunakan PrettyTable
    table = PrettyTable()
    table.field_names = ["No", "Pilihan Menu"]
    
    # Set alignment
    table.align["No"] = "c"
    table.align["Pilihan Menu"] = "l"
    table.hrules = 1
    
    # Set width kolom
    table.max_width["Pilihan Menu"] = 40
    
    # MENU UNTUK ADMIN
    if SESSION['current_level'] == "admin":
        table.add_row(["1", "📊 Lihat Harga Pasar (Live)"])
        table.add_row(["2", "⚙️  Listing Koin Baru (CRUD)"])
        table.add_row(["3", "📜 Lihat Semua Transaksi (All Users)"])
        table.add_row(["0", "🚪 Keluar & Hapus Sesi"])
    
    # MENU UNTUK USER
    else:
        table.add_row(["1", "📊 Lihat Harga Pasar (Live)"])
        table.add_row(["2", "💼 Exchange & Wallet"])
        table.add_row(["3", "💰 BUY"])
        table.add_row(["4", "💸 SELL"])
        table.add_row(["5", "📜 Lihat Riwayat Transaksi Saya"])
        table.add_row(["0", "🚪 Keluar & Hapus Sesi"])

    print(table)


def show_message(title, messages, msg_type="info"):
    """Tampilkan message box"""
    table = PrettyTable()
    
    # Emoji berdasarkan tipe
    emoji_map = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️"
    }
    
    emoji = emoji_map.get(msg_type, "ℹ️")
    table.field_names = [f"{emoji} {title}"]
    table.hrules = 1
    
    if isinstance(messages, list):
        for msg in messages:
            table.add_row([msg])
    else:
        table.add_row([messages])
    
    print(table)