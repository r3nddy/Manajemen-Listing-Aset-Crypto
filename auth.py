"""
Modul Authentication
Login, Register, Logout
"""

from datetime import datetime
from prettytable import PrettyTable
import pwinput
import time

from config import SESSION, usdt_awal_user, max_percobaan_login, detik_lockout
from database import ambil_pengguna, tambah_pengguna, pengguna_ada, simpan_database
from utils import bersihkan_layar, pause, blockchain_loading, verification_animation, countdown_timer


def register():
    """Registrasi pengguna baru"""
    try:
        bersihkan_layar()
        tampilkan_header()
        
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
                if pengguna_ada(username):
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
                pilihan_level = input("    Pilihan [1/2]: ").strip()
                if pilihan_level == "1" or pilihan_level == "":
                    level = "user"
                    print("    ✅ Level: User")
                    break
                elif pilihan_level == "2":
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
        else:
            wallets = {
                "USDT": usdt_awal_user,
                "BTC": 0.0,
                "ETH": 0.0,
                "BNB": 0.0
            }

        data_pengguna = {
            'password': password,
            'level': level,
            'tanggal_gabung': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'wallets': wallets
        }
        
        tambah_pengguna(username, data_pengguna)
        
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
        
        bersihkan_layar()
        tampilkan_header()

        success_box = PrettyTable()
        success_box.field_names = ["✅ REGISTRASI BERHASIL"]
        success_box.add_row([f"Selamat datang, {username}! 🎉"])
        success_box.add_row(["Akun Anda telah dibuat"])
        success_box.add_row(["Silakan login untuk melanjutkan"])
        print(success_box)

        pause()
        
    except KeyboardInterrupt:
        print("\n\n    ⚠️  Registrasi dibatalkan")
        pause()
    except Exception as e:
        print(f"\n    ❌ Error saat registrasi: {e}")
        pause()


def login():
    """Login pengguna"""
    try:
        bersihkan_layar()
        tampilkan_header()
        
        # Header login
        login_header = PrettyTable()
        login_header.field_names = ["🔐 HALAMAN LOGIN"]
        login_header.add_row(["Masukkan kredensial untuk melanjutkan"])
        print(login_header)
        print()
        
        percobaan = 0
        berhasil = False
        
        while percobaan < max_percobaan_login and not berhasil:
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
                pengguna = ambil_pengguna(username)
                if pengguna and password == pengguna['password']:
                    SESSION['current_user'] = username
                    SESSION['current_level'] = pengguna['level']
                    berhasil = True
                    
                    # Login berhasil - Animasi loading
                    blockchain_loading()
                    verification_animation()
                    
                    time.sleep(0.5)
                    return True
                    
                else:
                    percobaan += 1
                    sisa = max_percobaan_login - percobaan
                    if sisa > 0:
                        print(f"    ❌ Username atau password salah! Sisa percobaan: {sisa}\n")
                    else:
                        print("    🚫 Username atau password salah 3 kali!")
                        print(f"    ⏳ Silakan tunggu {detik_lockout} detik sebelum mencoba lagi.")
                        
                        countdown_timer(detik_lockout)
                        
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
    try:
        bersihkan_layar()
        tampilkan_header()
        
        logout_box = PrettyTable()
        logout_box.field_names = ["🔓 LOGOUT"]
        logout_box.add_row([f"✓ Logout berhasil. Sampai jumpa, {SESSION['current_user']}!"])
        print(logout_box)
        
        SESSION['current_user'] = None
        SESSION['current_level'] = None
        pause()
    except Exception as e:
        print(f"Error saat logout: {e}")
        pause()


def tampilkan_header():
    """Tampilkan header aplikasi"""
    try:
        from datetime import datetime
        
        print("\n")
        
        now = datetime.now()
        
        main_table = PrettyTable()
        main_table.field_names = ["Manajemen Listing Aset Crypto 💎"]
        main_table.add_row([f"📅 {now.strftime('%A, %d %B %Y')} | ⏰ {now.strftime('%H:%M:%S')}"])
        main_table.align["Manajemen Listing Aset Crypto 💎"] = "c"
        
        print(main_table)
        
        if SESSION['current_user']:
            user_info = PrettyTable()
            user_info.field_names = ["USER INFO"]
            user_info.add_row([f"👤 {SESSION['current_user']} | 🎖️  {SESSION['current_level'].upper()}"])
            print(user_info)
        
        print()
    except Exception as e:
        print(f"Error saat menampilkan header: {e}")