# src/api/works_api.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import datetime

# Giả sử bạn có một cơ chế để lấy kết nối DB và user_id
# Đây là phần phụ thuộc (dependency) để inject vào các API
from config.database import get_db_connection 
# from services.auth_service import get_current_user_id

from services.works_service import WorksService

# Tạo một router riêng cho các API liên quan đến công trình khoa học
router = APIRouter(
    prefix="/api/works",
    tags=["Works"] # Gom nhóm các API này trong tài liệu Swagger
)

# --- Pydantic Models: Định nghĩa cấu trúc dữ liệu cho request và response ---

class ArticleCreateModel(BaseModel):
    """Mô hình dữ liệu khi người dùng thêm một bài báo mới."""
    title: str = Field(..., min_length=1, description="Tên của bài báo khoa học")
    journal_id: int = Field(..., gt=0, description="ID của tạp chí từ bảng `journals`")
    publication_date: datetime.date = Field(..., description="Ngày xuất bản")
    is_main_author: bool = Field(False, description="Đánh dấu nếu là tác giả chính")
    publication_type: Optional[str] = Field(None, description="Loại hình xuất bản (ví dụ: Online)")

class WorkResponseModel(BaseModel):
    """Mô hình dữ liệu trả về cho một công trình khoa học."""
    id: int
    user_id: int
    work_type: str
    title: str
    journal_id: Optional[int]
    publication_date: datetime.date
    is_main_author: bool
    calculated_points: float
    status: str
    
    class Config:
        from_attributes = True # Cho phép Pydantic đọc dữ liệu từ đối tượng Python

# --- API Endpoints ---

@router.post("/", response_model=WorkResponseModel, status_code=status.HTTP_201_CREATED)
def add_new_article(
    article_data: ArticleCreateModel,
    db_connection = Depends(get_db_connection),
    # user_id: int = Depends(get_current_user_id) # Sẽ tích hợp sau khi có hệ thống auth
):
    """
    API endpoint để thêm một bài báo khoa học mới.
    """
    # Tạm thời gán user_id = 1 để test
    user_id = 1 
    
    works_service = WorksService(db_connection)
    
    # Chuyển đổi Pydantic model thành dict để service có thể xử lý
    new_article = works_service.add_new_article(user_id, article_data.model_dump())
    
    if not new_article:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể thêm bài báo. Vui lòng kiểm tra lại dữ liệu đầu vào."
        )
        
    return new_article

@router.get("/", response_model=List[WorkResponseModel])
def get_all_works_for_user(
    db_connection = Depends(get_db_connection),
    # user_id: int = Depends(get_current_user_id) # Sẽ tích hợp sau khi có hệ thống auth
):
    """
    API endpoint để lấy danh sách tất cả các công trình khoa học của người dùng.
    """
    # Tạm thời gán user_id = 1 để test
    user_id = 1
    
    works_service = WorksService(db_connection)
    works = works_service.get_works_by_user(user_id)
    
    return works

