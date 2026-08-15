"""
SQLite Adapter — Supabase API 兼容层

支持 .table(name).select("cols").eq("col","val").execute() 模式
仅用 Python stdlib sqlite3，无需安装任何额外依赖。
"""

import json
import os
import sqlite3


def _serialize_value(val):
    """Serialize list/dict to JSON string for SQLite storage."""
    if isinstance(val, (list, dict)):
        return json.dumps(val, ensure_ascii=False)
    return val
import threading
from typing import List, Optional

DB_PATH = os.getenv(
    "MOLTABLE_DB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "moltable_dev.db")
)


class Result:
    """模拟 Supabase 返回的 Result 对象"""
    def __init__(self, data):  # list or dict (single() → dict, Supabase semantics)
        self.data = data

    def __len__(self):
        return len(self.data)

    @property
    def count(self):
        """Return count from COUNT(*) query or len(data)."""
        if self.data and len(self.data) == 1:
            row = self.data[0]
            if isinstance(row, dict):
                vals = list(row.values())
                if len(vals) == 1 and isinstance(vals[0], (int, float)):
                    return int(vals[0])
        return len(self.data)


class QueryBuilder:
    """兼容 Supabase 链式查询 API"""
    def __init__(self, client: "SQLiteClient", table: str):
        self._client = client
        self._table = table
        self._select_cols = "*"
        self._wheres: List[str] = []
        self._params: list = []
        self._order_clause: Optional[str] = None
        self._limit_val: Optional[int] = None
        self._single_row = False
        self._op = "select"
        self._insert_data: Optional[dict] = None
        self._update_data: Optional[dict] = None

    # -- 链式方法 (都返回 self) --

    def select(self, *cols, **kwargs) -> "QueryBuilder":
        self._op = "select"
        if cols:
            self._select_cols = ", ".join(cols)
        # Support Supabase-style count queries: select("count", count="exact")
        # In SQLite, this becomes SELECT COUNT(*) plus we flag it
        if kwargs.get("count") == "exact" or "count" in cols:
            self._select_cols = "COUNT(*)"
        return self

    def eq(self, col: str, val) -> "QueryBuilder":
        self._wheres.append(f'"{col}" = ?')
        self._params.append(val)
        return self

    def in_(self, col: str, vals: list) -> "QueryBuilder":
        """Support Supabase .in_('col', [a, b, c]) → WHERE col IN (?, ?, ?)"""
        placeholders = ", ".join(["?" for _ in vals])
        self._wheres.append(f'"{col}" IN ({placeholders})')
        self._params.extend(vals)
        return self

    def neq(self, col: str, val) -> "QueryBuilder":
        self._wheres.append(f'"{col}" != ?')
        self._params.append(val)
        return self

    def gt(self, col: str, val) -> "QueryBuilder":
        self._wheres.append(f'"{col}" > ?')
        self._params.append(val)
        return self

    def gte(self, col: str, val) -> "QueryBuilder":
        self._wheres.append(f'"{col}" >= ?')
        self._params.append(val)
        return self

    def lt(self, col: str, val) -> "QueryBuilder":
        self._wheres.append(f'"{col}" < ?')
        self._params.append(val)
        return self

    def lte(self, col: str, val) -> "QueryBuilder":
        self._wheres.append(f'"{col}" <= ?')
        self._params.append(val)
        return self

    def is_(self, col: str, pattern: str) -> "QueryBuilder":
        if pattern == "null":
            self._wheres.append(f'"{col}" IS NULL')
        elif pattern == "not null":
            self._wheres.append(f'"{col}" IS NOT NULL')
        else:
            self._wheres.append(f'"{col}" = ?')
            self._params.append(pattern)
        return self

    def like(self, col: str, pattern: str) -> "QueryBuilder":
        self._wheres.append(f'"{col}" LIKE ?')
        self._params.append(pattern)
        return self

    def ilike(self, col: str, pattern: str) -> "QueryBuilder":
        self._wheres.append(f'LOWER("{col}") LIKE LOWER(?)')
        self._params.append(pattern)
        return self

    def order(self, col: str, *, desc: bool = False) -> "QueryBuilder":
        direction = "DESC" if desc else "ASC"
        self._order_clause = f'"{col}" {direction}'
        return self

    def limit(self, n: int) -> "QueryBuilder":
        self._limit_val = n
        return self

    def single(self) -> "QueryBuilder":
        self._single_row = True
        return self

    def insert(self, data: dict) -> "QueryBuilder":
        self._op = "insert"
        self._insert_data = data
        return self

    def update(self, data: dict) -> "QueryBuilder":
        self._op = "update"
        self._update_data = data
        return self

    def delete(self) -> "QueryBuilder":
        self._op = "delete"
        return self

    # -- 执行 --

    def execute(self) -> Result:
        sql, params = self._build_sql()
        conn = self._client.get_conn()
        cursor = conn.cursor()

        try:
            if self._op == "insert":
                cursor.execute(sql, params)
                conn.commit()
                return Result([self._insert_data])
            elif self._op == "update":
                cursor.execute(sql, params)
                conn.commit()
                # 模拟 Supabase:rowcount>0 表示命中行,返回非空 data(供双花防护等检查)
                return Result([{"updated": True}]) if cursor.rowcount > 0 else Result([])
            elif self._op == "delete":
                cursor.execute(sql, params)
                conn.commit()
                return Result([])
            else:
                cursor.execute(sql, params)
                if self._single_row:
                    # Supabase semantics: .single().execute() → data is a dict,
                    # not a list (all route/service consumers use .data.get(...))
                    row = cursor.fetchone()
                    if row:
                        cols = [desc[0] for desc in cursor.description]
                        return Result(dict(zip(cols, row)))
                    return Result({})
                rows = cursor.fetchall()
                cols = [desc[0] for desc in cursor.description]
                return Result([dict(zip(cols, row)) for row in rows])
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                return Result([])
            raise
        finally:
            cursor.close()

    def _build_sql(self) -> tuple:
        if self._op == "insert":
            cols = list(self._insert_data.keys())
            placeholders = ", ".join(["?" for _ in cols])
            col_names = ", ".join(f'"{c}"' for c in cols)
            sql = f'INSERT INTO "{self._table}" ({col_names}) VALUES ({placeholders})'
            params = [_serialize_value(self._insert_data[c]) for c in cols]
            return sql, params

        elif self._op == "update":
            sets = ", ".join(f'"{k}" = ?' for k in self._update_data)
            sql = f'UPDATE "{self._table}" SET {sets}'
            params = [_serialize_value(v) for v in self._update_data.values()]
            if self._wheres:
                sql += " WHERE " + " AND ".join(self._wheres)
                params += self._params
            return sql, params

        elif self._op == "delete":
            sql = f'DELETE FROM "{self._table}"'
            if self._wheres:
                sql += " WHERE " + " AND ".join(self._wheres)
            return sql, self._params

        else:  # select
            sql = f'SELECT {self._select_cols} FROM "{self._table}"'
            params = []
            if self._wheres:
                sql += " WHERE " + " AND ".join(self._wheres)
                params = self._params
            if self._order_clause:
                sql += f" ORDER BY {self._order_clause}"
            if self._limit_val is not None:
                sql += f" LIMIT {self._limit_val}"
            return sql, params


class SQLiteClient:
    """模拟 supabase.Client 的 SQLite 实现"""

    def __init__(self, db_path: str = None):
        path = db_path or DB_PATH
        self._db_path = path
        self._local = threading.local()
        # 预热一条连接
        self.get_conn()

    def get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            self._local.conn = conn
        return self._local.conn

    def table(self, name: str) -> QueryBuilder:
        return QueryBuilder(self, name)

    def rpc(self, _fn: str, _params: dict = None):
        """pgvector RPC stub — returns empty result for SQLite mode."""
        return _RpcStub()

    def auth(self):
        """Auth stub for SQLite mode."""
        return _AuthStub()

    def close(self):
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None


class _RpcStub:
    """Mock supabase RPC call — raises to trigger SQLite fallback."""
    def execute(self):
        raise NotImplementedError("pgvector rpc not available in SQLite mode")


class _AuthStub:
    """Mock supabase Auth — all methods return None or raise."""
    def get_user(self, token=None): return None
    def get_session(self): return None
    def sign_up(self, *a, **kw): return None
    def sign_in_with_password(self, *a, **kw): return None
    def sign_out(self): return None


def init_schema(client: SQLiteClient):
    """从 repositories/schema_sqlite.sql 初始化数据库"""
    import os
    schema_path = os.path.join(os.path.dirname(__file__), "schema_sqlite.sql")
    conn = client.get_conn()
    if os.path.exists(schema_path):
        with open(schema_path) as f:
            sql = f.read()
        # 按分号分割执行多条语句
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            # 去掉行首的注释行，避免注释+SQL在同一块被跳过
            lines = [line for line in stmt.split("\n") if not line.strip().startswith("--")]
            stmt = "\n".join(lines).strip()
            if stmt:
                try:
                    conn.execute(stmt)
                except sqlite3.OperationalError as e:
                    print(f"  [SQLite schema] skip: {e}")
        conn.commit()
    else:
        print(f"  [SQLite] schema file not found: {schema_path}")
