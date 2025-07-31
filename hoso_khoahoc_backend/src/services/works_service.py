# src/services/works_service.py

from repositories.work_repository import WorkRepository
from services.scoring_service import ScoringService
# Giả sử chúng ta sẽ có service này ở bước sau
# from services.verification_service import VerificationService 

class WorksService:
    """
    Service này xử lý tất cả logic nghiệp vụ liên quan đến việc
    quản lý các công trình khoa học của người dùng.
    """
    def __init__(self, db_connection):
        """
        Khởi tạo service với một kết nối đến database.
        """
        self.db_connection = db_connection
        self.work_repo = WorkRepository(db_connection)
        self.scoring_service = ScoringService(db_connection)
        # self.verification_service = VerificationService() # Sẽ được kích hoạt sau

    def add_new_article(self, user_id, article_data):
        """
        Thêm một bài báo khoa học mới cho người dùng.

        Args:
            user_id (int): ID của người dùng đang thực hiện.
            article_data (dict): Dữ liệu của bài báo từ frontend, ví dụ:
                {
                    "title": "Tên bài báo",
                    "journal_id": 48,
                    "publication_date": "2024-01-15",
                    "is_main_author": True,
                    "publication_type": "Online" 
                }

        Returns:
            dict or None: Trả về thông tin công trình đã được thêm vào, hoặc None nếu có lỗi.
        """
        try:
            # 1. Tính điểm cho bài báo trước khi lưu
            calculated_points = self.scoring_service.calculate_score_for_article(
                journal_id=article_data['journal_id'],
                publication_date=article_data['publication_date'],
                publication_type=article_data.get('publication_type') # .get() để an toàn nếu không có
            )

            # 2. Thêm điểm vừa tính vào dữ liệu để lưu
            article_data['user_id'] = user_id
            article_data['work_type'] = 'article'
            article_data['calculated_points'] = calculated_points
            article_data['status'] = 'pending' # Mặc định là chờ xác minh

            # 3. Gọi repository để lưu vào database
            new_work = self.work_repo.create_work(article_data)

            # 4. (Tùy chọn - Nâng cao) Kích hoạt luồng xác minh tự động
            # if new_work:
            #     self.verification_service.start_verification(new_work['id'])

            print(f"Đã thêm thành công bài báo '{article_data['title']}' với {calculated_points} điểm.")
            return new_work

        except Exception as e:
            print(f"Lỗi khi thêm bài báo mới: {e}")
            # Có thể thêm logging ở đây
            return None

    def get_works_by_user(self, user_id):
        """
        Lấy danh sách tất cả các công trình khoa học của một người dùng.
        """
        return self.work_repo.find_works_by_user_id(user_id)

    # Bạn có thể thêm các hàm khác ở đây như:
    # update_work(work_id, data_to_update)
    # delete_work(work_id)
    # ...

