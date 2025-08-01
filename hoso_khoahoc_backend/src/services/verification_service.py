# src/services/verification_service.py

import re
import time
from bs4 import BeautifulSoup

# Import các thư viện của Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def normalize_text(text):
    """
    Hàm chuẩn hóa văn bản: xóa khoảng trắng thừa, ký tự đặc biệt,
    và chuyển về chữ thường để dễ so sánh.
    """
    if not text:
        return ""
    # Chuyển về chữ thường
    text = text.lower()
    # Xóa các ký tự không phải chữ cái, số, hoặc khoảng trắng
    text = re.sub(r'[^\w\s]', '', text)
    # Xóa khoảng trắng thừa
    text = " ".join(text.split())
    return text

def verify_work_from_url(work_title: str, journal_url: str) -> dict:
    """
    PHIÊN BẢN NÂNG CẤP: Sử dụng Selenium Manager để tự động quản lý WebDriver.
    """
    if not journal_url:
        return {"verified": False, "status": "NO_URL", "message": "Không có URL để kiểm tra."}

    # Cấu hình để Selenium chạy ở chế độ "headless" (không mở cửa sổ trình duyệt)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    
    driver = None # Khởi tạo driver là None

    try:
        # Selenium sẽ tự động tìm hoặc tải chromedriver.exe phù hợp
        driver = webdriver.Chrome(options=chrome_options)
        
        # Mở URL
        driver.get(journal_url)
        
        # Chờ 3 giây để đảm bảo JavaScript đã chạy và tải xong hết nội dung
        time.sleep(3) 
        
        # Lấy toàn bộ nội dung HTML của trang SAU KHI JavaScript đã chạy
        page_source = driver.page_source
        
        # Dùng BeautifulSoup để phân tích nội dung HTML hoàn chỉnh này
        soup = BeautifulSoup(page_source, 'html.parser')

        # Lấy toàn bộ văn bản trên trang để tăng khả năng tìm thấy
        page_text = soup.get_text()

        # Chuẩn hóa văn bản để so sánh
        normalized_user_title = normalize_text(work_title)
        normalized_page_text = normalize_text(page_text)

        # Đối chiếu
        if normalized_user_title in normalized_page_text:
            return {
                "verified": True,
                "status": "VERIFIED_SELENIUM",
                "message": f"Đã xác minh. Tên công trình được tìm thấy trong nội dung trang web.",
            }
        else:
            return {
                "verified": False,
                "status": "NOT_FOUND_SELENIUM",
                "message": "Không tìm thấy tên công trình trên trang web sau khi đã dùng Selenium.",
            }

    except Exception as e:
        return {"verified": False, "status": "SELENIUM_ERROR", "message": f"Lỗi Selenium: {e}"}
    finally:
        # Luôn luôn đóng trình duyệt ảo sau khi làm xong để giải phóng tài nguyên
        if driver:
            driver.quit()