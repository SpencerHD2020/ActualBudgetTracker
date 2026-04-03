"""
Test script to populate the database with sample data.
This demonstrates how the application works.
"""
import database
from datetime import datetime, timedelta

def populate_sample_data():
    """Populate the database with sample data."""
    print("Initializing database...")
    database.init_database()
    
    print("\n--- Adding Account Balance ---")
    database.set_account_total(5000.00)
    print(f"Account balance set to: ${database.get_account_total():,.2f}")
    
    print("\n--- Adding Transactions ---")
    transactions = [
        ("2024-03-01", "Monthly Salary", 3000.00),
        ("2024-03-05", "Grocery Store", -150.50),
        ("2024-03-10", "Gas Station", -45.00),
        ("2024-03-12", "Freelance Project", 500.00),
        ("2024-03-15", "Online Shopping", -89.99),
        ("2024-03-20", "Coffee Shop", -5.50),
        ("2024-03-22", "Restaurant Dinner", -45.00),
    ]
    
    for date, description, amount in transactions:
        tid = database.add_transaction(date, description, amount)
        print(f"  Added: {description:25} | {date} | ${amount:>8,.2f}")
    
    print("\n--- Adding Bi-Weekly Bills ---")
    bills = [
        ("Rent", 750.00, "Monthly rent split bi-weekly"),
        ("Utilities", 85.00, "Electric and water"),
        ("Internet", 50.00, "ISP bill"),
        ("Phone", 45.00, "Mobile carrier"),
    ]
    
    for name, amount, description in bills:
        bid = database.add_bill(name, amount, description)
        print(f"  Added: {name:20} | ${amount:>8,.2f} bi-weekly")
    
    total_bills = database.get_total_bi_weekly_bills()
    print(f"  Total bi-weekly bills: ${total_bills:,.2f}")
    
    print("\n--- Adding Credit Card Debt ---")
    cards = [
        ("Chase Sapphire Preferred", 2500.00),
        ("American Express Blue", 1200.00),
        ("Capital One Quicksilver", 350.00),
    ]
    
    for name, amount in cards:
        ccid = database.add_credit_card(name, amount)
        print(f"  Added: {name:30} | ${amount:>8,.2f}")
    
    total_cc = database.get_total_cc_debt()
    print(f"  Total CC debt: ${total_cc:,.2f}")
    
    print("\n--- Financial Summary ---")
    account = database.get_account_total()
    bills = database.get_total_bi_weekly_bills()
    cc = database.get_total_cc_debt()
    
    print(f"Total Amount in Account:        ${account:>12,.2f}")
    print(f"Bi-Weekly Bills:                ${bills:>12,.2f}")
    print(f"After Bills:                    ${account - bills:>12,.2f}")
    print(f"Total CC Debt:                  ${cc:>12,.2f}")
    print(f"Net Available (After all):      ${account - bills - cc:>12,.2f}")
    
    print("\n✅ Sample data loaded successfully!")
    print("\nYou can now run: python main.py")

if __name__ == "__main__":
    populate_sample_data()
