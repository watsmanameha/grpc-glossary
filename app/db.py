import aiosqlite

DB_PATH = "/data/glossary.db"

INIT_SQL = """
CREATE TABLE IF NOT EXISTS terms(
  keyword TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT NOT NULL
);
"""

SEED = [
  ("ast", "Абстрактное синтаксическое дерево (AST)",
   "Структурное дерево исходного кода, используемое при анализе программ."),
  ("gof", "Паттерны GoF",
   "Классические шаблоны проектирования, рассматриваемые в ВКР."),
  ("observer", "Наблюдатель",
   "Поведенческий паттерн, реализующий подписку на события."),
  ("grpc", "gRPC",
   "Фреймворк удалённого вызова процедур, основанный на HTTP/2 и Protobuf.")
]

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(INIT_SQL)
        for k, t, d in SEED:
            await db.execute(
                "INSERT OR IGNORE INTO terms(keyword,title,description) VALUES(?,?,?)",
                (k, t, d)
            )
        await db.commit()

async def get_term(keyword: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM terms WHERE keyword=?", (keyword,))
        row = await cur.fetchone()
        return dict(row) if row else None

async def list_terms(limit=10, offset=0):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM terms ORDER BY keyword LIMIT ? OFFSET ?", (limit, offset)
        )
        rows = await cur.fetchall()
        cur2 = await db.execute("SELECT COUNT(*) as c FROM terms")
        total = (await cur2.fetchone())["c"]
        return [dict(r) for r in rows], total

async def add_term(term: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO terms(keyword,title,description) VALUES(?,?,?)",
            (term["keyword"], term["title"], term["description"])
        )
        await db.commit()
        return True
