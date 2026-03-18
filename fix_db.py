import os
import sqlalchemy
from sqlalchemy import text, inspect

# Lấy URL kết nối từ biến môi trường
database_url = os.getenv('DATABASE_URL')

if not database_url:
    print("❌ Không tìm thấy biến môi trường DATABASE_URL")
    exit(1)

# Xử lý URL cho SQLAlchemy (postgres:// -> postgresql://)
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Đảm bảo SSL
if "sslmode" not in database_url and "sqlite" not in database_url:
    database_url += "?sslmode=require"

print(f"🔄 Đang kết nối đến Database... (URL ẩn mật khẩu)")

try:
    engine = sqlalchemy.create_engine(database_url)
    
    with engine.connect() as conn:
        inspector = inspect(engine)
        
        # 1. Kiểm tra và thêm cột 'note' cho bảng 'project'
        if 'project' in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns('project')]
            if 'note' not in columns:
                print("⚠️ Cột 'note' chưa tồn tại trong bảng 'project'. Đang thêm...")
                conn.execute(text("ALTER TABLE project ADD COLUMN note TEXT"))
                conn.commit()
                print("✅ Đã thêm cột 'note' thành công!")
            else:
                print("✅ Cột 'note' đã tồn tại. Không cần thay đổi.")
        else:
            print("⚠️ Bảng 'project' chưa tồn tại. Bỏ qua.")

        # 2. Xử lý bảng alembic_version (nếu bị lệch version)
        # Xóa luôn version cũ để reset trạng thái migration, tránh lỗi 'Can't locate revision'
        if 'alembic_version' in inspector.get_table_names():
             print("🔄 Đang reset bảng alembic_version để tránh xung đột...")
             conn.execute(text("DELETE FROM alembic_version"))
             conn.commit()
             print("✅ Đã xóa lịch sử migration cũ.")

    print("🎉 Hoàn tất sửa lỗi Database!")

except Exception as e:
    print(f"❌ Có lỗi xảy ra: {e}")
    exit(1)
