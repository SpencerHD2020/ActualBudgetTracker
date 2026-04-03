"""
Cleanup script for old transactions.
Run this periodically to archive/delete transactions older than 2 years.
"""
import database
from datetime import datetime

def cleanup_transactions():
    """Run the transaction cleanup process."""
    print("Starting transaction cleanup...")
    deleted_count = database.cleanup_old_transactions(years=2)
    print(f"Deleted {deleted_count} transactions older than 2 years")
    print("Cleanup complete!")

if __name__ == "__main__":
    cleanup_transactions()
