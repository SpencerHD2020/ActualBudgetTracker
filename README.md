# Budget Tracker Application

A comprehensive graphical budget tracking application built with PyQt6 and SQLite.

## Features

### 📊 Dashboard
- **Total Amount in Account**: Your current account balance
- **After Bi-Weekly Bills**: Account balance minus bi-weekly bill obligations
- **Total CC Debt**: Sum of all credit card debt
- **Net Available**: Account balance minus bills and CC debt

### 💰 Transactions
- Record income and expenses with date, description, and amount
- Supports negative and positive values
- Full transaction history with sorting by date
- Delete transactions when needed
- Automatic recalculation of account balance

### 📋 Bi-Weekly Bills
- Track recurring bills on a bi-weekly basis (typically half of monthly bills)
- Maintain a list of active bills
- Bills automatically factored into dashboard calculations
- Easy deactivation without deletion

### 💳 Credit Card Management
- Track multiple credit card debts
- Store card name and amount owed
- Included in net available calculations

### 🗄️ Data Persistence
- All data stored in SQLite database (`budget.db`)
- Account data persists on exit and loads on startup
- Transactions kept for 2 years (configurable cleanup)

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
```bash
# Create and activate virtual environment (optional but recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

Or with the venv:
```bash
.venv\Scripts\python.exe main.py
```

## File Structure

- **main.py**: Main application entry point and PyQt6 UI
- **database.py**: SQLite database functions and business logic
- **init_db.py**: Interactive CLI script for setting your real initial values
- **wipe_db.py**: Utility script to wipe all data from the database
- **cleanup.py**: Script for archiving old transactions
- **test_data.py**: (Optional) Populate sample/demo data for testing
- **budget.db**: SQLite database file (created on first run)

## Database Management

### Initial Setup
Set your real starting values (account balance, bills, credit cards) interactively:

```bash
python init_db.py
```

### Wiping the Database
To clear all data from every table (transactions, bills, credit cards, account data):

```bash
python wipe_db.py
```

You will be asked to confirm before any data is deleted.

### Transaction Cleanup
To delete transactions older than 2 years:

```bash
python cleanup.py
```

Modify the `years` parameter in `cleanup.py` to change the retention period.

## Usage

### Adding a Transaction
1. Go to the "Transactions" tab
2. Enter the date, description, and amount (positive for income, negative for expenses)
3. Click "Add Transaction"
4. Dashboard automatically updates with the new balance

### Managing Bills
1. Go to the "Bills" tab
2. Enter the bill name and bi-weekly amount
3. Optionally add a description
4. Click "Add Bill"
5. Bills are automatically summed and displayed on the dashboard

### Managing Credit Cards
1. Go to the "Credit Cards" tab
2. Enter the card name and amount owed
3. Click "Add Credit Card"
4. Amount is included in net available calculations

### Checking Your Budget
- Return to the "Dashboard" tab to see all summary metrics
- Click "Refresh" to reload data from database

## Database Schema

### transactions
- id: Primary key
- date: Transaction date (YYYY-MM-DD)
- description: Transaction description
- amount: Signed floating-point amount
- created_at: Timestamp of creation

### bills
- id: Primary key
- name: Bill name
- amount_bi_weekly: Bi-weekly amount
- description: Optional description
- active: Whether the bill is active (1) or inactive (0)
- created_at: Timestamp of creation

### credit_cards
- id: Primary key
- name: Credit card name
- amount_owed: Current amount owed
- created_at: Timestamp of creation
- updated_at: Timestamp of last update

### account_data
- id: Primary key
- total_amount: Last known account balance
- last_updated: Timestamp of last update

## Tips

- **Regular Updates**: Update your account balance when you transfer money in/out
- **Bill Tracking**: Add bills in half-month increments matching your pay schedule
- **Cleanup**: Run the cleanup script quarterly to maintain database performance
- **Negative Transactions**: Use negative amounts for expenses to decrease your balance
- **Card Debt**: Update credit card amounts when you make payments or new charges

## Future Enhancements

- Category-based transaction filtering
- Budget goals and alerts
- Multi-account support
- Export to CSV/Excel
- Recurring transaction automation
- Chart visualizations and trends
