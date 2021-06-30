from sqlite3 import Connection as SQLite3Connection

__all__ = ["set_sqlite_foreign_key_pragma"]


def set_sqlite_foreign_key_pragma(conn, _connection_record):
    if isinstance(conn, SQLite3Connection):
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
