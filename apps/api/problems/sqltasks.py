"""SQL problems — task kind `sql` (ADR-0053).

The solver submits one `SELECT`. Each test is a setup script (the schema
and its rows); the query's result is printed and compared with the
jury's, like the output of any program.

**Where it runs.** Inside the sandbox that already runs every Python
submission: the job's source is the small runner below with the query
embedded as a string literal, and the database is SQLite in memory. No
database server, no network, no second sandbox to defend — the judge does
not know the kind exists. ADR-0053 named PostgreSQL; a server per test
would have been a new, privileged surface on the machine that holds the
platform's own database, so the first version is SQLite and the dialect
is said plainly on the problem page.

**What the query may do.** Read. SQLite's authorizer refuses everything
that is not a read (`INSERT`, `DELETE`, `PRAGMA`, `ATTACH`, DDL), and the
driver refuses more than one statement. Even past both, the code is
inside the same jail as any other submission.

**Output.** One row per line, columns separated by a tab; `NULL` for
null; a real number with at most six decimals. Column names are not
printed — an alias must not decide a verdict. A setup script that starts
with `UNORDERED_MARK` has its rows sorted before printing, for problems
that do not ask for an order.
"""

from __future__ import annotations

from problems.models import Language

#: The language row an SQL attempt is filed under. Inactive: offered only
#: on SQL problems, where it is the only one.
SQL_LANGUAGE = "sql"

#: First line of a test's setup script: the row order is not part of the answer.
UNORDERED_MARK = "-- rankwant: unordered"

#: More rows than this is an error, not an answer.
MAX_ROWS = 100_000

_RUNNER = '''"""SQL runner: the test's setup script on stdin, the submitted query below."""
import sqlite3
import sys

QUERY = __QUERY__
UNORDERED_MARK = __MARK__
MAX_ROWS = __MAX_ROWS__
READS = (
    sqlite3.SQLITE_SELECT,
    sqlite3.SQLITE_READ,
    sqlite3.SQLITE_FUNCTION,
    sqlite3.SQLITE_RECURSIVE,
)


def fail(message):
    print("SQL error: " + str(message), file=sys.stderr)
    sys.exit(1)


def cell(value):
    if value is None:
        return "NULL"
    if isinstance(value, float):
        text = "%.6f" % value
        return text.rstrip("0").rstrip(".") if "." in text else text
    if isinstance(value, bytes):
        return value.hex()
    return str(value).replace("\\t", " ").replace("\\n", " ").replace("\\r", " ")


setup = sys.stdin.read()
db = sqlite3.connect(":memory:")
db.executescript(setup)
db.commit()
# From here on the connection only reads.
db.set_authorizer(lambda action, *_: sqlite3.SQLITE_OK if action in READS else sqlite3.SQLITE_DENY)
try:
    cursor = db.execute(QUERY)
    if cursor.description is None:
        fail("the statement returns no rows; write a SELECT")
    rows = cursor.fetchmany(MAX_ROWS + 1)
except (sqlite3.Error, sqlite3.Warning, ValueError) as error:
    fail(error)
if len(rows) > MAX_ROWS:
    fail("more than %d rows" % MAX_ROWS)
lines = ["\\t".join(cell(value) for value in row) for row in rows]
if setup.lstrip().lower().startswith(UNORDERED_MARK):
    lines.sort()
sys.stdout.write("".join(line + "\\n" for line in lines))
'''


def sql_language() -> Language:
    row, _ = Language.objects.get_or_create(
        code=SQL_LANGUAGE,
        defaults={
            "name": "SQL",
            "version": "SQLite 3",
            "source_file": "main.py",
            "compile_cmd": [],
            "run_cmd": ["python3", "{src}"],
            "is_active": False,
        },
    )
    return row


def compose(query: str) -> str:
    """The program the judge runs for this query.

    `repr` makes the query a Python string literal whatever it contains:
    quotes, backslashes and newlines stay data and never become code.
    """
    return (
        _RUNNER.replace("__QUERY__", repr(query))
        .replace("__MARK__", repr(UNORDERED_MARK))
        .replace("__MAX_ROWS__", str(MAX_ROWS))
    )
