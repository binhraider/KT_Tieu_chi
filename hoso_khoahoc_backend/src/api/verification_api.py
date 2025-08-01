# src/api/verification_api.py

from fastapi import APIRouter, Depends, HTTPException
from ..config.database import get_db
from ..services.verification_service import verify_work_from_url
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/work/{work_id}")
async def verify_scientific_work(work_id: int, db=Depends(get_db)):
    """
    Kích hoạt "bot" để xác minh một công trình khoa học dựa trên ID của nó.
    """
    try:
        with db.cursor(dictionary=True) as cursor:
            # 1. Lấy thông tin công trình (tên) và link tạp chí từ database
            query = """
                SELECT
                    sw.title,
                    j.link as journal_url
                FROM scientific_works sw
                LEFT JOIN journals j ON sw.journal_id = j.id
                WHERE sw.id = %s
            """
            cursor.execute(query, (work_id,))
            work_to_verify = cursor.fetchone()

            if not work_to_verify:
                raise HTTPException(status_code=404, detail="Không tìm thấy công trình khoa học với ID này.")

            work_title = work_to_verify.get("title")
            journal_url = work_to_verify.get("journal_url")

            # 2. Ra lệnh cho "bot" thực hiện xác minh
            verification_result = verify_work_from_url(work_title, journal_url)

            # 3. Cập nhật lại trạng thái của công trình trong database dựa trên kết quả
            new_status = 'pending_verification' # Trạng thái mặc định
            if verification_result["verified"]:
                new_status = 'verified_auto' # Xác minh tự động thành công
            elif verification_result["status"] in ["NO_URL", "REQUEST_ERROR", "NOT_FOUND"]:
                new_status = 'needs_manual_review' # Cần người xem xét thủ công

            update_query = """
                UPDATE scientific_works
                SET status = %s, verification_notes = %s
                WHERE id = %s
            """
            cursor.execute(update_query, (new_status, verification_result.get("message"), work_id))
            db.commit()

            # 4. Trả kết quả về cho frontend
            return verification_result

    except Exception as e:
        logger.error(f"Lỗi khi xác minh công trình {work_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ nội bộ: {e}")