#!/usr/bin/env python3
"""
Test Installation Script
Script kiểm tra cài đặt và hoạt động của Hotmail Email Checker
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Kiểm tra imports...")
    
    try:
        import requests
        print("✅ requests: OK")
    except ImportError as e:
        print(f"❌ requests: FAILED - {e}")
        return False
    
    try:
        import tkinter
        print("✅ tkinter: OK")
    except ImportError as e:
        print(f"❌ tkinter: FAILED - {e}")
        return False
    
    try:
        from urllib.parse import quote
        print("✅ urllib.parse: OK")
    except ImportError as e:
        print(f"❌ urllib.parse: FAILED - {e}")
        return False
    
    try:
        from datetime import datetime
        print("✅ datetime: OK")
    except ImportError as e:
        print(f"❌ datetime: FAILED - {e}")
        return False
    
    return True

def test_files():
    """Test if all required files exist"""
    print("\n📁 Kiểm tra files...")
    
    required_files = [
        "hotmail_checker_gui.py",
        "hotmail_checker_cli.py", 
        "launcher.py",
        "requirements.txt",
        "README.md",
        "sample_emails.txt"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}: OK")
        else:
            print(f"❌ {file}: NOT FOUND")
            all_exist = False
    
    return all_exist

def test_cli_syntax():
    """Test CLI script syntax"""
    print("\n💻 Kiểm tra CLI syntax...")
    
    try:
        with open("hotmail_checker_cli.py", "r") as f:
            content = f.read()
        
        # Basic syntax check
        compile(content, "hotmail_checker_cli.py", "exec")
        print("✅ CLI syntax: OK")
        return True
    except SyntaxError as e:
        print(f"❌ CLI syntax: FAILED - {e}")
        return False
    except Exception as e:
        print(f"❌ CLI syntax: FAILED - {e}")
        return False

def test_gui_syntax():
    """Test GUI script syntax"""
    print("\n🖥️  Kiểm tra GUI syntax...")
    
    try:
        with open("hotmail_checker_gui.py", "r") as f:
            content = f.read()
        
        # Basic syntax check
        compile(content, "hotmail_checker_gui.py", "exec")
        print("✅ GUI syntax: OK")
        return True
    except SyntaxError as e:
        print(f"❌ GUI syntax: FAILED - {e}")
        return False
    except Exception as e:
        print(f"❌ GUI syntax: FAILED - {e}")
        return False

def test_sample_emails():
    """Test sample emails file"""
    print("\n📧 Kiểm tra sample emails...")
    
    try:
        with open("sample_emails.txt", "r") as f:
            emails = f.readlines()
        
        if len(emails) > 0:
            print(f"✅ Sample emails: OK ({len(emails)} emails)")
            return True
        else:
            print("❌ Sample emails: EMPTY")
            return False
    except Exception as e:
        print(f"❌ Sample emails: FAILED - {e}")
        return False

def main():
    """Main test function"""
    print("🚀 HOTMAIL EMAIL CHECKER - INSTALLATION TEST")
    print("=" * 50)
    
    # Run all tests
    tests = [
        test_imports,
        test_files,
        test_cli_syntax,
        test_gui_syntax,
        test_sample_emails
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 KẾT QUẢ KIỂM TRA:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if all(results):
        print("\n🎉 TẤT CẢ KIỂM TRA ĐỀU THÀNH CÔNG!")
        print("🚀 Bạn có thể sử dụng Hotmail Email Checker!")
        print("\n💡 Hướng dẫn sử dụng:")
        print("   GUI: python3 hotmail_checker_gui.py")
        print("   CLI: python3 hotmail_checker_cli.py --help")
        print("   Launcher: python3 launcher.py")
    else:
        print("\n⚠️  MỘT SỐ KIỂM TRA THẤT BẠI!")
        print("🔧 Vui lòng kiểm tra và sửa lỗi trước khi sử dụng.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)