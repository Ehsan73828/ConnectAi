import sqlite3
import os
from datetime import datetime


# =========================================================
# Database Path
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_PATH = os.path.join(
    BASE_DIR,
    "contacts.db"
)


# =========================================================
# Connection
# =========================================================

def get_connection():
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    return conn


# =========================================================
# Initialize Database
# =========================================================

def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT,

            phone TEXT,

            email TEXT,

            note TEXT,

            followup TEXT,

            contact_type TEXT DEFAULT 'شخصی',

            vip INTEGER DEFAULT 0,

            created_at TEXT,

            updated_at TEXT

        )
    """)

    # -----------------------------------------------------
    # Upgrade old database
    # -----------------------------------------------------

    cursor.execute(
        "PRAGMA table_info(contacts)"
    )

    existing_columns = {
        row["name"]
        for row in cursor.fetchall()
    }

    if "created_at" not in existing_columns:

        cursor.execute("""
            ALTER TABLE contacts
            ADD COLUMN created_at TEXT
        """)

    if "updated_at" not in existing_columns:

        cursor.execute("""
            ALTER TABLE contacts
            ADD COLUMN updated_at TEXT
        """)

    # -----------------------------------------------------
    # Indexes
    # -----------------------------------------------------

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_contacts_name
        ON contacts(name)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_contacts_phone
        ON contacts(phone)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_contacts_followup
        ON contacts(followup)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_contacts_type
        ON contacts(contact_type)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_contacts_vip
        ON contacts(vip)
    """)

    # -----------------------------------------------------
    # Fill missing timestamps in old records
    # -----------------------------------------------------

    now = datetime.now().isoformat(
        timespec="seconds"
    )

    cursor.execute("""
        UPDATE contacts
        SET created_at=?
        WHERE created_at IS NULL
           OR created_at=''
    """, (now,))

    cursor.execute("""
        UPDATE contacts
        SET updated_at=?
        WHERE updated_at IS NULL
           OR updated_at=''
    """, (now,))

    conn.commit()
    conn.close()


# =========================================================
# Add Contact
# =========================================================

def add_contact(
    name,
    phone,
    email,
    note,
    followup,
    contact_type="شخصی"
):

    now = datetime.now().isoformat(
        timespec="seconds"
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO contacts (
            name,
            phone,
            email,
            note,
            followup,
            contact_type,
            vip,
            created_at,
            updated_at
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        (name or "").strip(),
        (phone or "").strip(),
        (email or "").strip(),
        (note or "").strip(),
        followup or "",
        contact_type or "شخصی",
        0,
        now,
        now
    ))

    contact_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return contact_id


# =========================================================
# Get All Contacts
# =========================================================

def get_contacts():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            phone,
            email,
            note,
            followup,
            contact_type,
            vip,
            created_at,
            updated_at

        FROM contacts

        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return [
        row_to_dict(row)
        for row in rows
    ]


# =========================================================
# Convert Row → Dictionary
# =========================================================

def row_to_dict(row):

    return {

        "id": row["id"],

        "name": row["name"] or "",

        "phone": row["phone"] or "",

        "email": row["email"] or "",

        "note": row["note"] or "",

        "followup": row["followup"] or "",

        "contact_type":
            row["contact_type"] or "شخصی",

        "vip":
            row["vip"] or 0,

        "created_at":
            row["created_at"] or "",

        "updated_at":
            row["updated_at"] or ""
    }


# =========================================================
# Get Single Contact
# =========================================================

def get_contact(contact_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            phone,
            email,
            note,
            followup,
            contact_type,
            vip,
            created_at,
            updated_at

        FROM contacts

        WHERE id=?
    """, (contact_id,))

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return row_to_dict(row)


# =========================================================
# Update Contact
# =========================================================

def update_contact(
    contact_id,
    name,
    phone,
    email,
    note,
    followup,
    contact_type="شخصی"
):

    now = datetime.now().isoformat(
        timespec="seconds"
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE contacts

        SET
            name=?,
            phone=?,
            email=?,
            note=?,
            followup=?,
            contact_type=?,
            updated_at=?

        WHERE id=?
    """, (
        (name or "").strip(),
        (phone or "").strip(),
        (email or "").strip(),
        (note or "").strip(),
        followup or "",
        contact_type or "شخصی",
        now,
        contact_id
    ))

    changed = cursor.rowcount

    conn.commit()
    conn.close()

    return changed > 0


# =========================================================
# Delete Contact
# =========================================================

def delete_contact(contact_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM contacts

        WHERE id=?
    """, (contact_id,))

    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted > 0


# =========================================================
# VIP Toggle
# =========================================================

def toggle_vip(
    contact_id,
    current_vip
):

    now = datetime.now().isoformat(
        timespec="seconds"
    )

    new_value = (
        0
        if current_vip
        else 1
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE contacts

        SET
            vip=?,
            updated_at=?

        WHERE id=?
    """, (
        new_value,
        now,
        contact_id
    ))

    changed = cursor.rowcount

    conn.commit()
    conn.close()

    return changed > 0


# =========================================================
# Search Contacts
# =========================================================

def search_contacts(query):

    query = (query or "").strip()

    if not query:
        return get_contacts()

    conn = get_connection()
    cursor = conn.cursor()

    value = f"%{query}%"

    cursor.execute("""
        SELECT
            id,
            name,
            phone,
            email,
            note,
            followup,
            contact_type,
            vip,
            created_at,
            updated_at

        FROM contacts

        WHERE
            name LIKE ?
            OR phone LIKE ?
            OR email LIKE ?
            OR note LIKE ?

        ORDER BY id DESC
    """, (
        value,
        value,
        value,
        value
    ))

    rows = cursor.fetchall()

    conn.close()

    return [
        row_to_dict(row)
        for row in rows
    ]


# =========================================================
# Count Contacts
# =========================================================

def count_contacts():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM contacts
    """)

    count = cursor.fetchone()[0]

    conn.close()

    return count


# =========================================================
# Count VIP Contacts
# =========================================================

def count_vip():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM contacts
        WHERE vip=1
    """)

    count = cursor.fetchone()[0]

    conn.close()

    return count


# =========================================================
# Database Health Check
# =========================================================

def check_database():

    try:

        conn = get_connection()

        conn.execute(
            "SELECT 1"
        )

        conn.close()

        return True

    except Exception:

        return False


# =========================================================
# Start Database
# =========================================================

init_db()