# services/judge-py — bake-off nomzod B

**Python worker + isolate** (GPL-2.0+). [ADR-0004](../../docs/07-adr/0004-judge-engine.md) bake-off.

Qoidalar `judge-go` bilan bir xil: pull protokoli, kiruvchi port yo'q, DB credential yo'q.
Farq: isolate cgroup v1 ga bog'liq — bake-off shuni o'lchaydi.
