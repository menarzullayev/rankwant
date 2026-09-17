#!/usr/bin/env python3
"""Fetch a container image over plain HTTPS, resuming broken downloads, then `docker load` it.

On this network `docker pull` from mcr.microsoft.com dies mid-layer with "failed to
copy: read tcp ...: connection reset by peer" and never resumes: five attempts failed on
2026-09-17 for mcr.microsoft.com/playwright:v1.63.0-noble (956 MB), which E2E needs.
Plain HTTPS range requests to the same blobs did not break. This tool downloads each
blob with Range resume and retries, checks it against its sha256 digest, and writes a
docker-archive tarball that `docker load` accepts (it decompresses gzip layers and checks
them against the config's diff_ids).

Registries that hand out anonymous bearer tokens (Docker Hub) and ones that need none
(MCR) both work. Only public images are supported.

usage:
  python tools/fetch_image.py mcr.microsoft.com/playwright:v1.63.0-noble --load
  python tools/fetch_image.py alpine:3.20 --out alpine.tar --tag rw-fetch-test:alpine
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import re
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

INDEX_TYPES = ", ".join(
    [
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.v2+json",
    ]
)
ATTEMPTS = 40


class Reference:
    def __init__(self, text: str) -> None:
        name, _, tag = text.rpartition(":") if ":" in text.split("/")[-1] else (text, "", "latest")
        first = name.split("/")[0]
        if "." in first or ":" in first or first == "localhost":
            self.registry, self.repo = first, name[len(first) + 1 :]
        else:
            self.registry = "registry-1.docker.io"
            self.repo = name if "/" in name else f"library/{name}"
        self.tag = tag or "latest"
        self.text = text


class Registry:
    def __init__(self, ref: Reference) -> None:
        self.ref = ref
        self.base = f"https://{ref.registry}/v2/{ref.repo}"
        self.token: str | None = None

    def _open(self, url: str, headers: dict[str, str]):
        if self.token:
            headers = {**headers, "Authorization": f"Bearer {self.token}"}
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60)
        except urllib.error.HTTPError as exc:
            challenge = exc.headers.get("WWW-Authenticate", "")
            if exc.code != 401 or self.token or not challenge.startswith("Bearer "):
                raise
            params = dict(re.findall(r'(\w+)="([^"]*)"', challenge))
            query = urllib.parse.urlencode(
                {"service": params.get("service", ""), "scope": params.get("scope", f"repository:{self.ref.repo}:pull")}
            )
            with urllib.request.urlopen(f"{params['realm']}?{query}", timeout=60) as resp:
                body = json.load(resp)
            self.token = body.get("token") or body.get("access_token")
            return self._open(url, headers)

    def json(self, path: str, accept: str) -> dict:
        with self._open(f"{self.base}/{path}", {"Accept": accept}) as resp:
            return json.load(resp)

    def blob(self, digest: str, start: int):
        return self._open(f"{self.base}/blobs/{digest}", {"Range": f"bytes={start}-"})


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def fetch_blob(registry: Registry, digest: str, size: int, blobs: Path) -> Path:
    path = blobs / digest.split(":", 1)[1]
    for attempt in range(1, ATTEMPTS + 1):
        have = path.stat().st_size if path.exists() else 0
        if have == size:
            break
        if have > size:
            path.unlink()
            have = 0
        try:
            with registry.blob(digest, have) as resp:
                # A server that ignores Range answers 200 with the whole blob.
                with path.open("ab" if resp.status == 206 else "wb") as f:
                    while chunk := resp.read(1 << 20):
                        f.write(chunk)
        except (urllib.error.URLError, http.client.HTTPException, OSError, TimeoutError) as exc:
            print(f"  {digest[7:19]} attempt {attempt} at {have >> 20} MB: {exc}", flush=True)
            time.sleep(min(30, 2 * attempt))
    else:
        raise SystemExit(f"{digest}: gave up after {ATTEMPTS} attempts")
    if sha256_of(path) != digest:
        path.unlink()
        raise SystemExit(f"{digest}: checksum mismatch; the partial file was removed, run again")
    print(f"  ok {digest[7:19]} {size >> 20} MB", flush=True)
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image", help="image reference, e.g. mcr.microsoft.com/playwright:v1.63.0-noble")
    ap.add_argument("--platform", default="linux/amd64", help="platform to pick from a multi-arch index")
    ap.add_argument("--out", type=Path, help="tarball path (default: a temporary file, removed after --load)")
    ap.add_argument("--tag", help="tag to give the loaded image (default: the reference itself)")
    ap.add_argument("--load", action="store_true", help="run `docker load` on the result")
    args = ap.parse_args()

    ref = Reference(args.image)
    registry = Registry(ref)
    os_name, _, arch = args.platform.partition("/")
    manifest = registry.json(f"manifests/{ref.tag}", INDEX_TYPES)
    if "manifests" in manifest:
        entry = next(
            (m for m in manifest["manifests"] if m.get("platform", {}).get("os") == os_name and m.get("platform", {}).get("architecture") == arch),
            None,
        )
        if entry is None:
            raise SystemExit(f"{ref.text}: no {args.platform} image in the index")
        manifest = registry.json(f"manifests/{entry['digest']}", INDEX_TYPES)
    blobs_meta = [manifest["config"], *manifest["layers"]]
    total = sum(b["size"] for b in blobs_meta)
    print(f"{ref.text} ({args.platform}): {len(manifest['layers'])} layers, {total >> 20} MB", flush=True)

    with tempfile.TemporaryDirectory() as tmp:
        blobs = Path(tmp) / "blobs" / "sha256"
        blobs.mkdir(parents=True)
        started = time.time()
        with ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(lambda b: fetch_blob(registry, b["digest"], b["size"], blobs), blobs_meta))
        print(f"downloaded in {time.time() - started:.0f} s", flush=True)

        def member(meta: dict) -> str:
            return "blobs/sha256/" + meta["digest"].split(":", 1)[1]

        archive = [{"Config": member(manifest["config"]), "RepoTags": [args.tag or ref.text], "Layers": [member(l) for l in manifest["layers"]]}]
        out = args.out or Path(tmp) / "image.tar"
        (Path(tmp) / "manifest.json").write_text(json.dumps(archive), encoding="utf-8")
        with tarfile.open(out, "w") as tar:
            tar.add(Path(tmp) / "manifest.json", arcname="manifest.json")
            for meta in blobs_meta:
                tar.add(Path(tmp) / member(meta), arcname=member(meta))
        print(f"wrote {out} ({out.stat().st_size >> 20} MB)", flush=True)

        if args.load:
            proc = subprocess.run(["docker", "load", "-i", str(out)], stdin=subprocess.DEVNULL, capture_output=True, text=True)
            print((proc.stdout or proc.stderr).strip(), flush=True)
            if proc.returncode != 0:
                return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
