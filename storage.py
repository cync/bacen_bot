import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS seen_items (
    source TEXT NOT NULL,
    item_id TEXT NOT NULL,
    PRIMARY KEY (source, item_id)
);
CREATE TABLE IF NOT EXISTS subscribers (
    chat_id BIGINT PRIMARY KEY,
    first_name TEXT,
    username TEXT,
    joined_at TIMESTAMPTZ DEFAULT NOW()
);
"""

class PGStore:
    def __init__(self, url: str):
        self.url = url
        self.conn = None

    def init(self):
        self.conn = psycopg2.connect(self.url)
        with self.conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        self.conn.commit()

    # ============ subscribers ============
    def upsert_subscriber(self, chat_id: int, first_name: str | None, username: str | None):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO subscribers (chat_id, first_name, username)
                VALUES (%s, %s, %s)
                ON CONFLICT (chat_id) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    username = EXCLUDED.username
                """,
                (chat_id, first_name, username),
            )
        self.conn.commit()

    def remove_subscriber(self, chat_id: int):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM subscribers WHERE chat_id=%s", (chat_id,))
        self.conn.commit()

    def list_subscribers(self) -> list[int]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT chat_id FROM subscribers")
            rows = cur.fetchall()
        return [r[0] for r in rows]

    # ============ dedupe ============
    def mark_new_and_return_is_new(self, source: str, item_id: str) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO seen_items (source, item_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                (source, item_id),
            )
            inserted = cur.rowcount == 1
        self.conn.commit()
        return inserted

def get_store() -> PGStore:
    db_url = os.environ["DATABASE_URL"]
    store = PGStore(db_url)
    store.init()
    return store
