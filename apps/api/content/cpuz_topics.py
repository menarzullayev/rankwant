"""Our topics for the imported library (ADR-0062 § 2.6: category, level and topics).

A category maps to our broad topics; a few articles map to a narrower one we
already have. The topics feed the "topic and difficulty" practice layer and
the topic filters. A slug that does not exist in a database is skipped.
"""

from __future__ import annotations

CATEGORY_TOPICS: dict[str, list[str]] = {
    "algebra": ["sonlar-nazariyasi", "math"],
    "combinatorics": ["kombinatorika"],
    "data-structures": ["malumotlar-tuzilmasi"],
    "dynamic-programming": ["dp"],
    "game-theory": ["oyinlar-nazariyasi"],
    "geometry": ["geometriya"],
    "graph": ["graflar-nazariyasi", "graphs"],
    "linear-algebra": ["matritsa", "math"],
    "num-methods": ["math"],
    "others": [],
    "schedules": ["greedy"],
    "sequences": ["malumotlar-tuzilmasi"],
    "string": ["satrlar"],
}

ARTICLE_TOPICS: dict[str, list[str]] = {
    "algebra--binary-exp": ["ikkilik-daraja"],
    "algebra--big-integer": ["katta-arifmetika"],
    "data_structures--segment_tree": ["segment-daraxti"],
    "data_structures--fenwick": ["fenwick-daraxti"],
    "num_methods--binary_search": ["ikkilik-qidiruv"],
    "num_methods--ternary_search": ["uchlik-qidiruv"],
    "string--string-hashing": ["heshlash"],
    "string--rabin-karp": ["heshlash"],
    "graph--edmonds_karp": ["maksimal-oqim"],
    "graph--dinic": ["maksimal-oqim"],
    "graph--mpm": ["maksimal-oqim"],
    "graph--push-relabel": ["maksimal-oqim"],
    "graph--push-relabel-faster": ["maksimal-oqim"],
    "graph--min_cost_flow": ["maksimal-oqim"],
    "graph--flow_with_demands": ["maksimal-oqim"],
    "geometry--intersecting_segments": ["skanerlash-chizigi"],
    "geometry--length-of-segments-union": ["skanerlash-chizigi"],
}


def topics_for(entry_id: str, category: str) -> list[str]:
    return [*ARTICLE_TOPICS.get(entry_id, []), *CATEGORY_TOPICS.get(category, [])]
