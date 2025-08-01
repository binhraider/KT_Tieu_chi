# src/services/scoring_service.py

from ..repositories.journal_repository import JournalRepository
from ..models.user_profile import WorkInput
from fastapi import Depends

class ScoringService:
    def __init__(self, journal_repo: JournalRepository = Depends(JournalRepository)):
        self.journal_repo = journal_repo

    def calculate_work_score(self, work: WorkInput, db) -> float:
        """
        PHIÊN BẢN HOÀN CHỈNH: Tính điểm dựa trên loại công trình khoa học.
        - Bài báo tạp chí: Tra cứu CSDL.
        - Các loại khác: Tính điểm cố định theo quy tắc.
        """
        loai = work.loai_cong_trinh
        
        # 1. Bài báo Tạp chí
        if loai == 'TAP_CHI':
            if not work.ten_tap_chi or not work.ngay_xuat_ban:
                return 0.0
            return self.journal_repo.get_score_by_journal_name(
                db=db,
                journal_name=work.ten_tap_chi,
                publication_date=work.ngay_xuat_ban
            )
            
        # 2. Sách phục vụ đào tạo (dựa trên ảnh bạn cung cấp)
        elif loai == 'SACH_CHUYEN_KHAO':
            return 3.0
        elif loai == 'SACH_GIAO_TRINH':
            return 2.0
        elif loai == 'SACH_THAM_KHAO':
            return 1.5
        elif loai == 'SACH_HUONG_DAN':
            return 1.0
        elif loai == 'CHUONG_SACH':
            return 1.0
            
        # 3. Kết quả ứng dụng KH&CN
        elif loai == 'SANG_CHE':
            return 3.0
        elif loai == 'GIAI_PHAP_HUU_ICH':
            return 2.0

        # 4. Tác phẩm nghệ thuật / TDTT
        elif loai == 'GIAI_THUONG_QUOC_GIA':
            return 1.0
        elif loai == 'GIAI_THUONG_QUOC_TE':
            return 1.5

        # 5. Bài báo thay thế đề tài (cho ngành đặc thù)
        elif loai == 'BAI_BAO_THAY_THE':
            return 1.5
            
        # Mặc định, các loại khác không có điểm
        else:
            return 0.0