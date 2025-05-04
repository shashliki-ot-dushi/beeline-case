import os

from minio import Minio


MINIO_URL = os.getenv('AWS_ENDPOINT_URL', 'minio:9000').strip('/')
MINIO_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
MINIO_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
MINIO_BUCKET = os.getenv('AWS_S3_BUCKET')


minio_client = Minio(
    MINIO_URL,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)


def get_s3_connection():
    return minio_client