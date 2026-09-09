"""Test ma'lumoti uchun S3 (local: MinIO).

Test DB da saqlanmaydi (05-domain-model): judge S3 dan o'qiydi, DB ga
umuman ulanmaydi (08-technical-spec xavfsizlik chegarasi).
"""

from __future__ import annotations

import functools
import logging
from typing import Any

import boto3
from botocore.config import Config
from django.conf import settings
from django.core.cache import cache

log = logging.getLogger(__name__)

#: Namuna test qancha bo'lsa ham sahifada o'qiladi — kattasini kesamiz,
#: aks holda noto'g'ri belgilangan katta test butun sahifani cho'ktirardi.
MAX_SAMPLE_BYTES = 16 * 1024
SAMPLES_TTL = 3600
#: Nosozlik NATIJASI qisqa keshlanadi. Uni bir soat saqlash MinIO bir
#: soniya uzilganda ham sahifani bir soatga namunasiz qoldirardi
#: (o'lchandi: saqlash qaytgach ham `samples` 0 bo'lib qoldi).
FAILURE_TTL = 60

#: Saqlash yiqilganda boto3 standart sozlamada 60 soniya kutadi va besh
#: marta qayta uradi — sahifa 15 soniya osilib qolgan edi. Yuk ostida bu
#: gunicorn worker'larini tugatib, butun saytni cho'ktirardi.
S3_TIMEOUT = Config(
    connect_timeout=2, read_timeout=3, retries={"max_attempts": 2, "mode": "standard"}
)


@functools.lru_cache(maxsize=1)
def client() -> Any:  # boto3 mijozi tipi runtime'da yaratiladi
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_KEY,
        aws_secret_access_key=settings.S3_SECRET,
        region_name=settings.S3_REGION,
        config=S3_TIMEOUT,
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


def get_test_data(ref: str) -> str:
    """`s3://bucket/key` havolasidan matn o'qiydi."""
    bucket, _, key = ref.removeprefix("s3://").partition("/")
    body: bytes = client().get_object(Bucket=bucket, Key=key)["Body"].read(MAX_SAMPLE_BYTES)
    return body.decode("utf-8", errors="replace")


def samples_cache_key(slug: str) -> str:
    return f"problem:samples:{slug}"


def sample_tests(problem: Any) -> list[dict[str, Any]]:
    """Masalaning namuna testlari — matni bilan.

    Har sahifa ochilishida S3 ga ikki marta bormaslik uchun keshlanadi;
    test yuklanganda `staff_views` keshni tozalaydi. S3 yiqilsa masala
    matni baribir ochilishi kerak, shuning uchun xato yutiladi.
    """
    key = samples_cache_key(problem.slug)
    cached = cache.get(key)
    if cached is not None:
        return cached  # type: ignore[no-any-return]

    samples: list[dict[str, Any]] = []
    complete = True
    for test in problem.tests.filter(is_sample=True).order_by("order"):
        try:
            samples.append(
                {
                    "order": test.order,
                    "input": get_test_data(test.input_ref),
                    "expected": get_test_data(test.output_ref),
                }
            )
        except Exception:
            # Bittasi o'qilmasa saqlash yiqilgan bo'lishi ehtimoli katta —
            # qolganini urinish har biriga yana timeout qo'shardi.
            log.warning("namuna test o'qilmadi: %s #%s", problem.slug, test.order)
            complete = False
            break

    cache.set(key, samples, SAMPLES_TTL if complete else FAILURE_TTL)
    return samples
