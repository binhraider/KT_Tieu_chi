# src/config/database.py

import mysql.connector
from mysql.connector import Error

# --- THAY ĐỔI CÁC THÔNG SỐ KẾT NỐI DATABASE CỦA BẠN TẠI ĐÂY ---
DB_CONFIG = {
    'host': 'localhost',
    'database': 'hoso_khoahoc_db', # Tên database của bạn
    'user': 'root',               # Tên user của bạn
    'password': '1111'            # Mật khẩu của bạn
}

def get_db_connection():
    """
    Hàm này sẽ được sử dụng bởi FastAPI's Dependency Injection.
    Nó tạo một kết nối mới cho mỗi request và đảm bảo nó được đóng lại sau đó.
    """
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        yield connection # Trả về connection cho API sử dụng
    except Error as e:
        print(f"Lỗi khi kết nối đến MySQL: {e}")
        # Có thể thêm logging ở đây
        yield None
    finally:
        if connection and connection.is_connected():
            connection.close()

