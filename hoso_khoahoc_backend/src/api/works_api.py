# src/api/works_api.py

from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from src.services.works_service import WorksService

router = APIRouter()

@router.get("/works", response_model=List[Dict[str, Any]])
def get_all_works(works_service: WorksService = Depends(WorksService)):
    """
    Lấy danh sách các công trình khoa học cùng với điểm số được tính.
    """
    return works_service.get_all_works_with_scores()