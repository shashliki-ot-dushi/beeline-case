import os, logging

from .base import get_s3_connection, MINIO_BUCKET


def get_file(subfolder: str, file_path: str) -> str:
    """Получаем код из Minio по пути файла"""
    minio_client = get_s3_connection()

    try:
        key = f"{subfolder}/{file_path}"
        response = minio_client.get_object(MINIO_BUCKET, key)
        code = response.read().decode('utf-8')
        return code
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла из Minio: {e}")
        return ""