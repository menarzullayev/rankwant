"""Test ma'lumoti uchun S3 (local: MinIO).

Test DB da saqlanmaydi (05-domain-model): judge S3 dan o'qiydi, DB ga
umuman ulanmaydi (08-technical-spec xavfsizlik chegarasi).
"""

from __future__ import annotations

import functools
from typing import Any

import boto3
from django.conf import settings


@functools.lru_cache(maxsize=1)
def client() -> Any:  # boto3 mijozi tipi runtime'da yaratiladi
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_KEY,
        aws_secret_access_key=settings.S3_SECRET,
        region_name=settings.S3_REGION,
    )


def ensure_bucket() -> None:
    s3 = client()
    existing = {b["Name"] for b in s3.list_buckets()["Buckets"]}
    if settings.S3_BUCKET not in existing:
        s3.create_bucket(Bucket=settings.S3_BUCKET)


def put_test_data(key: str, content: str) -> str:
    """Obyektni yozadi va judge tushunadigan `s3://bucket/key` havolasini qaytaradi."""
    client().put_object(Bucket=settings.S3_BUCKET, Key=key, Body=content.encode())
    return f"s3://{settings.S3_BUCKET}/{key}"
