# src/services/works_service.py

from typing import List, Dict, Any
from datetime import date
from fastapi import Depends
from .scoring_service import ScoringService

class WorksService:
    def __init__(self, scoring_service: ScoringService = Depends(ScoringService)):
        self.scoring_service = scoring_service

    def get_all_works_with_scores(self) -> List[Dict[str, Any]]:
        # Dữ liệu giả lập để minh họa
        mock_works = [
            {"id": 1, "ten_cong_trinh": "Nghiên cứu về AI", "ten_tap_chi": "Tạp chí Khoa học Máy tính Quốc tế", "nam_xuat_ban": date(2023, 5, 15)},
            {"id": 2, "ten_cong_trinh": "Ứng dụng Blockchain", "ten_tap_chi": "Hội nghị IEEE về An ninh", "nam_xuat_ban": date(2022, 8, 20)}
        ]

        results = []
        for work in mock_works:
            score = self.scoring_service.calculate_work_score(
                journal_name=work["ten_tap_chi"],
                publication_date=work["nam_xuat_ban"]
            )
            work_with_score = {**work, "diem_so": score}
            results.append(work_with_score)
            
        return results