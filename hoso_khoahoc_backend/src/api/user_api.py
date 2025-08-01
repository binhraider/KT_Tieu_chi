# src/api/user_api.py

import os
import shutil
import uuid
import logging # Thêm thư viện logging để ghi lỗi
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from ..config.database import get_db

# Cấu hình logging để in ra lỗi chi tiết trên console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your_secret_key"  # Đổi thành chuỗi bí mật thực tế
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str = ""

class UserLogin(BaseModel):
    email: str
    password: str

# Đăng ký
@router.post("/register")
def register(user: UserRegister, db=Depends(get_db)):
    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT id FROM users WHERE email=%s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email đã tồn tại")
        hashed = pwd_context.hash(user.password)
        cursor.execute(
            "INSERT INTO users (email, password_hash, full_name) VALUES (%s, %s, %s)",
            (user.email, hashed, user.full_name)
        )
        db.commit()
    return {"msg": "Đăng ký thành công"}

# Đăng nhập
@router.post("/login")
def login(user: UserLogin, db=Depends(get_db)):
    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM users WHERE email=%s", (user.email,))
        db_user = cursor.fetchone()
        if not db_user or not pwd_context.verify(user.password, db_user["password_hash"]):
            raise HTTPException(status_code=401, detail="Sai email hoặc mật khẩu")
        token_data = {
            "user_id": db_user["id"],
            "email": db_user["email"],
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token}

UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


@router.post("/upload-document")
async def upload_document(
    user_id: int = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    """
    Endpoint để tải file minh chứng lên cho một người dùng.
    """
    try:
        # 1. Tạo tên file duy nhất và đường dẫn lưu file
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)

        # 2. Lưu file vào thư mục
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. GHI DỮ LIỆU VÀO DATABASE (PHẦN ĐÃ ĐƯỢC CẢI TIẾN)
        # Sử dụng 'with' để đảm bảo cursor được đóng tự động và an toàn
        with db.cursor() as cursor:
            query = """
                INSERT INTO user_documents
                (user_id, document_type, file_path, original_filename)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, document_type, file_path, file.filename))
            db.commit() # Xác nhận thay đổi
            document_id = cursor.lastrowid

        return {
            "message": "Tải file thành công!",
            "document_id": document_id,
            "file_path": file_path
        }

    except Exception as e:
        # CẢI TIẾN: In ra lỗi cụ thể trên console của server để dễ dàng chẩn đoán
        logger.error(f"An error occurred during file upload: {e}", exc_info=True)
        # Trả về lỗi 500 cho client
        raise HTTPException(status_code=500, detail=f"Server không thể xử lý file. Lỗi: {e}")
    finally:
        # Luôn luôn đóng file sau khi xử lý xong
        if file:
            file.file.close()