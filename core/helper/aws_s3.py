import io
import os
import uuid

import boto3
from botocore.exceptions import ClientError

from django.conf import settings

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

def upload_file_to_s3(file_obj, key):
    file_content = io.BytesIO(file_obj.read())
    file_content.seek(0)
    try:
        s3_client.upload_fileobj(file_content, settings.AWS_STORAGE_BUCKET_NAME, key)
        return True
    except ClientError as e:
        print(f"Upload lỗi: {e}")
        return False

def delete_file_from_s3(key):
    try:
        s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        return True
    except ClientError as e:
        print(f"Xóa file lỗi: {e}")
        return False

def generate_unique_filename(filename: str) -> str:
    base_name, ext = os.path.splitext(filename)
    unique_hex = uuid.uuid4().hex
    return f"post_media/{base_name}_{unique_hex}{ext}"