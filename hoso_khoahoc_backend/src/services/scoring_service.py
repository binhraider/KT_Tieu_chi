# src/services/scoring_service.py

# Giả sử bạn có một file repository để xử lý việc truy vấn CSDL
# Chúng ta sẽ tạo file này ở bước tiếp theo.
from repositories.journal_repository import JournalRepository

class ScoringService:
    """
    Service này chứa toàn bộ logic nghiệp vụ liên quan đến việc tính điểm
    cho các công trình khoa học.
    """
    def __init__(self, db_connection):
        """
        Khởi tạo service với một kết nối đến database.
        
        Args:
            db_connection: Đối tượng kết nối từ mysql.connector.
        """
        # Service này sẽ sử dụng JournalRepository để nói chuyện với database.
        self.journal_repo = JournalRepository(db_connection)

    def calculate_score_for_article(self, journal_id, publication_date, publication_type=None):
        """
        Tính điểm cho một bài báo khoa học dựa trên thông tin đã có.

        Args:
            journal_id (int): ID của tạp chí trong bảng `journals`.
            publication_date (str or date): Ngày xuất bản của bài báo (ví dụ: '2024-05-15').
            publication_type (str, optional): Loại hình xuất bản (ví dụ: 'Online'). Mặc định là None.

        Returns:
            float: Số điểm tính được. Trả về 0.0 nếu không tìm thấy quy tắc tính điểm.
        """
        print(f"Bắt đầu tính điểm cho journal_id: {journal_id}, ngày xuất bản: {publication_date}")

        # Gọi đến repository để tìm điểm trong database
        points = self.journal_repo.find_points_for_journal(
            journal_id,
            publication_date,
            publication_type
        )

        if points is not None:
            print(f"Tìm thấy điểm: {points}")
            return points
        
        print("Không tìm thấy quy tắc tính điểm phù hợp. Trả về 0 điểm.")
        return 0.0

    # Bạn có thể thêm các hàm tính điểm cho các loại công trình khác ở đây
    # ví dụ: calculate_score_for_book(), calculate_score_for_patent()
    # ...

