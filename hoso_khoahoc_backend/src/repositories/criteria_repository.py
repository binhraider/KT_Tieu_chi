# src/repositories/criteria_repository.py

import pandas as pd
import os
from typing import List, Dict, Any

class CriteriaRepository:
    def __init__(self):
        # SỬA ĐỔI: Xây dựng đường dẫn tuyệt đối đến các file dữ liệu
        # __file__ là đường dẫn đến file hiện tại (criteria_repository.py)
        # os.path.dirname() sẽ lấy thư mục chứa file đó (tức là 'repositories')
        # os.path.join(...) sẽ đi lùi 2 cấp ('..', '..') để lên thư mục gốc,
        # sau đó đi vào thư mục 'scripts'
        base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts')

        # Giả sử các file của bạn nằm trong thư mục 'scripts'
        self.pgs_criteria_path = os.path.join(base_path, 'data.xlsx - Tiến trình PGS.csv')
        self.gs_criteria_path = os.path.join(base_path, 'data.xlsx - Tiến trình GS.csv')
        self.tieu_chuan_path = os.path.join(base_path, 'Tiêu chuẩn chức danh.csv')

    def _load_criteria(self, file_path: str) -> List[Dict[str, Any]]:
        """Hàm nội bộ để đọc file CSV chứa quy tắc."""
        try:
            df = pd.read_csv(file_path)
            return df.to_dict('records')
        except FileNotFoundError:
            # Ném ra lỗi rõ ràng hơn để dễ dàng debug
            raise FileNotFoundError(f"Không tìm thấy file quy tắc tại đường dẫn: {file_path}")
        except Exception as e:
            raise IOError(f"Lỗi khi đọc file {file_path}: {e}")

    def get_pgs_criteria(self) -> List[Dict[str, Any]]:
        """Lấy các quy tắc cho chức danh PGS."""
        return self._load_criteria(self.pgs_criteria_path)

    def get_gs_criteria(self) -> List[Dict[str, Any]]:
        """Lấy các quy tắc cho chức danh GS."""
        return self._load_criteria(self.gs_criteria_path)

    def get_tieu_chuan(self) -> List[Dict[str, Any]]:
        """Lấy các tiêu chuẩn chung."""
        return self._load_criteria(self.tieu_chuan_path)