import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import time
import os
import threading
from urllib.parse import quote
from datetime import datetime

class HotmailChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotmail Email Checker - Tool kiểm tra email")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Biến điều khiển
        self.is_checking = False
        self.total_emails = 0
        self.current_index = 0
        self.existing_count = 0
        self.non_existing_count = 0
        self.unknown_count = 0
        
        # File handles để ghi real-time
        self.existing_file = None
        self.non_existing_file = None
        self.unknown_file = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
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
        self.file_path_var = tk.StringVar(value="acc.txt")
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
        self.delay_var = tk.StringVar(value="2")
        delay_spinbox = ttk.Spinbox(settings_frame, from_=1, to=10, width=10, textvariable=self.delay_var)
        delay_spinbox.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(settings_frame, text="Timeout (giây):").grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.timeout_var = tk.StringVar(value="10")
        timeout_spinbox = ttk.Spinbox(settings_frame, from_=5, to=30, width=10, textvariable=self.timeout_var)
        timeout_spinbox.grid(row=0, column=3, sticky=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="🚀 Bắt đầu kiểm tra", 
                                      command=self.start_checking, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Dừng", 
                                     command=self.stop_checking, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📂 Mở thư mục", 
                  command=self.open_output_folder).pack(side=tk.LEFT, padx=5)
        
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
        """Bật/tắt proxy entry"""
        if self.use_proxy_var.get():
            self.proxy_entry.config(state='normal')
        else:
            self.proxy_entry.config(state='disabled')
    
    def select_file(self):
        """Chọn file email"""
        filename = filedialog.askopenfilename(
            title="Chọn file email",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
    
    def open_output_folder(self):
        """Mở thư mục chứa file kết quả"""
        output_dir = os.path.dirname(os.path.abspath(__file__))
        if os.name == 'nt':  # Windows
            os.startfile(output_dir)
        elif os.name == 'posix':  # macOS and Linux
            os.system(f'open "{output_dir}"')
    
    def log(self, message):
        """Ghi log vào text widget"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def check_email_exists(self, email, proxy=None):
        """Kiểm tra email có tồn tại không - Logic đơn giản và chính xác"""
        try:
            url = f"https://login.live.com/?username={quote(email)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
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
            
            response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout, allow_redirects=True)
            
            if response.status_code == 200:
                content = response.text
                
                # DEBUG: Log một phần content để kiểm tra
                self.log(f"🔍 Checking response for {email}...")
                
                # BƯỚC 1: Kiểm tra EMAIL KHÔNG TỒN TẠI trước tiên (ƯU TIÊN CAO NHẤT)
                # Patterns từ screenshot của bạn
                error_patterns = [
                    "Chúng tôi không tìm thấy tài khoản Microsoft",
                    "không tìm thấy tài khoản Microsoft",  
                    "That Microsoft account doesn't exist",
                    "Microsoft account doesn't exist",
                    "account doesn't exist",
                    "Hãy thử nhập lại",
                    "tạo tài khoản mới"
                ]
                
                # Kiểm tra từng pattern "không tồn tại"
                for pattern in error_patterns:
                    if pattern.lower() in content.lower():
                        self.log(f"❌ CHƯA TỒN TẠI - Tìm thấy: '{pattern}'")
                        return False
                
                # BƯỚC 2: Kiểm tra EMAIL TỒN TẠI
                # Chỉ kiểm tra nếu KHÔNG có error patterns ở trên
                
                # Patterns chắc chắn email tồn tại
                exist_patterns = [
                    "Nhập mật khẩu",
                    "Enter your password", 
                    "Enter password",
                    "Nhận mã để đăng nhập",
                    "Get a verification code",
                    "Chúng tôi sẽ gửi yêu cầu đăng nhập"
                ]
                
                for pattern in exist_patterns:
                    if pattern.lower() in content.lower():
                        self.log(f"✅ ĐÃ TỒN TẠI - Tìm thấy: '{pattern}'")
                        return True
                
                # BƯỚC 3: Kiểm tra HTML elements chỉ có khi email tồn tại
                password_elements = [
                    'type="password"',
                    'name="passwd"',
                    'id="i0118"'
                ]
                
                password_field_count = 0
                for element in password_elements:
                    if element.lower() in content.lower():
                        password_field_count += 1
                        self.log(f"🔍 Tìm thấy password field: {element}")
                
                if password_field_count > 0:
                    self.log(f"✅ ĐÃ TỒN TẠI - Có {password_field_count} password fields")
                    return True
                
                # BƯỚC 4: Nếu không tìm thấy gì rõ ràng
                self.log(f"⚠️ Không xác định được trạng thái của {email}")
                
                # Debug: In ra một đoạn content để kiểm tra
                content_snippet = content[:500] if len(content) > 500 else content
                self.log(f"📄 Content snippet: {content_snippet}")
                
                return None
                
            else:
                self.log(f"❌ HTTP {response.status_code} cho {email}")
                return None
                
        except requests.exceptions.ProxyError:
            self.log(f"❌ Lỗi proxy cho {email}")
            return None
        except requests.exceptions.Timeout:
            self.log(f"❌ Timeout cho {email}")
            return None
        except requests.exceptions.ConnectionError:
            self.log(f"❌ Lỗi kết nối cho {email}")
            return None
        except Exception as e:
            self.log(f"❌ Lỗi cho {email}: {str(e)}")
            return None
    
    def verify_with_post_request(self, session, email, proxies, timeout):
        """Phương pháp bổ sung: Thử POST request để xác nhận"""
        try:
            # Thử gửi POST request giả lập form login
            post_url = "https://login.live.com/ppsecure/post.srf"
            
            post_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': f'https://login.live.com/?username={quote(email)}',
                'Origin': 'https://login.live.com',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Data giả lập (password sai để kiểm tra response)
            post_data = {
                'login': email,
                'passwd': 'invalid_password_test_123',
                'LoginOptions': '3',
                'type': '11',
                'PPFT': '',  # Token sẽ bị thiếu nhưng không sao
                'idsbho': '1',
                'sso': '',
                'default': 'false'
            }
            
            response = session.post(post_url, headers=post_headers, data=post_data, 
                                  proxies=proxies, timeout=timeout, allow_redirects=True)
            
            if response.status_code in [200, 302]:
                content_lower = response.text.lower()
                
                # Nếu có thông báo sai password = email tồn tại
                if any(pattern in content_lower for pattern in [
                    'your account or password is incorrect',
                    'incorrect password',
                    'wrong password',
                    'password is incorrect',
                    'sign-in error'
                ]):
                    self.log(f"🔍 POST method xác nhận email tồn tại")
                    return True
                    
                # Nếu có thông báo account không tồn tại
                elif any(pattern in content_lower for pattern in [
                    'that microsoft account doesn\'t exist',
                    'account doesn\'t exist',
                    'we couldn\'t find an account'
                ]):
                    self.log(f"🔍 POST method xác nhận email không tồn tại")
                    return False
            
            # Nếu không rõ ràng, return None
            self.log(f"⚠️ Không thể xác định chính xác trạng thái của {email}")
            return None
            
        except Exception as e:
            self.log(f"❌ Lỗi POST verification cho {email}: {str(e)}")
            return None
    
    def read_emails_from_file(self, filename):
        """Đọc email từ file"""
        if not os.path.exists(filename):
            messagebox.showerror("Lỗi", f"File {filename} không tồn tại!")
            return []
        
        emails = []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    email = line.strip()
                    if email and '@' in email:
                        emails.append(email)
            return emails
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file {filename}: {str(e)}")
            return []
    
    def open_output_files(self):
        """Mở các file output để ghi real-time"""
        try:
            self.existing_file = open("da_tao.txt", "w", encoding="utf-8")
            self.non_existing_file = open("chua_tao.txt", "w", encoding="utf-8")  
            self.unknown_file = open("khong_xac_dinh.txt", "w", encoding="utf-8")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo file output: {str(e)}")
            return False
        return True
    
    def close_output_files(self):
        """Đóng các file output"""
        if self.existing_file:
            self.existing_file.close()
        if self.non_existing_file:
            self.non_existing_file.close()
        if self.unknown_file:
            self.unknown_file.close()
    
    def write_result_immediately(self, email, result):
        """Ghi kết quả ngay lập tức vào file"""
        try:
            if result is True and self.existing_file:
                self.existing_file.write(email + '\n')
                self.existing_file.flush()  # Force write to disk
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
        """Cập nhật thống kê"""
        self.existing_label.config(text=f"✅ Đã tạo: {self.existing_count}")
        self.non_existing_label.config(text=f"❌ Chưa tạo: {self.non_existing_count}")
        self.unknown_label.config(text=f"⚠️ Không rõ: {self.unknown_count}")
    
    def checking_worker(self):
        """Worker thread để kiểm tra email"""
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
        
        # Lấy proxy nếu có
        proxy = None
        if self.use_proxy_var.get() and self.proxy_var.get().strip():
            proxy = self.proxy_var.get().strip()
            self.log(f"🌐 Sử dụng proxy: {proxy}")
        else:
            self.log("🌐 Không sử dụng proxy")
        
        self.log(f"🚀 Bắt đầu kiểm tra {self.total_emails} email...")
        
        delay = int(self.delay_var.get())
        
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
            
            # Ghi kết quả ngay lập tức
            self.write_result_immediately(email, result)
            self.update_stats()
            
            if self.current_index < self.total_emails and self.is_checking:
                self.log(f"⏳ Đợi {delay} giây...")
                for _ in range(delay * 10):  # Check every 0.1s for stop signal
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
        """Bắt đầu kiểm tra"""
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
        """Dừng kiểm tra"""
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
