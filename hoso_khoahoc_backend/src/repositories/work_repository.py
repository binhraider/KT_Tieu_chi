# src/repositories/work_repository.py

class WorkRepository:
    """
    Lớp này chịu trách nhiệm cho tất cả các truy vấn đến database
    liên quan đến bảng `scientific_works`.
    """
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def find_by_id(self, work_id: int):
        """
        Tìm một công trình khoa học bằng ID.
        """
        cursor = self.db_connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM scientific_works WHERE id = %s", (work_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Lỗi khi tìm công trình bằng ID: {e}")
            return None
        finally:
            cursor.close()

    def update_status(self, work_id: int, new_status: str, notes: str):
        """
        Cập nhật trạng thái và ghi chú xác minh cho một công trình.
        """
        cursor = self.db_connection.cursor()
        sql_query = "UPDATE scientific_works SET status = %s, verification_notes = %s WHERE id = %s;"
        try:
            cursor.execute(sql_query, (new_status, notes, work_id))
            self.db_connection.commit()
            print(f"Đã cập nhật trạng thái cho công trình ID {work_id} thành '{new_status}'")
            return True
        except Exception as e:
            print(f"Lỗi khi cập nhật trạng thái công trình: {e}")
            self.db_connection.rollback()
            return False
        finally:
            cursor.close()

    def create_work(self, work_data):
        """
        Tạo một bản ghi công trình khoa học mới trong database.
        """
        cursor = self.db_connection.cursor(dictionary=True)
        sql_query = """
            INSERT INTO scientific_works (
                user_id, work_type, title, journal_id, publication_date,
                is_main_author, calculated_points, status
            ) VALUES (
                %(user_id)s, %(work_type)s, %(title)s, %(journal_id)s, %(publication_date)s,
                %(is_main_author)s, %(calculated_points)s, %(status)s
            );
        """
        try:
            cursor.execute(sql_query, work_data)
            self.db_connection.commit()
            work_id = cursor.lastrowid
            return self.find_by_id(work_id)
        except Exception as e:
            print(f"Lỗi khi tạo công trình khoa học mới: {e}")
            self.db_connection.rollback()
            return None
        finally:
            cursor.close()

    def find_works_by_user_id(self, user_id):
        """
        Tìm tất cả các công trình của một người dùng.
        """
        cursor = self.db_connection.cursor(dictionary=True)
        sql_query = "SELECT * FROM scientific_works WHERE user_id = %s ORDER BY publication_date DESC;"
        try:
            cursor.execute(sql_query, (user_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Lỗi khi tìm công trình theo user_id: {e}")
            return []
        finally:
            cursor.close()
