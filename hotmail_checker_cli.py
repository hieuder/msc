#!/usr/bin/env python3
"""
Hotmail Email Checker - CLI Version
Tool kiểm tra email Hotmail/Outlook có tồn tại hay không
"""

import requests
import time
import os
import sys
import argparse
from urllib.parse import quote
from datetime import datetime
import signal
from typing import List, Optional, Tuple
import json

class HotmailCheckerCLI:
    def __init__(self):
        self.is_checking = False
        self.total_emails = 0
        self.current_index = 0
        self.existing_count = 0
        self.non_existing_count = 0
        self.unknown_count = 0
        
        # File handles for real-time writing
        self.existing_file = None
        self.non_existing_file = None
        self.unknown_file = None
        
        # Session for better connection handling
        self.session = requests.Session()
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n⚠️  Nhận tín hiệu dừng (Ctrl+C)...")
        self.stop_checking()
        sys.exit(0)
    
    def print_banner(self):
        """Print application banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🚀 HOTMAIL EMAIL CHECKER                  ║
║                        (CLI Version)                        ║
║                                                              ║
║  Tool kiểm tra email Hotmail/Outlook có tồn tại hay không   ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def print_status(self, message: str, status_type: str = "info"):
        """Print status message with timestamp and color coding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if status_type == "success":
            prefix = "✅"
        elif status_type == "error":
            prefix = "❌"
        elif status_type == "warning":
            prefix = "⚠️"
        elif status_type == "info":
            prefix = "ℹ️"
        else:
            prefix = "📝"
        
        print(f"[{timestamp}] {prefix} {message}")
    
    def check_email_exists(self, email: str, proxy: Optional[str] = None, timeout: int = 15) -> Optional[bool]:
        """Check if email exists - Improved logic"""
        try:
            url = f"https://login.live.com/?username={quote(email)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'no-cache'
            }
            
            proxies = None
            if proxy:
                proxies = {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
            
            response = self.session.get(url, headers=headers, proxies=proxies, timeout=timeout, allow_redirects=True)
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for "doesn't exist" patterns first
                error_patterns = [
                    "that microsoft account doesn't exist",
                    "microsoft account doesn't exist",
                    "account doesn't exist",
                    "we couldn't find an account",
                    "no account found",
                    "create a new account"
                ]
                
                for pattern in error_patterns:
                    if pattern in content:
                        return False
                
                # Check for "exists" patterns
                exist_patterns = [
                    "enter your password",
                    "enter password",
                    "get a verification code",
                    "we'll send a sign-in request",
                    'type="password"',
                    'name="passwd"',
                    'id="i0118"'
                ]
                
                for pattern in exist_patterns:
                    if pattern in content:
                        return True
                
                # If unclear, return None
                return None
                
            else:
                self.print_status(f"HTTP {response.status_code} for {email}", "error")
                return None
                
        except requests.exceptions.ProxyError:
            self.print_status(f"Proxy error for {email}", "error")
            return None
        except requests.exceptions.Timeout:
            self.print_status(f"Timeout for {email}", "error")
            return None
        except requests.exceptions.ConnectionError:
            self.print_status(f"Connection error for {email}", "error")
            return None
        except Exception as e:
            self.print_status(f"Error for {email}: {str(e)}", "error")
            return None
    
    def read_emails_from_file(self, filename: str) -> List[str]:
        """Read emails from file"""
        if not os.path.exists(filename):
            self.print_status(f"File {filename} không tồn tại!", "error")
            return []
        
        emails = []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    email = line.strip()
                    if email and '@' in email:
                        emails.append(email)
                    elif email:  # Non-empty line without @
                        self.print_status(f"Dòng {line_num}: '{email}' không phải email hợp lệ", "warning")
            return emails
        except Exception as e:
            self.print_status(f"Không thể đọc file {filename}: {str(e)}", "error")
            return []
    
    def open_output_files(self) -> bool:
        """Open output files for writing"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.existing_file = open(f"existing_{timestamp}.txt", "w", encoding="utf-8")
            self.non_existing_file = open(f"non_existing_{timestamp}.txt", "w", encoding="utf-8")  
            self.unknown_file = open(f"unknown_{timestamp}.txt", "w", encoding="utf-8")
            return True
        except Exception as e:
            self.print_status(f"Không thể tạo file output: {str(e)}", "error")
            return False
    
    def close_output_files(self):
        """Close output files"""
        try:
            if self.existing_file:
                self.existing_file.close()
            if self.non_existing_file:
                self.non_existing_file.close()
            if self.unknown_file:
                self.unknown_file.close()
        except Exception as e:
            self.print_status(f"Lỗi đóng file: {str(e)}", "error")
    
    def write_result_immediately(self, email: str, result: Optional[bool]):
        """Write result immediately to file"""
        try:
            if result is True and self.existing_file:
                self.existing_file.write(email + '\n')
                self.existing_file.flush()
                self.existing_count += 1
            elif result is False and self.non_existing_file:
                self.non_existing_file.write(email + '\n')
                self.non_existing_file.flush()
                self.non_existing_count += 1
            elif result is None and self.unknown_file:
                self.unknown_file.write(email + '\n')
                self.unknown_file.flush()
                self.unknown_count += 1
        except Exception as e:
            self.print_status(f"Lỗi ghi file cho {email}: {str(e)}", "error")
    
    def print_progress(self, current: int, total: int, email: str):
        """Print progress bar"""
        percentage = (current / total) * 100
        bar_length = 50
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        print(f"\r📊 Progress: [{bar}] {percentage:.1f}% ({current}/{total}) - {email}", end='', flush=True)
    
    def print_final_stats(self):
        """Print final statistics"""
        print("\n" + "="*60)
        print("📊 THỐNG KÊ CUỐI CÙNG")
        print("="*60)
        print(f"✅ Email đã tồn tại: {self.existing_count}")
        print(f"❌ Email chưa tồn tại: {self.non_existing_count}")
        print(f"⚠️  Email không xác định được: {self.unknown_count}")
        print(f"📧 Tổng số email đã kiểm tra: {self.current_index}")
        print("="*60)
    
    def check_emails(self, emails: List[str], proxy: Optional[str], delay: float, timeout: int):
        """Check all emails"""
        self.total_emails = len(emails)
        
        if not self.open_output_files():
            return
        
        # Get proxy if enabled
        if proxy:
            self.print_status(f"Sử dụng proxy: {proxy}", "info")
        else:
            self.print_status("Không sử dụng proxy", "info")
        
        self.print_status(f"Bắt đầu kiểm tra {self.total_emails} email...", "info")
        print()  # Empty line for progress bar
        
        for i, email in enumerate(emails):
            if not self.is_checking:
                break
                
            self.current_index = i + 1
            self.print_progress(self.current_index, self.total_emails, email)
            
            result = self.check_email_exists(email, proxy, timeout)
            
            if result is True:
                self.print_status(f"Email đã tồn tại: {email}", "success")
            elif result is False:
                self.print_status(f"Email chưa tồn tại: {email}", "error")
            else:
                self.print_status(f"Không xác định được: {email}", "warning")
            
            # Write result immediately
            self.write_result_immediately(email, result)
            
            if self.current_index < self.total_emails and self.is_checking:
                time.sleep(delay)
        
        self.close_output_files()
        
        if self.is_checking:  # Completed normally
            print()  # New line after progress bar
            self.print_status(f"Hoàn thành! Đã kiểm tra {self.current_index}/{self.total_emails} email", "success")
        else:
            print()  # New line after progress bar
            self.print_status("Đã dừng kiểm tra", "warning")
        
        self.print_final_stats()
    
    def start_checking(self, input_file: str, proxy: Optional[str], delay: float, timeout: int):
        """Start the checking process"""
        self.is_checking = True
        
        # Reset counters
        self.existing_count = 0
        self.non_existing_count = 0
        self.unknown_count = 0
        self.current_index = 0
        
        # Read emails from file
        emails = self.read_emails_from_file(input_file)
        
        if not emails:
            self.print_status("Không có email nào để kiểm tra!", "error")
            return
        
        # Start checking
        try:
            self.check_emails(emails, proxy, delay, timeout)
        except KeyboardInterrupt:
            self.print_status("Đã dừng bởi người dùng", "warning")
        finally:
            self.stop_checking()
    
    def stop_checking(self):
        """Stop checking"""
        self.is_checking = False

def main():
    parser = argparse.ArgumentParser(
        description="Hotmail Email Checker - CLI Version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python hotmail_checker_cli.py emails.txt
  python hotmail_checker_cli.py emails.txt --proxy 127.0.0.1:8080
  python hotmail_checker_cli.py emails.txt --delay 2 --timeout 20
  python hotmail_checker_cli.py emails.txt --proxy 127.0.0.1:8080 --delay 1.5
        """
    )
    
    parser.add_argument('input_file', help='File chứa danh sách email (mỗi dòng một email)')
    parser.add_argument('--proxy', help='Proxy server (format: ip:port)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay giữa các request (giây, mặc định: 1.0)')
    parser.add_argument('--timeout', type=int, default=15, help='Timeout cho mỗi request (giây, mặc định: 15)')
    parser.add_argument('--version', action='version', version='Hotmail Email Checker CLI v1.0')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"❌ Lỗi: File '{args.input_file}' không tồn tại!")
        sys.exit(1)
    
    # Validate delay
    if args.delay < 0:
        print("❌ Lỗi: Delay phải >= 0!")
        sys.exit(1)
    
    # Validate timeout
    if args.timeout < 1:
        print("❌ Lỗi: Timeout phải >= 1!")
        sys.exit(1)
    
    # Create checker instance
    checker = HotmailCheckerCLI()
    
    # Print banner
    checker.print_banner()
    
    # Print configuration
    print("⚙️  CẤU HÌNH:")
    print(f"   📁 File input: {args.input_file}")
    print(f"   🌐 Proxy: {args.proxy if args.proxy else 'Không sử dụng'}")
    print(f"   ⏱️  Delay: {args.delay} giây")
    print(f"   ⏰ Timeout: {args.timeout} giây")
    print()
    
    # Start checking
    checker.start_checking(args.input_file, args.proxy, args.delay, args.timeout)

if __name__ == "__main__":
    main()