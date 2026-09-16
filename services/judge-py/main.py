"""judge-py — bake-off nomzod B: Python worker + isolate.

PULL protokoli (ADR-0004): navbatdan ish tortadi, kiruvchi port ochmaydi.
DB credential OLMAYDI — faqat REDIS_URL.
"""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
import time

import redis

import preflight
import protocol as P
from judge import judge
from protocol import Job, ResultDict

JOBS_KEY = "rankwant:judge:jobs"
RESULTS_KEY = "rankwant:judge:results"

logging.basicConfig(level=logging.INFO, format='{"level":"%(levelname)s","msg":"%(message)s"}')
log = logging.getLogger("judge-py")

_stop = False


def _handle_stop(*_: object) -> None:
    global _stop
    _stop = True
    log.info("to'xtatish signali — navbat bo'shatilmoqda")


def main() -> int:
    if os.environ.get("DATABASE_URL"):
        # 06-architecture xavfsizlik chegarasi: judge host'da DB credential bo'lmaydi
        log.error("DATABASE_URL berilgan — judge host'da DB credential bo'lmasligi shart")
        return 1

    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT, _handle_stop)

    # PREFLIGHT: limitlarni majburlay olmasak — ishlamaymiz.
    # Cheklovsiz judge foydalanuvchi kodini host'ga qo'yib yuboradi.
    try:
        preflight.check()
    except preflight.PreflightError as exc:
        log.error("preflight muvaffaqiyatsiz — worker ishga tushmaydi: %s", exc)
        return 1
    log.info("preflight o'tdi — isolate limitlari majburlanadi")

    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    rdb = redis.Redis.from_url(url)
    rdb.ping()
    log.info("judge-py ishga tushdi (sandbox=isolate)")

    while not _stop:
        item = rdb.brpop(JOBS_KEY, timeout=2)
        if not item:
            continue
        received = time.monotonic()
        try:
            job = Job.from_json(json.loads(item[1]))
        except (ValueError, KeyError, TypeError) as exc:
            # Buzuq xabar — yozib qo'yamiz va davom etamiz. Bunga javob
            # yuborib bo'lmaydi: job_id ham ishonchsiz.
            log.error("job parse qilinmadi: %s", exc)
            continue

        result: ResultDict
        try:
            result = judge(job)
        except Exception:
            # Worker BITTA job tufayli to'xtamasligi kerak. Lekin natijasiz
            # ham qoldirmaymiz: API PENDING holatda abadiy kutib qolardi.
            log.exception("job bajarilmadi: %s", job.job_id)
            result = {
                "job_id": job.job_id,
                # Yiqilgan ish ham marshrutni olib qaytishi SHART: hack
                # dvigateli javobni shu ikki maydondan topadi, aks holda
                # hack abadiy «tekshirilmoqda» bo'lib qolardi.
                "hack_id": job.hack_id,
                "hack_stage": job.hack_stage,
                "verdict": P.IE,
                "score": 0,
                "time_ms": 0,
                "memory_kb": 0,
                "failed_test_index": None,
                "compile_output": "",
                "per_test": [],
                "judge_meta": {
                    "worker": "judge-py",
                    "sandbox": "isolate",
                    "queue_wait_ms": 0,
                    "sandbox_setup_ms": 0,
                    "total_ms": int((time.monotonic() - received) * 1000),
                },
            }

        elapsed = int((time.monotonic() - received) * 1000)
        result["judge_meta"]["queue_wait_ms"] = max(0, elapsed - result["judge_meta"]["total_ms"])

        rdb.lpush(RESULTS_KEY, json.dumps(result))
        log.info(
            "bajarildi job=%s verdict=%s cpu_ms=%s mem_kb=%s total_ms=%s",
            job.job_id,
            result["verdict"],
            result["time_ms"],
            result["memory_kb"],
            result["judge_meta"]["total_ms"],
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
