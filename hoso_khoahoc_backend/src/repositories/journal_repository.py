# src/repositories/journal_repository.py

from typing import List, Dict, Any, Optional
from datetime import date
from mysql.connector.connection import MySQLConnection

class JournalRepository:
    """
    Lớp này chỉ chứa logic truy vấn CSDL.
    Nó không tự khởi tạo kết nối mà sẽ nhận kết nối từ API layer.
    """
    def get_all(self, db: MySQLConnection) -> List[Dict[str, Any]]:
        """Lấy tất cả các tạp chí."""
        query = "SELECT id, name, publisher AS co_quan_xuat_ban, link FROM journals"
        with db.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def get_score_by_journal_name(self, db: MySQLConnection, journal_name: str, publication_date: date) -> float:
        """Lấy điểm của một tạp chí dựa trên tên và ngày xuất bản."""
        query = """
            SELECT jp.points
            FROM journals j
            JOIN journal_points jp ON j.id = jp.journal_id
            WHERE j.name = %s
              AND jp.effective_from <= %s
              AND (jp.effective_to IS NULL OR jp.effective_to >= %s)
            ORDER BY jp.effective_from DESC
            LIMIT 1
        """
        with db.cursor(dictionary=True) as cursor:
            cursor.execute(query, (journal_name, publication_date, publication_date))
            result = cursor.fetchone()
            return float(result['points']) if result else 0.0

    def get_journal_link_by_name(self, db: MySQLConnection, journal_name: str) -> Optional[str]:
        """Lấy đường link của một tạp chí dựa vào tên của nó."""
        if not journal_name:
            return None
            
        query = "SELECT link FROM journals WHERE name = %s LIMIT 1"
        with db.cursor(dictionary=True) as cursor:
            cursor.execute(query, (journal_name,))
            result = cursor.fetchone()
            return result['link'] if result and result['link'] else None