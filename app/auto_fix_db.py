import sqlalchemy
from sqlalchemy import text, inspect
import logging

def auto_fix_database(database_url):
    """
    Hàm này sẽ tự động kiểm tra và thêm cột 'note' vào bảng 'project' nếu thiếu.
    Được gọi ngay khi ứng dụng Flask khởi tạo.
    """
    logger = logging.getLogger(__name__)
    
    if not database_url:
        logger.error("❌ auto_fix: Không tìm thấy DATABASE_URL")
        return

    # Xử lý URL cho SQLAlchemy
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    if "sslmode" not in database_url and "sqlite" not in database_url:
        database_url += "?sslmode=require"

    try:
        engine = sqlalchemy.create_engine(database_url)
        with engine.connect() as conn:
            inspector = inspect(engine)
            
            # 1. Thêm cột 'note' vào bảng 'project'
            if 'project' in inspector.get_table_names():
                columns = [c['name'] for c in inspector.get_columns('project')]
                if 'note' not in columns:
                    logger.warning("⚠️ auto_fix: Cột 'note' chưa tồn tại. Đang thêm...")
                    conn.execute(text("ALTER TABLE project ADD COLUMN note TEXT"))
                    conn.commit()
                    logger.info("✅ auto_fix: Đã thêm cột 'note' thành công!")
                else:
                    logger.info("✅ auto_fix: Cột 'note' đã tồn tại.")

            # 2. Thêm cột 'question' và 'source' nếu thiếu
            if 'project' in inspector.get_table_names():
                columns = [c['name'] for c in inspector.get_columns('project')]
                if 'question' not in columns:
                    conn.execute(text("ALTER TABLE project ADD COLUMN question TEXT"))
                    conn.commit()
                    logger.info("✅ auto_fix: Đã thêm cột 'question'")
                if 'source' not in columns:
                    conn.execute(text("ALTER TABLE project ADD COLUMN source VARCHAR(255)"))
                    conn.commit()
                    logger.info("✅ auto_fix: Đã thêm cột 'source'")

    except Exception as e:
        logger.error(f"❌ auto_fix: Lỗi khi sửa Database: {e}")
