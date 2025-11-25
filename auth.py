"""
Authentication Module
Login, Register, Logout
"""

from datetime import datetime
from prettytable import PrettyTable
import pwinput
import time

from config import SESSION, USER_INITIAL_USDT, MAX_LOGIN_ATTEMPTS, LOCKOUT_SECONDS
from database import get_user, add_user, user_exists, save_database
from utils import clear_screen, pause, blockchain_loading, verification_animation, countdown_timer


def register():
    """Registrasi user baru"""
    try:
        clear_screen()
        print_header()
        
        # Header registrasi
        reg_header = PrettyTable()
        reg_header.field_names = ["📝 FORM REGISTRASI"]
        reg_header.add_row(["Buat akun baru untuk mengakses sistem"])
        print(reg_header)
        print()
        
        # Input Username
        while True:
            try:
                username = input("    👤 Username : ").lower().strip()
                
                if not username or username == "":
                    print("    ❌ Username tidak boleh kosong!\n")
                    continue
                if len(username) < 4:
                    print("    ❌ Username minimal 4 karakter!\n")
                    continue
                if user_exists(username):
                    print("    ❌ Username sudah digunakan! Pilih yang lain.\n")
                    continue
                print("    ✅ Username tersedia!")
                break
            except KeyboardInterrupt:
                print("\n    ⚠️  Input dibatalkan")
                pause()
                return
        
        # Input Password dengan pwinput (masked)
        while True:
            try:
                password = pwinput.pwinput(prompt="    🔒 Password : ", mask="*")
                
                if not password or password.strip() == "":
                    print("    ❌ Password tidak boleh kosong!\n")
                    continue
                if len(password) < 6:
                    print("    ❌ Password minimal 6 karakter!\n")
                    continue
                
                print("    ✅ Password diterima!")
                
                confirm_pass = pwinput.pwinput(prompt="    🔒 Konfirmasi: ", mask="*")
                if password != confirm_pass:
                    print("    ❌ Password tidak cocok! Coba lagi.\n")
                    continue
                print("    ✅ Password confirmed!")
                break
            except KeyboardInterrupt:
                print("\n    ⚠️  Input dibatalkan")
                pause()
                return
        
        # Pilih Level Akses
        print()
        level_table = PrettyTable()
        level_table.field_names = ["NO", "LEVEL AKSES", "HAK AKSES"]
        level_table.add_row(["1", "User (Trader)", "✅ Trading, ✅ Wallet, ❌ CRUD Koin"])
        level_table.add_row(["2", "Admin", "✅ CRUD Koin, ❌ Trading, ❌ Wallet"])
        level_table.align["NO"] = "c"
        level_table.align["LEVEL AKSES"] = "l"
        level_table.align["HAK AKSES"] = "l"
        print(level_table)
        print()
        
        while True:
            try:
                level_choice = input("    Pilihan [1/2]: ").strip()
                if level_choice == "1" or level_choice == "":
                    level = "user"
                    print("    ✅ Level: User")
                    break
                elif level_choice == "2":
                    level = "admin"
                    print("    ✅ Level: Admin")
                    break
                else:
                    print("    ❌ Pilihan tidak valid!")
            except KeyboardInterrupt:
                print("\n    ⚠️  Input dibatalkan")
                pause()
                return
        
        print()
        
        # Proses registrasi dengan loading
        process_table = PrettyTable()
        process_table.field_names = ["STATUS"]
        process_table.add_row(["🔄 Memproses registrasi..."])
        print(process_table)
        time.sleep(1)
        
        # Simpan user ke database
        if level == "admin":
            wallets = {}
            bonus_msg = "Tidak ada wallet (Admin mode)"
        else:
            wallets = {
                "USDT": USER_INITIAL_USDT,
                "BTC": 0.0,
                "ETH": 0.0,
                "BNB": 0.0
            }
            bonus_msg = "Bonus USDT $10,000 telah ditambahkan!"

        user_data = {
            'password': password,
            'level': level,
            'join_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'wallets': wallets
        }
        
        add_user(username, user_data)
        
        # Loading animation
        print()
        for i in range(101):
            filled = int(20 * i / 100)
            bar = '█' * filled + '░' * (20 - filled)
            import sys
            sys.stdout.write(f'\r    [{bar}] {i}%')
            sys.stdout.flush()
            time.sleep(0.02)
        
        print("\n")
        
        # Success message
        clear_screen()
        print_header()
        
        success_box = PrettyTable()
        success_box.field_names = ["✅ REGISTRASI BERHASIL"]
        success_box.add_row([f"Selamat datang, {username}! 🎉"])
        success_box.add_row(["Akun Anda telah dibuat"])
        success_box.add_row([bonus_msg])
        success_box.add_row(["Silakan login untuk melanjutkan"])
        print(success_box)
        
        # Detail akun
        print()
        detail_table = PrettyTable()
        detail_table.field_names = ["INFORMASI AKUN", "DATA"]
        detail_table.add_row(["👤 Username", username])
        detail_table.add_row(["🎖️  Level", level.upper()])

        if level == "user":
            detail_table.add_row(["💰 Bonus USDT", "$10,000.00"])
        else:
            detail_table.add_row(["💰 Wallet", "Tidak tersedia (Admin)"])
            
        detail_table.add_row(["📅 Tanggal Bergabung", user_data['join_date']])
        
        detail_table.align["INFORMASI AKUN"] = "l"
        detail_table.align["DATA"] = "l"
        print(detail_table)
        
        # Tips
        print()
        tips = PrettyTable()
        tips.field_names = ["💡 TIPS KEAMANAN"]
        tips.add_row(["Simpan kredensial Anda dengan aman!"])
        print(tips)
        
        pause()
        
    except KeyboardInterrupt:
        print("\n\n    ⚠️  Registrasi dibatalkan")
        pause()
    except Exception as e:
        print(f"\n    ❌ Error saat registrasi: {e}")
        pause()


def login():
    """Login user"""
    try:
        clear_screen()
        print_header()
        
        # Header login
        login_header = PrettyTable()
        login_header.field_names = ["🔐 HALAMAN LOGIN"]
        login_header.add_row(["Masukkan kredensial untuk melanjutkan"])
        print(login_header)
        print()
        
        percobaan = 0
        berhasil = False
        
        while percobaan < MAX_LOGIN_ATTEMPTS and not berhasil:
            try:
                username = input("    👤 Username: ").lower().strip()
                
                if not username or username == "":
                    print("    ❌ Username tidak boleh kosong!\n")
                    continue
                
                password = pwinput.pwinput(prompt="    🔒 Password: ", mask="*")
                
                if not password:
                    print("    ❌ Password tidak boleh kosong!\n")
                    continue
                
                print()
                
                # Validasi login
                user = get_user(username)
                if user and password == user['password']:
                    SESSION['current_user'] = username
                    SESSION['current_level'] = user['level']
                    berhasil = True
                    
                    # Login berhasil - Animasi loading
                    blockchain_loading()
                    verification_animation()
                    
                    time.sleep(0.5)
                    return True
                    
                else:
                    percobaan += 1
                    sisa = MAX_LOGIN_ATTEMPTS - percobaan
                    if sisa > 0:
                        print(f"    ❌ Username atau password salah! Sisa percobaan: {sisa}\n")
                    else:
                        print("    🚫 Username atau password salah 3 kali!")
                        print(f"    ⏳ Silakan tunggu {LOCKOUT_SECONDS} detik sebelum mencoba lagi.")
                        
                        countdown_timer(LOCKOUT_SECONDS)
                        
                        print("    ✅ Waktu tunggu selesai. Anda bisa mencoba login kembali.")
                        time.sleep(2)
                        return False
                        
            except KeyboardInterrupt:
                print("\n    ⚠️  Login dibatalkan")
                pause()
                return False
            except Exception as e:
                print(f"    ❌ Error saat login: {e}")
                percobaan += 1
        
        return berhasil
        
    except KeyboardInterrupt:
        print("\n\n    ⚠️  Login dibatalkan")
        pause()
        return False
    except Exception as e:
        print(f"\n    ❌ Error pada fungsi login: {e}")
        pause()
        return False


def logout():
    """Logout dan hapus sesi"""
    clear_screen()
    print_header()
    
    logout_box = PrettyTable()
    logout_box.field_names = ["🔓 LOGOUT"]
    logout_box.add_row(["✓ Sesi API dihapus"])
    logout_box.add_row([f"✓ Logout berhasil. Sampai jumpa, {SESSION['current_user']}!"])
    print(logout_box)
    
    SESSION['current_user'] = None
    SESSION['current_level'] = None
    pause()


def print_header():
    """Print header aplikasi"""
    from datetime import datetime
    
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