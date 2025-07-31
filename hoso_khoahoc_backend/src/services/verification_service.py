# src/services/verification_service.py
import time
from repositories.work_repository import WorkRepository
from repositories.journal_repository import JournalRepository

# Cài đặt các thư viện này bằng lệnh: pip install requests beautifulsoup4
import requests
from bs4 import BeautifulSoup

class VerificationService:
    """
    Service này chứa logic của "con bot" tự động xác minh.
    Nó sẽ thực hiện các tác vụ chạy nền tốn thời gian.
    """
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.work_repo = WorkRepository(db_connection)
        self.journal_repo = JournalRepository(db_connection)

    def start_verification_task(self, work_id: int):
        """
        Hàm chính để bắt đầu quá trình xác minh cho một công trình.
        Đây là hàm sẽ được chạy dưới nền.
        """
        print(f"--- [BACKGROUND TASK] Bắt đầu xác minh cho công trình có ID: {work_id} ---")
        
        # 1. Lấy thông tin công trình và tạp chí từ database
        work_details = self.work_repo.find_by_id(work_id)
        if not work_details or not work_details.get('journal_id'):
            print(f"[TASK FAILED] Không tìm thấy thông tin công trình hoặc tạp chí cho ID: {work_id}")
            return

        journal_details = self.journal_repo.find_by_id(work_details['journal_id'])
        if not journal_details or not journal_details.get('link'):
            print(f"[TASK FAILED] Không có link để xác minh cho tạp chí ID: {journal_details['id']}")
            self.work_repo.update_status(work_id, 'verification_failed', 'Tạp chí không có link tham khảo trong CSDL.')
            return

        # 2. Logic Web Scraping thực tế
        print(f"Đang truy cập link: {journal_details['link']} để tìm bài báo '{work_details['title']}'...")
        
        try:
            # Gửi yêu cầu HTTP tới trang web của tạp chí
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = requests.get(journal_details['link'], headers=headers, timeout=15)
            response.raise_for_status() # Báo lỗi nếu request không thành công (ví dụ: 404, 500)

            # Phân tích nội dung HTML của trang web
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tìm kiếm tên bài báo trong toàn bộ văn bản của trang
            # Đây là một phương pháp tìm kiếm đơn giản, có thể cần cải tiến cho từng trang cụ thể
            page_text = soup.get_text().lower()
            article_title = work_details['title'].lower()

            if article_title in page_text:
                # Nếu tìm thấy, cập nhật trạng thái là đã xác minh tự động
                verification_notes = "Hệ thống tự động tìm thấy tiêu đề bài báo trên trang tham khảo."
                self.work_repo.update_status(work_id, 'verified_auto', verification_notes)
                print(f"--- [TASK SUCCESS] Đã tự động xác minh thành công công trình ID: {work_id} ---")
            else:
                # Nếu không tìm thấy, chuyển cho người duyệt thủ công
                verification_notes = "Hệ thống không tìm thấy tiêu đề bài báo trên trang tham khảo. Cần xác minh thủ công."
                self.work_repo.update_status(work_id, 'needs_manual_review', verification_notes)
                print(f"--- [TASK INFO] Không tìm thấy kết quả, cần người duyệt thủ công cho ID: {work_id} ---")

        except requests.exceptions.RequestException as e:
            # Xử lý các lỗi liên quan đến mạng (không kết nối được, timeout...)
            print(f"[TASK FAILED] Lỗi mạng khi truy cập link: {e}")
            self.work_repo.update_status(work_id, 'verification_failed', f"Lỗi mạng: {e}")
        except Exception as e:
            # Xử lý các lỗi khác
            print(f"[TASK FAILED] Lỗi không xác định trong quá trình scraping: {e}")
            self.work_repo.update_status(work_id, 'verification_failed', f"Lỗi hệ thống: {e}")

