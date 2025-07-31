-- ===================================================================
-- SQL SCRIPT TẠO DATABASE CHO DỰ ÁN HỒ SƠ KHOA HỌC
-- Phiên bản cuối cùng, đã cập nhật theo các cải tiến
-- ===================================================================

-- Tạo database nếu chưa tồn tại (tùy chọn)
CREATE DATABASE IF NOT EXISTS hoso_khoahoc_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Sử dụng database vừa tạo
USE hoso_khoahoc_db;

-- Xóa các bảng cũ nếu tồn tại để tạo lại từ đầu
DROP TABLE IF EXISTS `journal_points`;
DROP TABLE IF EXISTS `scientific_works`;
DROP TABLE IF EXISTS `journals`;
DROP TABLE IF EXISTS `criteria_rules`;
DROP TABLE IF EXISTS `users`;


-- Bảng 1: Quản lý người dùng
CREATE TABLE `users` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `full_name` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `phone_number` VARCHAR(20) NULL,
  `birth_date` DATE NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Bảng 2: Danh mục các tạp chí, hội nghị (Cập nhật: Thêm cột link)
CREATE TABLE `journals` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `name` TEXT NOT NULL,
  `issn` VARCHAR(255) NULL COMMENT 'Dành cho bản in (p-ISSN)',
  `eissn` VARCHAR(255) NULL COMMENT 'Dành cho bản điện tử (e-ISSN)',
  `publisher` TEXT NULL,
  `type` VARCHAR(255) NULL,
  `link` VARCHAR(2048) NULL COMMENT 'Link tham khảo của tạp chí',
  INDEX `idx_issn` (`issn`),
  INDEX `idx_eissn` (`eissn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Bảng 3: Điểm số của tạp chí (Xử lý việc điểm thay đổi theo thời gian)
CREATE TABLE `journal_points` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `journal_id` INT UNSIGNED NOT NULL,
  `field_of_study` VARCHAR(255) NULL COMMENT 'Ngành hoặc liên ngành',
  `points` DECIMAL(5, 2) NOT NULL,
  `publication_type` VARCHAR(50) NULL COMMENT 'Loại hình xuất bản, ví dụ: Online, Không online',
  `effective_from` DATE NOT NULL,
  `effective_to` DATE NULL,
  FOREIGN KEY (`journal_id`) REFERENCES `journals` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Bảng 4: Các công trình khoa học của người dùng (Cập nhật: Thêm các trạng thái mới)
CREATE TABLE `scientific_works` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT UNSIGNED NOT NULL,
  `work_type` ENUM('article', 'book', 'report', 'patent') NOT NULL COMMENT 'Loại công trình khoa học',
  `title` TEXT NOT NULL,
  `journal_id` INT UNSIGNED NULL COMMENT 'Liên kết đến tạp chí nếu là bài báo',
  `publication_date` DATE NOT NULL,
  `is_main_author` BOOLEAN DEFAULT FALSE,
  `authors` TEXT NULL COMMENT 'Danh sách các tác giả khác',
  `calculated_points` DECIMAL(5, 2) DEFAULT 0.00,
  `status` ENUM('pending_verification', 'verified_auto', 'needs_manual_review', 'verified_manual', 'rejected', 'verification_failed') DEFAULT 'pending_verification' COMMENT 'Trạng thái kiểm duyệt',
  `verification_notes` TEXT NULL COMMENT 'Ghi chú từ quá trình xác minh',
  `evidence_url` VARCHAR(2048) NULL COMMENT 'Link hoặc đường dẫn tới file minh chứng',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`journal_id`) REFERENCES `journals` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Bảng 5: Lưu trữ các quy tắc xét duyệt (Rule Engine)
CREATE TABLE `criteria_rules` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `academic_title` ENUM('PGS', 'GS') NOT NULL COMMENT 'Chức danh áp dụng',
  `rule_code` VARCHAR(100) NOT NULL UNIQUE COMMENT 'Mã định danh cho quy tắc, ví dụ: MIN_TOTAL_POINTS',
  `description` TEXT NULL,
  `rule_details` JSON NOT NULL COMMENT 'Lưu chi tiết quy tắc dưới dạng JSON, ví dụ: {"value": 10, "unit": "points", "condition": ">="}'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
