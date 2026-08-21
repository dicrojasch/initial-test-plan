import sqlite3


def get_user_by_id(user_id: str):
    """Query the users table for a row by id.

    NOTE: Intentionally vulnerable to SQL injection for demonstration
    purposes. This is flagged by Semgrep during security scans.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE users (id TEXT, name TEXT)")
    cursor.executemany(
        "INSERT INTO users (id, name) VALUES (?, ?)",
        [("1", "Alice"), ("2", "Bob")],
    )

    cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
    row = cursor.fetchone()
    conn.close()
    return row
