import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "budget.db"

def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Bi-weekly bills table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount_bi_weekly REAL NOT NULL,
            description TEXT,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Credit card debt table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credit_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount_owed REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Account balance table (stores last known state)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS account_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_amount REAL NOT NULL DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# ============================================================================
# Transaction Functions
# ============================================================================

def add_transaction(date: str, description: str, amount: float) -> int:
    """Add a transaction. Returns the transaction ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (date, description, amount)
        VALUES (?, ?, ?)
    ''', (date, description, amount))
    conn.commit()
    trans_id = cursor.lastrowid
    conn.close()
    return trans_id

def get_transactions(start_date: str = None, end_date: str = None) -> list:
    """Get all transactions, optionally filtered by date range."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if start_date and end_date:
        cursor.execute('''
            SELECT id, date, description, amount, created_at
            FROM transactions
            WHERE date >= ? AND date <= ?
            ORDER BY date DESC
        ''', (start_date, end_date))
    else:
        cursor.execute('''
            SELECT id, date, description, amount, created_at
            FROM transactions
            ORDER BY date DESC
        ''')
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_transactions() -> list:
    """Get all transactions."""
    return get_transactions()

def delete_transaction(transaction_id: int):
    """Delete a transaction by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    conn.commit()
    conn.close()

def update_transaction(transaction_id: int, date: str, description: str, amount: float):
    """Update a transaction."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE transactions
        SET date = ?, description = ?, amount = ?
        WHERE id = ?
    ''', (date, description, amount, transaction_id))
    conn.commit()
    conn.close()

def cleanup_old_transactions(years: int = 2):
    """Delete transactions older than specified years."""
    conn = get_connection()
    cursor = conn.cursor()
    cutoff_date = (datetime.now() - timedelta(days=365*years)).strftime('%Y-%m-%d')
    cursor.execute('DELETE FROM transactions WHERE date < ?', (cutoff_date,))
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()
    return rows_deleted

# ============================================================================
# Bills Functions
# ============================================================================

def add_bill(name: str, amount_bi_weekly: float, description: str = "") -> int:
    """Add a bi-weekly bill. Returns the bill ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bills (name, amount_bi_weekly, description, active)
        VALUES (?, ?, ?, 1)
    ''', (name, amount_bi_weekly, description))
    conn.commit()
    bill_id = cursor.lastrowid
    conn.close()
    return bill_id

def get_bills(active_only: bool = True) -> list:
    """Get all bills or only active bills."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if active_only:
        cursor.execute('''
            SELECT id, name, amount_bi_weekly, description, active, created_at
            FROM bills
            WHERE active = 1
            ORDER BY name
        ''')
    else:
        cursor.execute('''
            SELECT id, name, amount_bi_weekly, description, active, created_at
            FROM bills
            ORDER BY name
        ''')
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_total_bi_weekly_bills() -> float:
    """Get sum of all active bi-weekly bills."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(amount_bi_weekly) FROM bills WHERE active = 1')
    result = cursor.fetchone()[0]
    conn.close()
    return result if result is not None else 0.0

def delete_bill(bill_id: int):
    """Delete a bill by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM bills WHERE id = ?', (bill_id,))
    conn.commit()
    conn.close()

def update_bill(bill_id: int, name: str, amount_bi_weekly: float, description: str = ""):
    """Update a bill."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE bills
        SET name = ?, amount_bi_weekly = ?, description = ?
        WHERE id = ?
    ''', (name, amount_bi_weekly, description, bill_id))
    conn.commit()
    conn.close()

def deactivate_bill(bill_id: int):
    """Deactivate a bill without deleting it."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE bills SET active = 0 WHERE id = ?', (bill_id,))
    conn.commit()
    conn.close()

# ============================================================================
# Credit Card Functions
# ============================================================================

def add_credit_card(name: str, amount_owed: float) -> int:
    """Add a credit card. Returns the credit card ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO credit_cards (name, amount_owed)
        VALUES (?, ?)
    ''', (name, amount_owed))
    conn.commit()
    cc_id = cursor.lastrowid
    conn.close()
    return cc_id

def get_credit_cards() -> list:
    """Get all credit cards."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, amount_owed, created_at, updated_at
        FROM credit_cards
        ORDER BY name
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_total_cc_debt() -> float:
    """Get total credit card debt."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(amount_owed) FROM credit_cards')
    result = cursor.fetchone()[0]
    conn.close()
    return result if result is not None else 0.0

def delete_credit_card(cc_id: int):
    """Delete a credit card by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM credit_cards WHERE id = ?', (cc_id,))
    conn.commit()
    conn.close()

def update_credit_card(cc_id: int, name: str, amount_owed: float):
    """Update a credit card."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE credit_cards
        SET name = ?, amount_owed = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (name, amount_owed, cc_id))
    conn.commit()
    conn.close()

# ============================================================================
# Account Data Functions
# ============================================================================

def set_account_total(amount: float):
    """Set the account total amount."""
    conn = get_connection()
    cursor = conn.cursor()
    # First check if there's already a record
    cursor.execute('SELECT id FROM account_data LIMIT 1')
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute('''
            UPDATE account_data
            SET total_amount = ?, last_updated = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (amount, existing[0]))
    else:
        cursor.execute('''
            INSERT INTO account_data (total_amount)
            VALUES (?)
        ''', (amount,))
    
    conn.commit()
    conn.close()

def get_account_total() -> float:
    """Get the last known account total."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT total_amount FROM account_data ORDER BY last_updated DESC LIMIT 1')
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0.0
