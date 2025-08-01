# src/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Dùng import tương đối từ trong cùng package 'src'
from src.api import works_api , progress_api, journal_api
from src.api import user_api
from src.api import verification_api


app = FastAPI(
    title="Hồ Sơ Khoa Học API",
    description="API cho hệ thống quản lý và chấm điểm hồ sơ khoa học.",
    version="1.0.0"
)

# Cấu hình CORS
# ... (giữ nguyên phần CORS của bạn) ...
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cho phép tất cả để test
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(works_api.router, prefix="/api", tags=["Công trình Khoa học"])
app.include_router(journal_api.router, prefix="/api", tags=["Tạp chí"])
app.include_router(progress_api.router, prefix="/api", tags=["Kiểm tra Tiến trình"])
app.include_router(user_api.router, prefix="/api/users", tags=["Users"])

app.include_router(verification_api.router, prefix="/api/verify", tags=["Verification Bot"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Chào mừng đến với API Hồ Sơ Khoa Học!"}




# uvicorn src.main:app --reload --host 0.0.0.0