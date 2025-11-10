from pathlib import Path
import sqlite3

def get_connection(db_path):
    return sqlite3.connect(db_path)

def has_consent(db_path):
    """Check if user has given consent (consent_given = 1)"""
    try:
        conn = get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT consent_given FROM CONSENT ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        # Return True only if consent_given is 1
        return result[0] == 1 if result else False
    except sqlite3.Error:
        return False

def record_consent(db_path, accepted):
    try:
        conn = get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO CONSENT (consent_given) VALUES (?)", (1 if accepted else 0,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error:
        return False

def revoke_consent(db_path):
    """Set consent_given to 0 in database"""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE CONSENT SET consent_given = 0 WHERE consent_given = 1")
    conn.commit()
    conn.close()
    print("\n✓ Consent revoked. Application will now exit.")
    print("  You will be asked for consent again on next startup.\n")
