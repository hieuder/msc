import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import time
import os
import threading
from urllib.parse import quote
from datetime import datetime
import json

class HotmailChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotmail Email Checker - Tool kiểm tra email")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # Control variables
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
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup user interface"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🚀 HOTMAIL EMAIL CHECKER", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="📁 Chọn file email", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="File email:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.file_path_var = tk.StringVar(value="emails.txt")
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="Chọn file", command=self.select_file).grid(row=0, column=2)
        
        # Proxy frame
        proxy_frame = ttk.LabelFrame(main_frame, text="🌐 Proxy Settings", padding="10")
        proxy_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        proxy_frame.columnconfigure(1, weight=1)
        
        self.use_proxy_var = tk.BooleanVar()
        ttk.Checkbutton(proxy_frame, text="Sử dụng proxy", 
                       variable=self.use_proxy_var, command=self.toggle_proxy).grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(proxy_frame, text="Proxy (ip:port):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.proxy_var = tk.StringVar()
        self.proxy_entry = ttk.Entry(proxy_frame, textvariable=self.proxy_var, state='disabled')
        self.proxy_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Cài đặt", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(settings_frame, text="Delay (giây):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.delay_var = tk.StringVar(value="1")
        delay_spinbox = ttk.Spinbox(settings_frame, from_=0.5, to=10, increment=0.5, width=10, textvariable=self.delay_var)
        delay_spinbox.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(settings_frame, text="Timeout (giây):").grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.timeout_var = tk.StringVar(value="15")
        timeout_spinbox = ttk.Spinbox(settings_frame, from_=5, to=60, width=10, textvariable=self.timeout_var)
        timeout_spinbox.grid(row=0, column=3, sticky=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="🚀 Bắt đầu kiểm tra", 
                                      command=self.start_checking)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Dừng", 
                                     command=self.stop_checking, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📂 Mở thư mục", 
                  command=self.open_output_folder).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="🧹 Xóa log", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="📊 Tiến độ", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Chưa bắt đầu")
        ttk.Label(progress_frame, textvariable=self.progress_var, font=('Arial', 10, 'bold')).grid(row=0, column=0)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Stats frame
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        stats_frame.columnconfigure((0, 1, 2), weight=1)
        
        self.existing_label = ttk.Label(stats_frame, text="✅ Đã tạo: 0", foreground='green')
        self.existing_label.grid(row=0, column=0)
        
        self.non_existing_label = ttk.Label(stats_frame, text="❌ Chưa tạo: 0", foreground='red')
        self.non_existing_label.grid(row=0, column=1)
        
        self.unknown_label = ttk.Label(stats_frame, text="⚠️ Không rõ: 0", foreground='orange')
        self.unknown_label.grid(row=0, column=2)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="📝 Log", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def toggle_proxy(self):
        """Enable/disable proxy entry"""
        if self.use_proxy_var.get():
            self.proxy_entry.config(state='normal')
        else:
            self.proxy_entry.config(state='disabled')
    
    def select_file(self):
        """Select email file"""
        filename = filedialog.askopenfilename(
            title="Chọn file email",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
    
    def open_output_folder(self):
        """Open output folder"""
        output_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            if os.name == 'nt':  # Windows
                os.startfile(output_dir)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'xdg-open "{output_dir}"' if os.system('which xdg-open') == 0 else f'open "{output_dir}"')
        except Exception as e:
            self.log(f"❌ Không thể mở thư mục: {str(e)}")
    
    def clear_log(self):
        """Clear log text"""
        self.log_text.delete(1.0, tk.END)
        self.log("🧹 Đã xóa log")
    
    def log(self, message):
        """Write log to text widget"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def check_email_exists(self, email, proxy=None):
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
            
            timeout = int(self.timeout_var.get())
            
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
                self.log(f"❌ HTTP {response.status_code} for {email}")
                return None
                
        except requests.exceptions.ProxyError:
            self.log(f"❌ Proxy error for {email}")
            return None
        except requests.exceptions.Timeout:
            self.log(f"❌ Timeout for {email}")
            return None
        except requests.exceptions.ConnectionError:
            self.log(f"❌ Connection error for {email}")
            return None
        except Exception as e:
            self.log(f"❌ Error for {email}: {str(e)}")
            return None
    
    def read_emails_from_file(self, filename):
        """Read emails from file"""
        if not os.path.exists(filename):
            messagebox.showerror("Lỗi", f"File {filename} không tồn tại!")
            return []
        
        emails = []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    email = line.strip()
                    if email and '@' in email:
                        emails.append(email)
                    elif email:  # Non-empty line without @
                        self.log(f"⚠️ Dòng {line_num}: '{email}' không phải email hợp lệ")
            return emails
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file {filename}: {str(e)}")
            return []
    
    def open_output_files(self):
        """Open output files for writing"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.existing_file = open(f"existing_{timestamp}.txt", "w", encoding="utf-8")
            self.non_existing_file = open(f"non_existing_{timestamp}.txt", "w", encoding="utf-8")  
            self.unknown_file = open(f"unknown_{timestamp}.txt", "w", encoding="utf-8")
            return True
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo file output: {str(e)}")
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
            self.log(f"❌ Lỗi đóng file: {str(e)}")
    
    def write_result_immediately(self, email, result):
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
            self.log(f"❌ Lỗi ghi file cho {email}: {str(e)}")
    
    def update_stats(self):
        """Update statistics"""
        self.existing_label.config(text=f"✅ Đã tạo: {self.existing_count}")
        self.non_existing_label.config(text=f"❌ Chưa tạo: {self.non_existing_count}")
        self.unknown_label.config(text=f"⚠️ Không rõ: {self.unknown_count}")
    
    def checking_worker(self):
        """Worker thread to check emails"""
        file_path = self.file_path_var.get()
        emails = self.read_emails_from_file(file_path)
        
        if not emails:
            self.log("❌ Không có email nào để kiểm tra!")
            self.stop_checking()
            return
        
        self.total_emails = len(emails)
        self.progress_bar.config(maximum=self.total_emails)
        
        if not self.open_output_files():
            self.stop_checking()
            return
        
        # Get proxy if enabled
        proxy = None
        if self.use_proxy_var.get() and self.proxy_var.get().strip():
            proxy = self.proxy_var.get().strip()
            self.log(f"🌐 Sử dụng proxy: {proxy}")
        else:
            self.log("🌐 Không sử dụng proxy")
        
        self.log(f"🚀 Bắt đầu kiểm tra {self.total_emails} email...")
        
        delay = float(self.delay_var.get())
        
        for i, email in enumerate(emails):
            if not self.is_checking:
                break
                
            self.current_index = i + 1
            self.progress_var.set(f"Đang kiểm tra ({self.current_index}/{self.total_emails}): {email}")
            self.progress_bar.config(value=self.current_index)
            
            self.log(f"📧 Kiểm tra: {email}")
            
            result = self.check_email_exists(email, proxy)
            
            if result is True:
                self.log(f"✅ Email đã tồn tại: {email}")
            elif result is False:
                self.log(f"❌ Email chưa tồn tại: {email}")
            else:
                self.log(f"⚠️ Không xác định được: {email}")
            
            # Write result immediately
            self.write_result_immediately(email, result)
            self.update_stats()
            
            if self.current_index < self.total_emails and self.is_checking:
                self.log(f"⏳ Đợi {delay} giây...")
                for _ in range(int(delay * 10)):  # Check every 0.1s for stop signal
                    if not self.is_checking:
                        break
                    time.sleep(0.1)
        
        self.close_output_files()
        
        if self.is_checking:  # Completed normally
            self.log(f"🎉 Hoàn thành! Đã kiểm tra {self.current_index}/{self.total_emails} email")
            self.progress_var.set("Hoàn thành!")
            messagebox.showinfo("Hoàn thành", 
                              f"Đã kiểm tra xong!\n"
                              f"✅ Đã tạo: {self.existing_count}\n"
                              f"❌ Chưa tạo: {self.non_existing_count}\n"
                              f"⚠️ Không rõ: {self.unknown_count}")
        else:
            self.log("⏹️ Đã dừng kiểm tra")
            self.progress_var.set("Đã dừng")
        
        self.stop_checking()
    
    def start_checking(self):
        """Start checking"""
        if self.is_checking:
            return
        
        # Reset counters
        self.existing_count = 0
        self.non_existing_count = 0
        self.unknown_count = 0
        self.current_index = 0
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        self.is_checking = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        # Start worker thread
        thread = threading.Thread(target=self.checking_worker, daemon=True)
        thread.start()
    
    def stop_checking(self):
        """Stop checking"""
        self.is_checking = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

def main():
    root = tk.Tk()
    app = HotmailChecker(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()