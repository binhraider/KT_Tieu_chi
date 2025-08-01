# src/api/journal_api.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from ..repositories.journal_repository import JournalRepository
from ..config.database import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Hàm này chỉ dùng để khởi tạo đối tượng Repository
def get_journal_repository():
    return JournalRepository()

@router.get("/journals", response_model=List[Dict[str, Any]])
async def get_all_journals(
    # FastAPI sẽ "tiêm" các đối tượng cần thiết vào đây
    db = Depends(get_db),
    journal_repo: JournalRepository = Depends(get_journal_repository)
):
    """
    Lấy danh sách tất cả các tạp chí trong CSDL.
    """
    try:
        # Gọi phương thức của repo và truyền kết nối db đã được tiêm vào
        journals = journal_repo.get_all(db=db)
        return journals
    except Exception as e:
        logger.error(f"ERROR fetching journals: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))