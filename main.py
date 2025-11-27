"""
Main Entry Point
"""

import sys
import time
from prettytable import PrettyTable

from config import SESSION
from database import muat_database
from auth import login, register, logout, tampilkan_header
from menu import tampilkan_menu_auth, menu_utama

from trading import (
    lihat_harga_pasar, 
    buat_order_beli, 
    buat_order_jual,
    lihat_dompet,  
    kelola_koin_lokal,
    lihat_riwayat_transaksi,
    muat_data_awal_pasar
)

from utils import bersihkan_layar, pause


def jalankan_menu_trading():
    """Menu trading setelah login"""
    try:
        # Muat data pasar dari API saat login (1x saja!)
        muat_data_awal_pasar()
        time.sleep(2)
        
        while True:
            try:
                menu_utama()
                pilihan = input("\n    🎯 Pilih menu: ").strip()
                
                # MENU ADMIN
                if SESSION['current_level'] == "admin":
                    if pilihan == "1":
                        lihat_harga_pasar()
                    elif pilihan == "2":
                        kelola_koin_lokal()
                    elif pilihan == "3":
                        lihat_riwayat_transaksi()
                    elif pilihan == "0":
                        logout()
                        break
                    else:
                        print("\n    ❌ Pilihan tidak valid!")
                        pause()
                
                # MENU USER
                else:
                    if pilihan == "1":
                        lihat_harga_pasar()
                    elif pilihan == "2":
                        lihat_dompet()
                    elif pilihan == "3":
                        buat_order_beli()
                    elif pilihan == "4":
                        buat_order_jual()
                    elif pilihan == "5":
                        lihat_riwayat_transaksi()
                    elif pilihan == "0":
                        logout()
                        break
                    else:
                        print("\n    ❌ Pilihan tidak valid!")
                        pause()
                        
            except KeyboardInterrupt:
                print("\n\n    ⚠️  Kembali ke menu...")
                time.sleep(1)
            except Exception as e:
                print(f"\n    ❌ Error di menu trading: {e}")
                pause()
    except Exception as e:
        print(f"Error saat menjalankan menu trading: {e}")
        pause()


def main():
    try:
        # Load database
        muat_database()
        
        while True:
            try:
                tampilkan_header()
                tampilkan_menu_auth()
                
                pilihan = input("    🎯 Pilih Menu [1-3]: ").strip()
                
                if pilihan == '1':
                    if login():
                        jalankan_menu_trading()
                        
                elif pilihan == '2':
                    register()
                    
                elif pilihan == '3':
                    bersihkan_layar()
                    tampilkan_header()
                    
                    exit_box = PrettyTable()
                    exit_box.field_names = ["👋 TERIMA KASIH"]
                    exit_box.add_row(["Terima kasih telah menggunakan"])
                    exit_box.add_row(["Manajemen Listing Aset Crypto"])
                    exit_box.add_row(["👑 Stay Safe, Trade Smart! 👑"])
                    print(exit_box)
                    print()
                    
                    time.sleep(1)
                    break
                    
                else:
                    error = PrettyTable()
                    error.field_names = ["⚠️ ERROR"]
                    error.add_row(["Pilihan tidak valid! Silakan pilih 1-3"])
                    print()
                    print(error)
                    time.sleep(1.5)
                    
            except KeyboardInterrupt:
                print("\n\n    ⚠️  Program dihentikan.")
                konfirmasi = input("    Apakah Anda yakin ingin keluar? (y/n): ").lower()
                if konfirmasi == 'y':
                    print("    👋 Goodbye!\n")
                    break
            except Exception as e:
                error_table = PrettyTable()
                error_table.field_names = ["❌ ERROR"]
                error_table.add_row([f"Terjadi kesalahan: {e}"])
                print()
                print(error_table)
                time.sleep(2)
    except Exception as e:
        print(f"Error pada program utama: {e}")
        pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n    ⚠️  Program dihentikan! ")
        print("    👋 Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Terjadi error: {e}")
        pause()