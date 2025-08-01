# src/models/user_profile.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import date

class WorkInput(BaseModel):
    # BỔ SUNG: Thêm trường loai_cong_trinh để khớp với frontend
    loai_cong_trinh: str
    
    ten_cong_trinh: str
    ten_tap_chi: str
    ngay_xuat_ban: date
    is_tac_gia_chinh: bool
    so_dong_tac_gia: int

class UserProfileData(BaseModel):
    # Các trường này phải khớp chính xác với key trong file Javascript
    tieu_chuan_dao_duc_ok: bool
    thoi_gian_cong_tac: int
    so_nam_sau_ts: int
    so_gio_giang_chuan: int
    so_hoc_vien_thac_si_huong_dan: int
    so_ncs_tien_si_huong_dan: int
    so_de_tai_cap_bo: int
    so_de_tai_cap_co_so: int
    works: List[WorkInput]

class CriterionResult(BaseModel):
    tieu_chi: str
    yeu_cau: str
    thuc_te: str
    dat: bool

class ProgressChecklist(BaseModel):
    """
    Model này định nghĩa cấu trúc dữ liệu trả về cho việc kiểm tra tiêu chuẩn.
    """
    tong_quan: Dict[str, Any]
    chi_tiet: List[CriterionResult]

# --- Các model mới cho kết quả của Bot ---
class VerificationDetail(BaseModel):
    verified: bool
    status: str
    message: str
    found_in: Optional[str] = None
    content_found: Optional[str] = None

class VerifiedWorkResult(BaseModel):
    ten_cong_trinh: str
    verification_result: VerificationDetail

class FinalChecklistResponse(ProgressChecklist):
    """
    Model cuối cùng, kế thừa từ ProgressChecklist và thêm kết quả của bot.
    """
    cong_trinh_da_xac_minh: List[VerifiedWorkResult]