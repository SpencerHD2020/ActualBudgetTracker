"""
Temporary script to wipe all database tables.
Run this to clear all data (transactions, bills, credit cards, account data).
"""
import database
import os
import sys


def wipe_all_tables():
    """Delete all rows from every table in the database."""
    if not os.path.exists(database.DB_PATH):
        print("No database file found. Nothing to wipe.")
        return

    conn = database.get_connection()
    cursor = conn.cursor()

    tables = ["transactions", "bills", "credit_cards", "account_data"]
    for table in tables:
        cursor.execute("DELETE FROM " + table)
        print(f"  Cleared table: {table}")

    conn.commit()
    conn.close()
    print("\nAll database tables have been wiped.")


if __name__ == "__main__":
    print("WARNING: This will permanently delete ALL data from the budget database.")
    confirm = input("Type 'yes' to confirm: ").strip().lower()
    if confirm == "yes":
        wipe_all_tables()
    else:
        print("Aborted. No data was deleted.")
        sys.exit(0)
