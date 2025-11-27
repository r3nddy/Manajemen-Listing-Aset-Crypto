"""
Modul Utils
Fungsi bantuan dan animasi
"""

import os
import sys
import time
from config import min_panjang_username, min_panjang_password


# ==================== FUNGSI BANTUAN ====================

def bersihkan_layar():
    """Membersihkan layar terminal"""
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception as e:
        print(f"Error saat membersihkan layar: {e}")
        pass


def pause():
    """Pause dan tunggu user menekan Enter"""
    try:
        input("\n    [Tekan Enter untuk melanjutkan...]")
    except KeyboardInterrupt:
        print("\n")
    except Exception:
        pass


def format_perubahan_harga(perubahan):
    """Format perubahan harga dengan tanda"""
    try:
        if perubahan > 0:
            return f"+{perubahan:.2f}%"
        else:
            return f"{perubahan:.2f}%"
    except Exception:
        return "0.00%"


def validasi_username(username):
    """Validasi username"""
    try:
        if not username or username.strip() == "":
            return False, "Username tidak boleh kosong"
        
        if len(username) < min_panjang_username:
            return False, f"Username minimal {min_panjang_username} karakter"
        
        return True, "Valid"
    except Exception as e:
        return False, f"Error saat validasi: {e}"


def validasi_password(password):
    """Validasi password"""
    try:
        if not password or password.strip() == "":
            return False, "Password tidak boleh kosong"
        
        if len(password) < min_panjang_password:
            return False, f"Password minimal {min_panjang_password} karakter"
        
        return True, "Valid"
    except Exception as e:
        return False, f"Error saat validasi: {e}"


# ==================== ANIMASI ====================

def blockchain_loading():
    """Loading bar dengan tema blockchain"""
    try:
        print("\n")
        print("    ⛓️  Menghubungkan ke Blockchain...")
        print()
        
        for i in range(101):
            terisi = int(20 * i / 100)
            batang = '█' * terisi + '░' * (20 - terisi)
            sys.stdout.write(f'\r    [{batang}] {i}%')
            sys.stdout.flush()
            time.sleep(0.03)
        
        print("\n")
        print("    🔐 Verifikasi Kredensial...")
        time.sleep(1)
        print("    ✅ Koneksi Berhasil!\n")
        time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n\nLoading dibatalkan.")
    except Exception as e:
        print(f"\nError saat loading: {e}")


def verification_animation():
    """Animasi verifikasi"""
    try:
        langkah = [
            "🔍 Memeriksa Username",
            "🔐 Validasi Password",
            "⛓️  Verifikasi Blockchain",
            "🛡️  Checking Security",
            "✅ Authentication Success"
        ]
        
        print()
        for step in langkah:
            print(f"    {step}", end="")
            for _ in range(3):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.2)
            print(" ✓")
            time.sleep(0.3)
        print()
    except KeyboardInterrupt:
        print("\n\nVerifikasi dibatalkan.")
    except Exception as e:
        print(f"\nError saat animasi verifikasi: {e}")


def countdown_timer(detik):
    """Countdown timer untuk lockout"""
    try:
        print("\n")
        for tersisa in range(detik, 0, -1):
            menit, detik_sisa = divmod(tersisa, 60)
            waktu = f'{menit:02d}:{detik_sisa:02d}'
            sys.stdout.write(f'\r    ⏳ Menunggu: {waktu} ')
            sys.stdout.flush()
            time.sleep(1)
        print("\n")
    except KeyboardInterrupt:
        print("\n\nTimer dibatalkan.")
    except Exception as e:
        print(f"\nError saat countdown: {e}")


def progress_bar(pesan="Processing", durasi=1):
    """Progress bar generik"""
    try:
        print()
        for i in range(101):
            terisi = int(20 * i / 100)
            batang = '█' * terisi + '░' * (20 - terisi)
            sys.stdout.write(f'\r    {pesan}: [{batang}] {i}%')
            sys.stdout.flush()
            time.sleep(durasi / 100)
        print("\n")
    except KeyboardInterrupt:
        print("\n\nProgress dibatalkan.")
    except Exception as e:
        print(f"\nError saat menampilkan progress: {e}")