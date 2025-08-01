import mysql.connector
from src.config.database import get_db_connection

class WorkRepository:
    def __init__(self):
        self.connection = get_db_connection()
        self.cursor = self.connection.cursor()

    def add_work(self, work_data: dict):
        query = """
            INSERT INTO cong_trinh_khoa_hoc (ten_cong_trinh, loai_cong_trinh, diem_so) 
            VALUES (%s, %s, %s)
        """
        self.cursor.execute(query, (work_data['name'], work_data['type'], work_data['score']))
        self.connection.commit()
        return self.cursor.lastrowid

    def __del__(self):
        self.connection.close()