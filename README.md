# 🚀 Hotmail Email Checker

Tool kiểm tra email Hotmail/Outlook có tồn tại hay không. Hỗ trợ cả giao diện đồ họa (GUI) và dòng lệnh (CLI).

## ✨ Tính năng

- ✅ Kiểm tra email Hotmail/Outlook có tồn tại
- 🌐 Hỗ trợ proxy (HTTP/HTTPS)
- ⚙️ Tùy chỉnh delay và timeout
- 📊 Hiển thị tiến độ real-time
- 📁 Xuất kết quả ra file riêng biệt
- 🎯 Hỗ trợ cả GUI và CLI
- 🛡️ Xử lý lỗi tốt và graceful shutdown

## 🚀 Cài đặt

### Yêu cầu hệ thống
- Python 3.7+
- pip

### Cài đặt dependencies
```bash
pip install -r requirements.txt
```

**Lưu ý**: `tkinter` thường đã có sẵn với Python, nhưng nếu gặp lỗi, hãy cài đặt:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**CentOS/RHEL:**
```bash
sudo yum install python3-tkinter
```

**macOS:**
```bash
brew install python-tk
```

## 📖 Cách sử dụng

### 🖥️ GUI Version

Chạy ứng dụng với giao diện đồ họa:

```bash
python hotmail_checker_gui.py
```

**Tính năng GUI:**
- Chọn file email từ giao diện
- Cài đặt proxy dễ dàng
- Điều chỉnh delay và timeout
- Xem tiến độ real-time
- Xem log chi tiết
- Mở thư mục output

### 💻 CLI Version

Chạy ứng dụng từ dòng lệnh:

```bash
# Cơ bản
python hotmail_checker_cli.py emails.txt

# Với proxy
python hotmail_checker_cli.py emails.txt --proxy 127.0.0.1:8080

# Tùy chỉnh delay và timeout
python hotmail_checker_cli.py emails.txt --delay 2 --timeout 20

# Xem help
python hotmail_checker_cli.py --help
```

**Tham số CLI:**
- `input_file`: File chứa danh sách email (bắt buộc)
- `--proxy`: Proxy server (format: ip:port)
- `--delay`: Delay giữa các request (giây, mặc định: 1.0)
- `--timeout`: Timeout cho mỗi request (giây, mặc định: 15)

## 📁 Format file input

File email phải có định dạng text, mỗi dòng một email:

```txt
user1@hotmail.com
user2@outlook.com
user3@live.com
```

## 📊 Kết quả output

Ứng dụng sẽ tạo 3 file kết quả với timestamp:

- `existing_YYYYMMDD_HHMMSS.txt` - Email đã tồn tại
- `non_existing_YYYYMMDD_HHMMSS.txt` - Email chưa tồn tại  
- `unknown_YYYYMMDD_HHMMSS.txt` - Email không xác định được

## 🔧 Cấu hình

### Delay
- **GUI**: 0.5 - 10 giây
- **CLI**: Tùy chỉnh tự do
- **Khuyến nghị**: 1-2 giây để tránh bị block

### Timeout
- **GUI**: 5 - 60 giây
- **CLI**: Tùy chỉnh tự do
- **Khuyến nghị**: 15-20 giây cho kết nối chậm

### Proxy
- Hỗ trợ HTTP proxy
- Format: `ip:port`
- Ví dụ: `127.0.0.1:8080`

## ⚠️ Lưu ý quan trọng

1. **Rate Limiting**: Không đặt delay quá thấp để tránh bị Microsoft block
2. **Proxy**: Sử dụng proxy chất lượng để tránh bị chặn IP
3. **File Input**: Đảm bảo file email có định dạng đúng
4. **Kết nối mạng**: Cần kết nối internet ổn định

## 🐛 Xử lý lỗi

### Lỗi thường gặp

**"File không tồn tại"**
- Kiểm tra đường dẫn file
- Đảm bảo file có quyền đọc

**"Lỗi proxy"**
- Kiểm tra proxy có hoạt động không
- Kiểm tra format proxy (ip:port)

**"Timeout"**
- Tăng giá trị timeout
- Kiểm tra kết nối mạng

**"Connection error"**
- Kiểm tra kết nối internet
- Thử lại sau vài phút

## 📝 Ví dụ sử dụng

### Tạo file email test
```bash
echo "test@hotmail.com" > emails.txt
echo "example@outlook.com" >> emails.txt
echo "demo@live.com" >> emails.txt
```

### Chạy với proxy
```bash
python hotmail_checker_cli.py emails.txt --proxy 127.0.0.1:8080 --delay 2
```

### Chạy GUI
```bash
python hotmail_checker_gui.py
```

## 🔒 Bảo mật

- Không chia sẻ file kết quả chứa email thật
- Sử dụng proxy an toàn
- Không spam request quá nhanh

## 📄 License

Dự án này được phát hành dưới MIT License.

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Hãy:

1. Fork dự án
2. Tạo feature branch
3. Commit thay đổi
4. Push lên branch
5. Tạo Pull Request

## 📞 Hỗ trợ

Nếu gặp vấn đề, hãy:

1. Kiểm tra README này
2. Xem log lỗi chi tiết
3. Tạo issue với thông tin chi tiết

---

**Lưu ý**: Tool này chỉ dành cho mục đích giáo dục và kiểm tra email hợp pháp. Không sử dụng để spam hoặc mục đích xấu.