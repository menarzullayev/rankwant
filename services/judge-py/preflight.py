"""Ishga tushishdan oldingi tayyorlash va tekshiruv.

2026-09-06: judge-go cgroup limitlarini jimgina qo'ya olmagani uchun fork bomb
cheklovsiz ishlab, host'ni ikki marta yiqitdi. Qoida: limitlarni majburlay
olmaydigan worker UMUMAN ishga tushmasligi kerak.

DIQQAT — tuzatilgan taxmin: isolate cgroup v2 da ISHLAYDI. Muammo cgroup
versiyasida emas, isolate'ning standart `cg_root = auto:/run/isolate/cgroup`
konfiguratsiyasida: u systemd boshqaradigan cgroup'ni kutadi. Konteynerda
systemd yo'q, va isolate'ning cg-keeper'i konteynerning O'Z cgroup'ida
subtree_control yoqmoqchi bo'lib "Device or resource busy" oladi (cgroup v2
da jarayonlari bor cgroup kontrollerlarni delegatsiya qila olmaydi).

Yechim judge-go dagi bilan bir xil: root ostida TOZA cgroup yaratamiz va
kontrollerlarni o'zimiz delegatsiya qilamiz.
"""

from __future__ import annotations

import os
import socket
import subprocess
import tempfile
from pathlib import Path

from sandbox import ISOLATE

CGROUP_ROOT = Path("/sys/fs/cgroup")
CG_PARENT = CGROUP_ROOT / "rankwant-isolate"
CONFIG_PATHS = [Path("/usr/local/etc/isolate"), Path("/usr/local/etc/isolate.conf")]


class PreflightError(RuntimeError):
    pass


def _port_env(name: str, default: int) -> int:
    """Butun sonli env; bo'sh/noto'g'ri qiymatda standart."""
    raw = os.environ.get(name, "")
    if not raw:
        return default
    try:
        port = int(raw)
    except ValueError as exc:
        raise PreflightError(f"{name}: noto'g'ri port: {raw!r}") from exc
    if not 0 < port < 65536:
        raise PreflightError(f"{name}: noto'g'ri port: {raw!r}")
    return port


def check_network() -> None:
    """ADR-0028: tarmoq chegarasi KOD bilan tekshiriladi — fail closed.

    judge-go PreflightNetwork bilan bir xil shartnoma: TAQIQLANGAN
    manzarga (postgres:5432, api:8000, + JUDGE_FORBIDDEN_HOSTS) ulanish
    MUVAFFAQIYATLI bo'lsa — PreflightError (worker ishga tushmaydi).
    Ulanish xatosi (refused/timeout/DNS yechilmadi) — chegara yopiq.
    Gate: JUDGE_NET_PREFLIGHT=1 bo'lmasa — o'tkazib yuboriladi (compose'da
    judge-net, internal: true bilan birga yoqiladi).
    """
    if os.environ.get("JUDGE_NET_PREFLIGHT") != "1":
        return

    postgres_host = os.environ.get("POSTGRES_HOST") or "postgres"
    targets: dict[str, int] = {
        postgres_host: _port_env("POSTGRES_PORT", 5432),
        "api": _port_env("API_PORT", 8000),
    }
    extra = os.environ.get("JUDGE_FORBIDDEN_HOSTS", "")
    for spec in extra.split(","):
        spec = spec.strip()
        if not spec:
            continue
        host, sep, port_str = spec.partition(":")
        if not sep:
            raise PreflightError(
                f"JUDGE_FORBIDDEN_HOSTS: port bo'lmagan yozuv: {spec!r} (host:port kutilgan)"
            )
        try:
            port = int(port_str)
        except ValueError as exc:
            raise PreflightError(f"JUDGE_FORBIDDEN_HOSTS: noto'g'ri port: {spec!r}") from exc
        if not 0 < port < 65536:
            raise PreflightError(f"JUDGE_FORBIDDEN_HOSTS: noto'g'ri port: {spec!r}")
        targets[host] = port

    for host, port in targets.items():
        try:
            sock = socket.create_connection((host, port), timeout=2)
        except OSError:
            # refused / timeout / DNS yechilmadi — chegara yopiq.
            continue
        sock.close()
        raise PreflightError(
            f"preflight: {host}:{port} ga ulanish MUVAFFAQIYATLI — tarmoq chegarasi buzilgan "
            f"(judge {host} tarmog'ida bo'lmasligi kerak; ADR-0028: judge-net, internal: true)"
        )


def _prepare_cgroup() -> None:
    """Toza ota cgroup yaratib, kontrollerlarni delegatsiya qiladi."""
    if not (CGROUP_ROOT / "cgroup.controllers").exists():
        raise PreflightError("cgroup v2 topilmadi — bu worker cgroup v2 ni talab qiladi")
    CG_PARENT.mkdir(parents=True, exist_ok=True)
    try:
        (CG_PARENT / "cgroup.subtree_control").write_text("+pids +memory +cpu")
    except OSError as exc:
        raise PreflightError(
            f"kontrollerlarni delegatsiya qilib bo'lmadi ({exc}). Konteyner "
            "--privileged --cgroupns=host bilan ishlashi kerak."
        ) from exc
    # Ota darajasidagi shift — bola cgroup sozlashda xato bo'lsa ham
    # portlash radiusi shu bilan chegaralanadi (judge-go dagi kabi).
    for name, value in (("pids.max", "512"), ("memory.max", "4294967296")):
        try:
            (CG_PARENT / name).write_text(value)
        except OSError:
            pass


def _point_isolate_at_cgroup() -> None:
    """isolate konfiguratsiyasini bizning cgroup'imizga yo'naltiradi.

    isolate ikki fayldan o'qishi mumkin (`isolate` va `isolate.conf`) —
    ikkalasini ham yozamiz.
    """
    written = False
    for cfg in CONFIG_PATHS:
        if not cfg.exists():
            continue
        lines = []
        for line in cfg.read_text().splitlines():
            if line.startswith("cg_root ="):
                line = f"cg_root = {CG_PARENT}"
            lines.append(line)
        cfg.write_text("\n".join(lines) + "\n")
        written = True
    if not written:
        raise PreflightError(f"isolate konfiguratsiyasi topilmadi: {CONFIG_PATHS}")


def check() -> None:
    """Limitlarni HAQIQATAN qo'llay olamizmi — taxmin emas, sinov."""
    if not Path(ISOLATE).exists():
        raise PreflightError(f"isolate topilmadi: {ISOLATE}")

    _prepare_cgroup()
    _point_isolate_at_cgroup()

    box = subprocess.run(
        [ISOLATE, "--box-id=99", "--cg", "--init"],
        capture_output=True,
        text=True,
        check=False,
    )
    if box.returncode != 0:
        raise PreflightError(f"isolate --init: {box.stdout.strip()} {box.stderr.strip()}")
    box_path = Path(box.stdout.strip()) / "box"
    try:
        # Xotira limiti majburlanishini ISBOTLAYMIZ: 64 MB limitda 400 MB
        # ajratishga urinamiz va cg-oom-killed kutamiz.
        (box_path / "probe.py").write_text("a = bytearray(400*1024*1024)\nprint(len(a))\n")
        with tempfile.NamedTemporaryFile("r", suffix=".txt") as meta:
            subprocess.run(
                [
                    ISOLATE,
                    "--box-id=99",
                    "--cg",
                    f"--meta={meta.name}",
                    "--cg-mem=65536",
                    "--time=10",
                    "--wall-time=20",
                    "-p4",
                    "--run",
                    "--",
                    "/usr/bin/python3",
                    "probe.py",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            report = dict(line.split(":", 1) for line in meta.read().splitlines() if ":" in line)
        if report.get("cg-oom-killed") != "1":
            raise PreflightError(
                "xotira limiti MAJBURLANMADI: 64 MB chegarada 400 MB ajratildi "
                f"(meta: {report}). Cheklovsiz judge ishga tushirilmaydi."
            )
    finally:
        subprocess.run(
            [ISOLATE, "--box-id=99", "--cg", "--cleanup"], capture_output=True, check=False
        )
