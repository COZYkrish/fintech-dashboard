import os
import sqlite3

def run_migration():
    db_path = os.path.join("instance", "fintech.db")
    if not os.path.exists(db_path):
        print("[-] Database file not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Columns to check/add in user table
    user_columns = [
        ("credit_score", "INTEGER DEFAULT 700")
    ]

    # Columns to check/add in loan table
    loan_columns = [
        ("interest_rate", "REAL DEFAULT 8.5"),
        ("emi", "REAL DEFAULT 0.0"),
        ("total_interest", "REAL DEFAULT 0.0"),
        ("remaining_balance", "REAL DEFAULT 0.0"),
        ("purpose", "TEXT DEFAULT 'Personal'"),
        ("income", "REAL DEFAULT 0.0"),
        ("collateral", "TEXT DEFAULT ''"),
        ("remarks", "TEXT DEFAULT ''")
    ]

    # Get current user columns
    cursor.execute("PRAGMA table_info(user)")
    existing_user_cols = [row[1] for row in cursor.fetchall()]

    for col_name, col_type in user_columns:
        if col_name not in existing_user_cols:
            print(f"[+] Adding column '{col_name}' to 'user' table...")
            cursor.execute(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}")
            conn.commit()

    # Get current loan columns
    cursor.execute("PRAGMA table_info(loan)")
    existing_loan_cols = [row[1] for row in cursor.fetchall()]

    for col_name, col_type in loan_columns:
        if col_name not in existing_loan_cols:
            print(f"[+] Adding column '{col_name}' to 'loan' table...")
            cursor.execute(f"ALTER TABLE loan ADD COLUMN {col_name} {col_type}")
            conn.commit()

    conn.close()
    print("[+] Migration completed successfully!")

if __name__ == "__main__":
    run_migration()
