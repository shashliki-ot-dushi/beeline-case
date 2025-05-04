from .base import get_s3_connection


def get_s3():
    yield get_s3_connection()