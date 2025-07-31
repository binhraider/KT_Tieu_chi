import pandas as pd
import mysql.connector
from mysql.connector import Error
import re
import logging
from datetime import datetime

# Cấu hình logging chi tiết
logging.basicConfig(
    filename=f'import_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s', 
    filemode='w'
)

# Console handler để hiển thị log trên màn hình
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

# --- THAY ĐỔI CÁC THÔNG SỐ KẾT NỐI DATABASE CỦA BẠN TẠI ĐÂY ---
DB_CONFIG = {
    'host': 'localhost',
    'database': 'hoso_khoahoc_db',
    'user': 'root',
    'password': '1111',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def create_db_connection():
    """Tạo kết nối đến database với error handling tốt hơn."""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("✅ Kết nối đến MySQL thành công!")
        logging.info("Kết nối database thành công")
    except Error as e:
        error_msg = f"Lỗi khi kết nối đến MySQL: {e}"
        print(f"❌ {error_msg}")
        logging.error(error_msg)
    return connection

def create_tables(connection):
    """Tạo bảng journals và journal_points với cấu trúc tối ưu."""
    cursor = connection.cursor()
    
    try:
        # Bảng journals với đầy đủ cột và tối ưu hóa
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journals (
                id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                name TEXT NOT NULL,
                issn VARCHAR(255) NULL,
                eissn VARCHAR(255) NULL,
                publisher TEXT NULL,
                type VARCHAR(255) NULL,
                link VARCHAR(2048) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_issn (issn),
                INDEX idx_eissn (eissn)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        
        # Bảng journal_points với cấu trúc tối ưu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journal_points (
                id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                journal_id INT UNSIGNED NOT NULL,
                field_of_study VARCHAR(255) NULL,
                points DECIMAL(5, 2) NOT NULL,
                publication_type VARCHAR(50) NULL,
                effective_from DATE NOT NULL,
                effective_to DATE NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (journal_id) REFERENCES journals(id) ON DELETE CASCADE,
                INDEX idx_journal_id (journal_id),
                INDEX idx_dates (effective_from, effective_to),
                INDEX idx_field (field_of_study)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        
        connection.commit()
        print("✅ Đã kiểm tra/tạo bảng journals và journal_points với indexes tối ưu.")
        logging.info("Tạo bảng thành công")
        
    except Error as e:
        error_msg = f"Lỗi khi tạo bảng: {e}"
        print(f"❌ {error_msg}")
        logging.error(error_msg)
        raise
    finally:
        cursor.close()

def normalize_issn(issn_string):
    """
    Chuẩn hóa ISSN/eISSN với logic kết hợp từ cả 2 phiên bản.
    Xử lý các trường hợp phức tạp và đơn giản.
    """
    if not issn_string or pd.isna(issn_string) or str(issn_string).lower() in ['none', 'n/a', '']:
        return None, None
    
    issn, eissn = None, None
    issn_string = str(issn_string).strip()
    
    # Xử lý trường hợp có p- và e- (từ phiên bản 1)
    p_match = re.search(r'p-([\d\w-]+)', issn_string, re.IGNORECASE)
    e_match = re.search(r'e-([\d\w-]+)', issn_string, re.IGNORECASE)
    
    if p_match:
        issn = p_match.group(1).strip()
    if e_match:
        eissn = e_match.group(1).strip()
    
    # Nếu không tìm thấy p- hoặc e-, sử dụng logic từ phiên bản 2
    if not issn and not eissn:
        if ',' in issn_string:
            parts = issn_string.split(',')
            for part in parts:
                part = part.strip()
                if part.startswith('p-'):
                    issn = part.replace('p-', '').strip()
                elif part.startswith('e-'):
                    eissn = part.replace('e-', '').strip()
                elif not issn:  # Gán part đầu tiên làm issn nếu chưa có
                    issn = re.sub(r'[^0-9-]', '', part)
        else:
            # Trường hợp đơn giản - lấy chuỗi số-gạch ngang đầu tiên
            main_match = re.search(r'([\d-]+)', issn_string)
            if main_match:
                issn = main_match.group(1).strip()
    
    # Validate ISSN format (basic check)
    def validate_issn(issn_val):
        if issn_val and re.match(r'^\d{4}-\d{3}[\dxX]$', issn_val):
            return issn_val
        elif issn_val and re.match(r'^\d{4}-\d{4}$', issn_val):
            return issn_val
        return issn_val  # Trả về như cũ nếu không match format chuẩn
    
    return validate_issn(issn), validate_issn(eissn)

def parse_point_rules(point_string):
    """
    Phân tích chuỗi điểm quy đổi với logic kết hợp và cải tiến.
    Xử lý các trường hợp phức tạp và edge cases.
    """
    if not point_string or pd.isna(point_string) or str(point_string).strip() == '':
        logging.warning(f"Chuỗi điểm rỗng hoặc không hợp lệ: {point_string}")
        return [{'points': 0.0, 'from': '1900-01-01', 'to': None, 'publication_type': None}]

    point_string = str(point_string).strip()
    
    # Tách các quy tắc bằng dấu chấm phẩy
    rule_parts = [part.strip() for part in point_string.split(';') if part.strip()]
    if not rule_parts:
        logging.warning(f"Không tìm thấy quy tắc điểm trong: {point_string}")
        return [{'points': 0.0, 'from': '1900-01-01', 'to': None, 'publication_type': None}]

    parsed_rules = []
    
    for part in rule_parts:
        # Tìm năm bắt đầu
        year_match = re.search(r'từ (\d{4})', part)
        from_year = int(year_match.group(1)) if year_match else None

        # Loại bỏ phần 'từ <năm>' để xử lý phần còn lại
        search_str = re.sub(r'từ \d{4}', '', part).strip()

        # Tìm publication_type
        publication_type = None
        if 'online' in search_str.lower():
            if 'không online' in search_str.lower():
                publication_type = 'Không online'
                search_str = re.sub(r'không online', '', search_str, flags=re.IGNORECASE).strip()
            else:
                publication_type = 'Online'
                search_str = re.sub(r'online', '', search_str, flags=re.IGNORECASE).strip()

        # Tìm giá trị điểm (hỗ trợ cả dấu phẩy và dấu chấm)
        point_matches = re.findall(r'(\d+[,.]\d+|\d+)', search_str)
        
        if point_matches:
            # Lấy số cuối cùng (thường là điểm)
            point_str = point_matches[-1].replace(',', '.')
            try:
                points = float(point_str)
                # Kiểm tra giá trị hợp lệ  
                if points > 100:
                    logging.warning(f"Giá trị điểm có thể không hợp lệ (>100): {points} trong '{part}'")
                    # Có thể là lỗi nhập liệu, thử chia cho 1000 hoặc đặt về 0
                    if points > 1000:
                        points = 0.0
                        logging.warning(f"Đặt điểm về 0 do giá trị quá lớn: {point_str}")
            except ValueError:
                logging.warning(f"Không thể chuyển đổi điểm: {point_str} trong '{part}'")
                points = 0.0
        else:
            logging.warning(f"Không tìm thấy giá trị điểm trong: '{part}'")
            points = 0.0

        parsed_rules.append({
            'points': points,
            'year': from_year,
            'publication_type': publication_type
        })

    # Sắp xếp theo năm và tính toán effective dates
    parsed_rules.sort(key=lambda x: x['year'] if x['year'] is not None else 0)

    final_rules = []
    for i, current_rule in enumerate(parsed_rules):
        from_date = f"{current_rule['year']}-01-01" if current_rule['year'] else '1900-01-01'
        to_date = None
        
        # Tìm rule tiếp theo có năm để tính effective_to
        for j in range(i + 1, len(parsed_rules)):
            if parsed_rules[j]['year'] is not None:
                to_date = f"{parsed_rules[j]['year'] - 1}-12-31"
                break

        final_rules.append({
            'points': current_rule['points'],
            'from': from_date,
            'to': to_date,
            'publication_type': current_rule['publication_type']
        })
        
    return final_rules if final_rules else [{'points': 0.0, 'from': '1900-01-01', 'to': None, 'publication_type': None}]

def import_data_from_excel(connection, excel_path, sheet_name, clean_data=False):
    """
    Nhập dữ liệu từ Excel với batch processing và error handling tối ưu.
    
    Args:
        connection: MySQL connection object
        excel_path: Đường dẫn file Excel
        sheet_name: Tên sheet
        clean_data: Có xóa dữ liệu cũ không (default: False)
    """
    try:
        print(f"📖 Đang đọc file Excel: {excel_path}")
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        df = df.where(pd.notna(df), None)
        print(f"✅ Đọc thành công {len(df)} dòng dữ liệu")
        logging.info(f"Đọc file Excel thành công: {len(df)} dòng")
        
    except FileNotFoundError:
        error_msg = f"Không tìm thấy file '{excel_path}'"
        print(f"❌ {error_msg}")
        logging.error(error_msg)
        return
    except Exception as e:
        error_msg = f"Lỗi khi đọc file Excel: {e}"
        print(f"❌ {error_msg}")
        logging.error(error_msg)
        return
    
    cursor = connection.cursor(buffered=True)
    
    # Xóa dữ liệu cũ nếu được yêu cầu
    if clean_data:
        print("🧹 Đang xóa dữ liệu cũ...")
        cursor.execute("DELETE FROM journal_points")
        cursor.execute("DELETE FROM journals") 
        connection.commit()
        print("✅ Đã xóa dữ liệu cũ")
        logging.info("Đã xóa dữ liệu cũ")
    
    # BƯỚC 1: Nhập dữ liệu journals
    print("\n📝 Bước 1: Bắt đầu nhập dữ liệu vào bảng `journals`...")
    
    unique_journals_df = df.dropna(subset=['Chỉ số ISSN/eISSN']).drop_duplicates(subset=['Chỉ số ISSN/eISSN'])
    journal_values = []
    journal_errors = []
    
    for index, row in unique_journals_df.iterrows():
        try:
            issn, eissn = normalize_issn(row['Chỉ số ISSN/eISSN'])
            if not issn and not eissn:
                journal_errors.append(f"Hàng {index}: Không có ISSN/eISSN hợp lệ - {row.get('Tên tạp chí/hội nghị', 'N/A')}")
                continue
            
            # Kiểm tra tồn tại (cải tiến query)
            cursor.execute("""
                SELECT id FROM journals 
                WHERE (issn = %s AND %s IS NOT NULL) 
                   OR (eissn = %s AND %s IS NOT NULL)
                LIMIT 1
            """, (issn, issn, eissn, eissn))
            
            if cursor.fetchone() is None:
                journal_values.append((
                    row.get('Tên tạp chí/hội nghị'),
                    issn,
                    eissn, 
                    row.get('Cơ quan xuất bản'),
                    row.get('Loại'),
                    row.get('Link tạp chí/hội nghị')
                ))
                
        except Exception as e:
            error_msg = f"Hàng {index} (journals): {e}"
            journal_errors.append(error_msg)
            logging.error(error_msg)
    
    # Batch insert cho journals
    journal_success_count = 0
    if journal_values:
        try:
            cursor.executemany("""
                INSERT INTO journals (name, issn, eissn, publisher, type, link) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, journal_values)
            journal_success_count = len(journal_values)
            connection.commit()
            print(f"✅ Đã nhập {journal_success_count} journals thành công")
            logging.info(f"Nhập {journal_success_count} journals thành công")
            
        except Exception as e:
            error_msg = f"Lỗi batch insert journals: {e}"
            print(f"❌ {error_msg}")
            logging.error(error_msg)
            connection.rollback()
    
    if journal_errors:
        print(f"⚠️  Có {len(journal_errors)} lỗi khi xử lý journals")
        for error in journal_errors[:5]:  # Chỉ hiển thị 5 lỗi đầu
            print(f"   • {error}")
        if len(journal_errors) > 5:
            print(f"   • ... và {len(journal_errors) - 5} lỗi khác (xem log file)")
    
    # BƯỚC 2: Nhập dữ liệu journal_points  
    print("\n📊 Bước 2: Bắt đầu nhập dữ liệu vào bảng `journal_points`...")
    
    point_values = []
    point_errors = []
    
    for index, row in df.iterrows():
        try:
            issn, eissn = normalize_issn(row['Chỉ số ISSN/eISSN'])
            if not issn and not eissn:
                continue
            
            # Tìm journal_id
            cursor.execute("""
                SELECT id FROM journals 
                WHERE (issn = %s AND %s IS NOT NULL) 
                   OR (eissn = %s AND %s IS NOT NULL)
                LIMIT 1
            """, (issn, issn, eissn, eissn))
            
            result = cursor.fetchone()
            if result:
                journal_id = result[0]
                point_rules = parse_point_rules(row['Quy đổi điểm'])
                
                for rule in point_rules:
                    if rule['points'] is None or rule['points'] < 0:
                        point_errors.append(f"Hàng {index}: Giá trị điểm không hợp lệ ({rule['points']})")
                        continue
                        
                    point_values.append((
                        journal_id,
                        row.get('Ngành/Liên ngành'),
                        rule['points'],
                        rule['publication_type'],
                        rule['from'],
                        rule['to']
                    ))
            else:
                point_errors.append(f"Hàng {index}: Không tìm thấy journal cho ISSN/eISSN {issn}/{eissn}")
                
        except Exception as e:
            error_msg = f"Hàng {index} (journal_points): {e}"
            point_errors.append(error_msg)
            logging.error(error_msg)
    
    # Batch insert cho journal_points
    point_success_count = 0
    if point_values:
        try:
            cursor.executemany("""
                INSERT INTO journal_points (journal_id, field_of_study, points, publication_type, effective_from, effective_to) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, point_values)
            point_success_count = len(point_values)
            connection.commit()
            print(f"✅ Đã nhập {point_success_count} journal_points thành công")
            logging.info(f"Nhập {point_success_count} journal_points thành công")
            
        except Exception as e:
            error_msg = f"Lỗi batch insert journal_points: {e}"
            print(f"❌ {error_msg}")
            logging.error(error_msg)
            connection.rollback()
    
    if point_errors:
        print(f"⚠️  Có {len(point_errors)} lỗi khi xử lý journal_points")
        for error in point_errors[:5]:
            print(f"   • {error}")
        if len(point_errors) > 5:
            print(f"   • ... và {len(point_errors) - 5} lỗi khác (xem log file)")
    
    cursor.close()
    
    # Thống kê kết quả
    print(f"\n📈 Tổng kết:")
    print(f"   • Journals: {journal_success_count} thành công, {len(journal_errors)} lỗi")
    print(f"   • Journal Points: {point_success_count} thành công, {len(point_errors)} lỗi")
    
    return {
        'journals_success': journal_success_count,
        'journals_errors': len(journal_errors),
        'points_success': point_success_count, 
        'points_errors': len(point_errors)
    }

def verify_data(connection):
    """Kiểm tra và thống kê dữ liệu trong database."""
    cursor = connection.cursor()
    
    print("\n🔍 Kiểm tra dữ liệu trong database:")
    
    # Đếm journals
    cursor.execute("SELECT COUNT(*) FROM journals")
    journal_count = cursor.fetchone()[0]
    print(f"   • Số journals: {journal_count}")
    
    # Đếm journal_points
    cursor.execute("SELECT COUNT(*) FROM journal_points") 
    point_count = cursor.fetchone()[0]
    print(f"   • Số journal_points: {point_count}")
    
    # Thống kê theo publication_type
    cursor.execute("""
        SELECT publication_type, COUNT(*) 
        FROM journal_points 
        GROUP BY publication_type
    """)
    pub_types = cursor.fetchall()
    print(f"   • Phân loại publication_type:")
    for pub_type, count in pub_types:
        print(f"     - {pub_type or 'NULL'}: {count}")
    
    # Thống kê theo khoảng điểm
    cursor.execute("""
        SELECT 
            CASE 
                WHEN points = 0 THEN '0 điểm'
                WHEN points > 0 AND points <= 1 THEN '0-1 điểm'
                WHEN points > 1 AND points <= 5 THEN '1-5 điểm'
                ELSE '>5 điểm'
            END as point_range,
            COUNT(*)
        FROM journal_points 
        GROUP BY point_range
        ORDER BY MIN(points)
    """)
    point_ranges = cursor.fetchall()
    print(f"   • Phân bố điểm:")
    for range_name, count in point_ranges:
        print(f"     - {range_name}: {count}")
    
    cursor.close()

def backup_data(connection, backup_file=None):
    """Tạo backup dữ liệu ra file CSV."""
    if not backup_file:
        backup_file = f"journal_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT 
                j.name, j.issn, j.eissn, j.publisher, j.type, j.link,
                jp.field_of_study, jp.points, jp.publication_type,
                jp.effective_from, jp.effective_to
            FROM journals j
            LEFT JOIN journal_points jp ON j.id = jp.journal_id
            ORDER BY j.name, jp.effective_from
        """)
        
        columns = ['name', 'issn', 'eissn', 'publisher', 'type', 'link', 
                  'field_of_study', 'points', 'publication_type', 
                  'effective_from', 'effective_to']
        
        df = pd.DataFrame(cursor.fetchall(), columns=columns)
        df.to_csv(backup_file, index=False, encoding='utf-8-sig')
        
        print(f"✅ Đã tạo backup: {backup_file}")
        logging.info(f"Tạo backup thành công: {backup_file}")
        cursor.close()
        
    except Exception as e:
        error_msg = f"Lỗi khi tạo backup: {e}"
        print(f"❌ {error_msg}")
        logging.error(error_msg)

if __name__ == '__main__':
    print("🚀 Bắt đầu quá trình nhập dữ liệu tạp chí khoa học")
    print("=" * 60)
    
    # Kết nối database
    conn = create_db_connection()
    if not conn or not conn.is_connected():
        print("❌ Không thể kết nối database. Thoát chương trình.")
        exit(1)
    
    try:
        # Tạo bảng
        create_tables(conn)
        
        # Cấu hình file đầu vào
        EXCEL_FILE_PATH = 'C:/Users/Admin/Downloads/hoso_khoahoc_backend/scripts/data.xlsx'
        JOURNAL_SHEET_NAME = 'DS tạp chí'
        
        # Hỏi người dùng có muốn xóa dữ liệu cũ không
        clean_choice = input("\n🤔 Bạn có muốn xóa dữ liệu cũ trước khi nhập không? (y/N): ").lower()
        clean_data = clean_choice in ['y', 'yes']
        
        if clean_data:
            print("⚠️  Sẽ xóa tất cả dữ liệu cũ!")
        else:
            print("ℹ️  Sẽ giữ lại dữ liệu cũ và chỉ thêm mới.")
        
        # Nhập dữ liệu
        result = import_data_from_excel(conn, EXCEL_FILE_PATH, JOURNAL_SHEET_NAME, clean_data)
        
        if result:
            # Kiểm tra dữ liệu
            verify_data(conn)
            
            # Tạo backup
            backup_choice = input("\n💾 Bạn có muốn tạo backup dữ liệu không? (Y/n): ").lower()
            if backup_choice not in ['n', 'no']:
                backup_data(conn)
        
        print("\n🎉 Hoàn tất quá trình nhập dữ liệu!")
        print("📋 Chi tiết xem trong file log được tạo.")
        
    except KeyboardInterrupt:
        print("\n⏹️  Người dùng hủy bỏ quá trình.")
        logging.warning("Người dùng hủy bỏ quá trình")
        
    except Exception as e:
        error_msg = f"Lỗi không mong muốn: {e}"
        print(f"\n💥 {error_msg}")
        logging.error(error_msg)
        
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("🔌 Đã đóng kết nối database.")
            logging.info("Đóng kết nối database")