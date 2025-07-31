# main.py (Đặt ở thư mục gốc của dự án)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import các router từ thư mục api
from src.api import works_api 
# from src.api import profile_api # Sẽ thêm sau

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Hồ Sơ Khoa Học API",
    description="API cho hệ thống quản lý và chấm điểm hồ sơ khoa học.",
    version="1.0.0"
)

# --- Cấu hình CORS ---
# Cho phép frontend (ví dụ chạy ở port 3000) có thể gọi đến API này
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173", # Port phổ biến cho Vite/React
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Cho phép tất cả các phương thức (GET, POST, etc.)
    allow_headers=["*"], # Cho phép tất cả các header
)


# --- Include các API Routers ---
# Thêm các API đã định nghĩa trong works_api.py vào ứng dụng chính
app.include_router(works_api.router)
# app.include_router(profile_api.router) # Sẽ thêm sau


# --- Endpoint gốc để kiểm tra server có hoạt động không ---
@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint gốc để kiểm tra tình trạng của API.
    """
    return {"message": "Chào mừng đến với API Hồ Sơ Khoa Học!"}

