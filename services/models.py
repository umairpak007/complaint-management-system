import sqlite3

def create_tables():
    conn = sqlite3.connect("database/cms.db")
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        email TEXT
    )
    """)

    # Customers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        address TEXT
    )
    """)

    # Complaints table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        description TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()
def add_password_column():
    import sqlite3
    conn = sqlite3.connect("database/cms.db")
    cur = conn.cursor()

    try:
        cur.execute("ALTER TABLE users ADD COLUMN password TEXT")
    except:
        pass  # column already exists

    conn.commit()
    conn.close()
