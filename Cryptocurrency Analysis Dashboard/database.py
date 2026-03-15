import sqlite3
from pathlib import Path

# path to the sqlite database file. It will be created next to this module.
DB_PATH = Path(__file__).parent / "users.db"


def get_connection():
    """Return a SQLite connection with row access by name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database, creating tables and a default admin user.

    This function is safe to call multiple times; the table is created
    if it does not already exist and the admin user is inserted only once.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

    # make sure there is at least one user so you can log in right away
    add_user("admin", "1234")


def add_user(username: str, password: str) -> bool:
    """Insert a new user into the database.

    Returns ``True`` if the user was created and ``False`` if the username
    already exists.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # username already exists
        return False
    finally:
        conn.close()


def validate_user(username: str, password: str) -> bool:
    """Check whether a username/password pair is valid.

    Passwords are stored in plain text here for simplicity.  In a real
    application you'd want to hash them with ``bcrypt`` or similar.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return False
    return row["password"] == password
