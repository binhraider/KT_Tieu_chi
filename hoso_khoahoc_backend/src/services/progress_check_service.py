# # src/services/progress_check_service.py

# from datetime import date
# from typing import List
# from ..models.user_profile import UserProfileData, ProgressChecklist, CriterionResult
# from ..services.scoring_service import ScoringService
# from ..repositories.criteria_repository import CriteriaRepository

# class ProgressCheckService:
#     def __init__(self, scoring_service: ScoringService, criteria_repo: CriteriaRepository):
#         self.scoring_service = scoring_service
#         self.criteria_repo = criteria_repo

#     def check_pgs_progress(self, profile: UserProfileData, db) -> ProgressChecklist:
#         total_score = 0
#         score_last_3_years = 0
        
#         today = date.today()
#         three_years_ago = today.replace(year=today.year - 3)

#         for work in profile.works:
#             # SỬA ĐỔI: Gọi đúng tên hàm là "calculate_work_score"
#             work_score = self.scoring_service.calculate_work_score(work=work, db=db)
#             total_score += work_score
#             if work.ngay_xuat_ban > three_years_ago:
#                 score_last_3_years += work_score
        
#         # Giữ nguyên logic lấy quy tắc và kiểm tra
#         pgs_criteria_rules = self.criteria_repo.get_pgs_criteria()
#         results: List[CriterionResult] = []

#         # Ví dụ một tiêu chí
#         rule_total_score = 10 
#         results.append(CriterionResult(
#             tieu_chi="Tổng điểm công trình khoa học",
#             yeu_cau=f"≥ {rule_total_score} điểm",
#             thuc_te=f"{total_score:.2f} điểm",
#             dat=(total_score >= rule_total_score)
#         ))
        
#         # Thêm các logic so sánh khác ở đây...

#         return ProgressChecklist(
#             tong_quan={"total_score": total_score, "completed_percent": 0.0},
#             chi_tiet=results
#         )
    




# src/services/progress_check_service.py

from ..models.user_profile import UserProfileData, ProgressChecklist
from ..services.scoring_service import ScoringService
from ..repositories.criteria_repository import CriteriaRepository

class ProgressCheckService:
    def __init__(self, scoring_service: ScoringService, criteria_repo: CriteriaRepository):
        self.scoring_service = scoring_service
        self.criteria_repo = criteria_repo

    def check_pgs_progress(self, profile: UserProfileData, db) -> ProgressChecklist:
        """
        PHIÊN BẢN TẠM THỜI: Bỏ qua việc đọc file và tính điểm để test Bot.
        Hàm này sẽ luôn trả về một kết quả rỗng.
        """
        print("--- Chay che do tam thoi: Bo qua buoc kiem tra tieu chuan ---")
        
        # Luôn trả về một checklist rỗng và không làm gì cả
        return ProgressChecklist(
            tong_quan={"total_score": 0, "message": "Chức năng tính điểm đang được tạm tắt."},
            chi_tiet=[]
        )