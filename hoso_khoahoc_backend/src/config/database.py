# src/config/database.py

import mysql.connector
from mysql.connector import pooling
import os

# Tạo một connection pool để quản lý kết nối hiệu quả
db_pool = pooling.MySQLConnectionPool(
    pool_name="hskh_pool",
    pool_size=5,
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "1111"),
    database=os.getenv("DB_NAME", "hoso_khoahoc_db"),
    port=os.getenv("DB_PORT", 3306)
)

def get_db():
    """
    Hàm dependency cung cấp một kết nối database cho mỗi request.
    """
    connection = None
    try:
        connection = db_pool.get_connection()
        yield connection
    finally:
        if connection and connection.is_connected():
            connection.close()