"""A judge-independent key for an external problem: `<site>:<id>` (ADR-0062 § 2.5).

Practice links are stored under this key, and so can be matched with a problem
imported later from the same source: the same problem reached by two URL
shapes (Codeforces' `contest/…/problem/…` and `problemset/problem/…`) gets one
key. Plain Python, no Django: `tools/cpuz_snapshot.py` uses it too.
"""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse


def exercise_key(url: str) -> str:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.rstrip("/")
    query = parse_qs(parsed.query)
    if "codeforces" in host:
        m = re.search(r"/gym/(\d+)/problem/(\w+)$", path)
        if m:
            return f"codeforces-gym:{m.group(1)}{m.group(2).upper()}"
        m = re.search(r"/(?:contest|problemset/problem)/(\d+)/(?:problem/)?(\w+)$", path)
        if m:
            return f"codeforces:{m.group(1)}{m.group(2).upper()}"
    if "spoj.com" in host and (m := re.search(r"/problems/([\w-]+)$", path)):
        return f"spoj:{m.group(1).upper()}"
    if "onlinejudge.org" in host and "problem" in query:
        return f"uva:{query['problem'][0]}"
    if "codechef.com" in host and (m := re.search(r"/problems/([\w-]+)$", path)):
        return f"codechef:{m.group(1).upper()}"
    if "cses.fi" in host and (m := re.search(r"/task/(\d+)$", path)):
        return f"cses:{m.group(1)}"
    if "leetcode.com" in host and (m := re.search(r"/problems/([\w-]+)", path)):
        return f"leetcode:{m.group(1).lower()}"
    if "topcoder.com" in host and "pm" in query:
        return f"topcoder:{query['pm'][0]}"
    if "atcoder.jp" in host and (m := re.search(r"/tasks/([\w-]+)$", path)):
        return f"atcoder:{m.group(1).lower()}"
    if "kattis.com" in host and (m := re.search(r"/problems/([\w.-]+)$", path)):
        return f"kattis:{m.group(1).lower()}"
    if "timus" in host and "num" in query:
        return f"timus:{query['num'][0]}"
    if "e-olymp.com" in host and (m := re.search(r"/problems/(\d+)$", path)):
        return f"eolymp:{m.group(1)}"
    tail = path.lower() + (("?" + parsed.query) if parsed.query else "")
    return f"{host}:{tail}"
