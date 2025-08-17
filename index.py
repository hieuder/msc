#!/usr/bin/env python3
"""
Hotmail Email Checker Launcher
Script khởi chạy để chọn giữa GUI và CLI version
"""

import os
import sys
import subprocess

def print_banner():
    """Print launcher banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🚀 HOTMAIL EMAIL CHECKER                  ║
║                          LAUNCHER                            ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import requests
        print("✅ requests library: OK")
    except ImportError:
        print("❌ requests library: NOT FOUND")
        print("   Hãy chạy: pip install requests")
        return False
    
    try:
        import tkinter
        print("✅ tkinter library: OK")
    except ImportError:
        print("❌ tkinter library: NOT FOUND")
        print("   Trên Ubuntu/Debian: sudo apt-get install python3-tk")
        print("   Trên CentOS/RHEL: sudo yum install python3-tkinter")
        print("   Trên macOS: brew install python-tk")
        return False
    
    return True

def run_gui():
    """Run GUI version"""
    print("🚀 Khởi chạy GUI version...")
    try:
        subprocess.run([sys.executable, "hotmail_checker_gui.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khởi chạy GUI: {e}")
    except FileNotFoundError:
        print("❌ Không tìm thấy file hotmail_checker_gui.py")

def run_cli():
    """Run CLI version"""
    print("🚀 Khởi chạy CLI version...")
    print("💡 Sử dụng: python hotmail_checker_cli.py --help để xem hướng dẫn")
    try:
        subprocess.run([sys.executable, "hotmail_checker_cli.py", "--help"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khởi chạy CLI: {e}")
    except FileNotFoundError:
        print("❌ Không tìm thấy file hotmail_checker_cli.py")

def show_menu():
    """Show main menu"""
    while True:
        print("\n📋 CHỌN PHIÊN BẢN:")
        print("1. 🖥️  GUI Version (Giao diện đồ họa)")
        print("2. 💻 CLI Version (Dòng lệnh)")
        print("3. 📖 Xem hướng dẫn")
        print("4. 🚪 Thoát")
        
        choice = input("\n👉 Nhập lựa chọn (1-4): ").strip()
        
        if choice == "1":
            run_gui()
        elif choice == "2":
            run_cli()
        elif choice == "3":
            show_help()
        elif choice == "4":
            print("👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ. Vui lòng chọn 1-4.")

def show_help():
    """Show help information"""
    help_text = """
📖 HƯỚNG DẪN SỬ DỤNG:

🖥️  GUI Version:
   - Chạy: python hotmail_checker_gui.py
   - Giao diện đồ họa dễ sử dụng
   - Chọn file email từ giao diện
   - Cài đặt proxy và delay
   - Xem tiến độ real-time

💻 CLI Version:
   - Chạy: python hotmail_checker_cli.py emails.txt
   - Với proxy: --proxy 127.0.0.1:8080
   - Tùy chỉnh delay: --delay 2
   - Tùy chỉnh timeout: --timeout 20

📁 Format file email:
   - Mỗi dòng một email
   - Ví dụ:
     user1@hotmail.com
     user2@outlook.com
     user3@live.com

🌐 Proxy:
   - Format: ip:port
   - Ví dụ: 127.0.0.1:8080

⚙️  Cài đặt dependencies:
   pip install -r requirements.txt
    """
    print(help_text)

def main():
    """Main launcher function"""
    print_banner()
    
    print("🔍 Kiểm tra dependencies...")
    if not check_dependencies():
        print("\n❌ Vui lòng cài đặt dependencies trước khi sử dụng.")
        return
    
    print("\n✅ Tất cả dependencies đã sẵn sàng!")
    
    # Check if files exist
    if not os.path.exists("hotmail_checker_gui.py"):
        print("⚠️  Không tìm thấy hotmail_checker_gui.py")
    
    if not os.path.exists("hotmail_checker_cli.py"):
        print("⚠️  Không tìm thấy hotmail_checker_cli.py")
    
    show_menu()

if __name__ == "__main__":
    main()
