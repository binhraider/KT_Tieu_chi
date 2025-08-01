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
        # --- LƯU CÁC CÔNG TRÌNH VÀO DATABASE ---
        user_id_for_works = 1 
        with db.cursor() as cursor:
            for work in profile_data.works:
                journal_id = None
                if work.loai_cong_trinh == 'TAP_CHI' and work.ten_tap_chi:
                    cursor.execute("SELECT id FROM journals WHERE name = %s LIMIT 1", (work.ten_tap_chi,))
                    journal_record = cursor.fetchone()
                    if journal_record:
                        journal_id = journal_record[0]

                # SỬA ĐỔI: Sử dụng getattr() để truy cập an toàn
                # Nó sẽ lấy giá trị của work.duong_dan_minh_chung nếu có,
                # nếu không sẽ trả về None, tránh gây ra lỗi.
                evidence_url = getattr(work, 'duong_dan_minh_chung', None)

                sql = """
                    INSERT INTO scientific_works 
                    (user_id, work_type, title, journal_id, publication_date, is_main_author, authors, evidence_url, status) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                val = (
                    user_id_for_works,
                    work.loai_cong_trinh,
                    work.ten_cong_trinh,
                    journal_id,
                    work.ngay_xuat_ban,
                    work.is_tac_gia_chinh,
                    str(work.so_dong_tac_gia),
                    evidence_url, # <-- Sử dụng biến đã được gán an toàn
                    'pending_verification'
                )
                cursor.execute(sql, val)
            db.commit()

        # --- CÁC BƯỚC XÁC MINH VÀ TÍNH ĐIỂM (Giữ nguyên) ---
        verified_works_details = []
        for work in profile_data.works:
            verification_result = {}
            if work.loai_cong_trinh == 'TAP_CHI':
                journal_url = journal_repo.get_journal_link_by_name(db=db, journal_name=work.ten_tap_chi)
                verification_result = verify_work_from_url(work_title=work.ten_cong_trinh, journal_url=journal_url)
            else:
                verification_result = { "verified": False, "status": "PENDING_ADMIN_REVIEW", "message": "Cần Admin xem xét và phê duyệt thủ công." }
            
            verified_works_details.append({ "ten_cong_trinh": work.ten_cong_trinh, "verification_result": verification_result })

        checklist = progress_service.check_pgs_progress(profile_data, db)

        final_result = {
            "tong_quan": checklist.tong_quan,
            "chi_tiet": checklist.chi_tiet,
            "cong_trinh_da_xac_minh": verified_works_details
        }
        return final_result

    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra hồ sơ PGS: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra trong quá trình xử lý.")