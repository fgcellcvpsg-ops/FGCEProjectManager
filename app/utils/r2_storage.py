import os
import boto3
from botocore.config import Config
import logging
import uuid
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

def get_r2_client():
    endpoint_url = os.getenv('R2_ENDPOINT_URL')
    access_key = os.getenv('R2_ACCESS_KEY_ID')
    secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
    
    if not all([endpoint_url, access_key, secret_key]):
        logger.error("Thiếu cấu hình biến môi trường cho R2 (R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY)")
        return None

    try:
        s3 = boto3.client(
            service_name='s3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )
        return s3
    except Exception as e:
        logger.error(f"Lỗi khởi tạo R2 client: {e}")
        return None

def upload_file_to_r2(file_obj, filename, folder="uploads"):
    s3 = get_r2_client()
    bucket_name = os.getenv('R2_BUCKET_NAME')
    public_url_base = os.getenv('R2_PUBLIC_URL')
    
    if not s3 or not bucket_name or not public_url_base:
        logger.error("Không thể upload: Thiếu cấu hình R2 (R2_BUCKET_NAME hoặc R2_PUBLIC_URL) hoặc s3 client lỗi")
        return None

    safe_filename = secure_filename(filename)
    unique_filename = f"{uuid.uuid4().hex[:8]}_{safe_filename}"
    object_name = f"{folder}/{unique_filename}" if folder else unique_filename

    try:
        content_type = file_obj.content_type if hasattr(file_obj, 'content_type') else 'application/octet-stream'
        
        s3.upload_fileobj(
            file_obj,
            bucket_name,
            object_name,
            ExtraArgs={'ContentType': content_type}
        )
        
        public_url_base = public_url_base.rstrip('/')
        final_url = f"{public_url_base}/{object_name}"
        
        logger.info(f"Đã tải file lên R2 thành công: {final_url}")
        return final_url
        
    except Exception as e:
        logger.error(f"Lỗi khi upload lên R2: {e}")
        return None

def delete_file_from_r2(file_url):
    if not file_url:
        return False
        
    s3 = get_r2_client()
    bucket_name = os.getenv('R2_BUCKET_NAME')
    public_url_base = os.getenv('R2_PUBLIC_URL')
    
    if not s3 or not bucket_name or not public_url_base:
        return False
        
    try:
        public_url_base = public_url_base.rstrip('/')
        if file_url.startswith(public_url_base):
            object_name = file_url[len(public_url_base)+1:]
            
            s3.delete_object(Bucket=bucket_name, Key=object_name)
            logger.info(f"Đã xóa file trên R2: {object_name}")
            return True
        return False
    except Exception as e:
        logger.error(f"Lỗi khi xóa file trên R2 ({file_url}): {e}")
        return False
