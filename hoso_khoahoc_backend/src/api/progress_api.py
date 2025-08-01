# src/api/progress_api.py

from fastapi import APIRouter, Depends, HTTPException
from ..models.user_profile import UserProfileData, FinalChecklistResponse
from ..services.progress_check_service import ProgressCheckService
from ..services.scoring_service import ScoringService
from ..repositories.criteria_repository import CriteriaRepository
from ..repositories.journal_repository import JournalRepository
from ..services.verification_service import verify_work_from_url
from ..config.database import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Dependency Providers (Giữ nguyên) ---
def get_journal_repository():
    return JournalRepository()

def get_progress_check_service():
    journal_repo = JournalRepository()
    scoring_service = ScoringService(journal_repo=journal_repo)
    criteria_repo = CriteriaRepository()
    return ProgressCheckService(scoring_service, criteria_repo)

@router.post("/check-progress/pgs", response_model=FinalChecklistResponse)
async def check_pgs_progress_endpoint(
    profile_data: UserProfileData,
    db = Depends(get_db),
    progress_service: ProgressCheckService = Depends(get_progress_check_service),
    journal_repo: JournalRepository = Depends(get_journal_repository)
):
    try:
        # --- BƯỚC 1: XÁC MINH CÔNG TRÌNH (LOGIC ĐÃ CẬP NHẬT) ---
        verified_works_details = []
        for work in profile_data.works:
            verification_result = {}
            
            # CHỈ KÍCH HOẠT BOT NẾU LÀ "BÀI BÁO TẠP CHÍ"
            if work.loai_cong_trinh == 'TAP_CHI':
                journal_url = journal_repo.get_journal_link_by_name(db=db, journal_name=work.ten_tap_chi)
                verification_result = verify_work_from_url(
                    work_title=work.ten_cong_trinh, 
                    journal_url=journal_url
                )
            # CÁC LOẠI CÔNG TRÌNH KHÁC -> MẶC ĐỊNH CHỜ ADMIN DUYỆT
            else:
                verification_result = {
                    "verified": False, # Trạng thái "chưa xác minh"
                    "status": "PENDING_ADMIN_REVIEW",
                    "message": "Cần Admin xem xét và phê duyệt thủ công."
                }

            verified_works_details.append({
                "ten_cong_trinh": work.ten_cong_trinh,
                "verification_result": verification_result
            })

        # --- BƯỚC 2: TÍNH ĐIỂM VÀ KIỂM TRA TIÊU CHUẨN (Không đổi) ---
        # Lưu ý: Hiện tại, hệ thống vẫn tính điểm cho tất cả.
        # Bạn có thể thêm logic để chỉ tính điểm cho các công trình đã được admin phê duyệt sau này.
        checklist = progress_service.check_pgs_progress(profile_data, db)

        # --- BƯỚC 3: GỘP KẾT QUẢ VÀ TRẢ VỀ ---
        final_result = {
            "tong_quan": checklist.tong_quan,
            "chi_tiet": checklist.chi_tiet,
            "cong_trinh_da_xac_minh": verified_works_details
        }
        return final_result

    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra hồ sơ PGS: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra trong quá trình xử lý.")