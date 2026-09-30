from pathlib import Path

loc = Path(__file__).resolve().parents[1] / "apps/web/src/i18n/locales"
old = (
    '    "RankWant problems use standard input and output. Sample: sum of two integers (A + B).",\n'
    '    "about.io.tabsLabel": "I/O style",\n'
    '  "about.io.kind.stdio"'
)
new = (
    '    "RankWant problems use standard input and output. Sample: sum of two integers (A + B).",\n'
    '  "about.io.tabsLabel": "I/O style",\n'
    '  "about.io.kind.stdio"'
)
for p in loc.glob("*.ts"):
    if p.name == "uz.ts":
        continue
    t = p.read_text(encoding="utf-8")
    if old not in t:
        continue
    t = t.replace(old, new)
    t = t.replace('"about.sampleMissing":', '  "about.sampleMissing":')
    p.write_text(t, encoding="utf-8")
    print("fixed", p.name)
