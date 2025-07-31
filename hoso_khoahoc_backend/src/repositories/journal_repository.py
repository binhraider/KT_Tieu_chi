# src/repositories/journal_repository.py

class JournalRepository:
    """
    Lớp này chịu trách nhiệm cho tất cả các truy vấn đến database
    liên quan đến bảng `journals` và `journal_points`.
    """
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def find_by_id(self, journal_id: int):
        """
        Tìm thông tin chi tiết của một tạp chí bằng ID.
        """
        cursor = self.db_connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM journals WHERE id = %s", (journal_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Lỗi khi tìm tạp chí bằng ID: {e}")
            return None
        finally:
            cursor.close()

    def find_points_for_journal(self, journal_id, publication_date, publication_type):
        """
        Tìm điểm của một tạp chí tại một thời điểm và loại hình xuất bản cụ thể.
        """
        cursor = self.db_connection.cursor(dictionary=True)
        sql_query = """
            SELECT points
            FROM journal_points
            WHERE
                journal_id = %s
                AND (publication_type = %s OR (%s IS NULL AND publication_type IS NULL))
                AND %s BETWEEN effective_from AND IFNULL(effective_to, '9999-12-31')
            ORDER BY
                CASE WHEN publication_type IS NOT NULL THEN 0 ELSE 1 END
            LIMIT 1;
        """
        try:
            cursor.execute(sql_query, (journal_id, publication_type, publication_type, publication_date))
            result = cursor.fetchone()
            return float(result['points']) if result else None
        except Exception as e:
            print(f"Lỗi khi truy vấn điểm: {e}")
            return None
        finally:
            cursor.close()
