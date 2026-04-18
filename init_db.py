"""
Interactive script for setting initial database values.
Use this to enter your real account balance, bills, and credit card debts.
"""
import database


def prompt_float(message: str) -> float:
    """Prompt the user for a float value. Returns 0.0 if input is empty."""
    while True:
        raw = input(message).strip()
        if not raw:
            return 0.0
        # Strip leading '$' and commas for convenience
        raw = raw.lstrip("$").replace(",", "")
        try:
            return float(raw)
        except ValueError:
            print("  Invalid number. Please try again.")


def setup_account_balance():
    """Prompt for and set the starting account balance."""
    print("\n--- Account Balance ---")
    amount = prompt_float("Enter your current account balance: $")
    database.set_account_total(amount)
    print(f"  Account balance set to ${amount:,.2f}")


def setup_bills():
    """Prompt for and add bi-weekly bills."""
    print("\n--- Bi-Weekly Bills ---")
    print("Enter your recurring bi-weekly bills. Press Enter with an empty name to finish.\n")

    count = 0
    while True:
        name = input(f"Bill #{count + 1} name (or Enter to finish): ").strip()
        if not name:
            break
        amount = prompt_float(f"  Bi-weekly amount for '{name}': $")
        description = input(f"  Description (optional): ").strip()
        database.add_bill(name, amount, description)
        print(f"  Added bill: {name} - ${amount:,.2f}")
        count += 1

    if count == 0:
        print("  No bills added.")
    else:
        total = database.get_total_bi_weekly_bills()
        print(f"\n  Total bi-weekly bills: ${total:,.2f}")


def setup_credit_cards():
    """Prompt for and add credit card debts."""
    print("\n--- Credit Card Debt ---")
    print("Enter your credit cards. Press Enter with an empty name to finish.\n")

    count = 0
    while True:
        name = input(f"Card #{count + 1} name (or Enter to finish): ").strip()
        if not name:
            break
        amount = prompt_float(f"  Amount owed on '{name}': $")
        database.add_credit_card(name, amount)
        print(f"  Added card: {name} - ${amount:,.2f}")
        count += 1

    if count == 0:
        print("  No credit cards added.")
    else:
        total = database.get_total_cc_debt()
        print(f"\n  Total credit card debt: ${total:,.2f}")


def print_summary():
    """Display a summary of the data that was entered."""
    account = database.get_account_total()
    bills = database.get_total_bi_weekly_bills()
    cc = database.get_total_cc_debt()

    print("\n===== Financial Summary =====")
    print(f"  Account Balance:          ${account:>12,.2f}")
    print(f"  Bi-Weekly Bills:          ${bills:>12,.2f}")
    print(f"  After Bills:              ${account - bills:>12,.2f}")
    print(f"  Total CC Debt:            ${cc:>12,.2f}")
    print(f"  Net Available:            ${account - bills - cc:>12,.2f}")
    print("==============================\n")


def main():
    print("Budget Tracker - Initial Setup")
    print("==============================")
    print("This will walk you through setting your real starting values.\n")

    database.init_database()

    setup_account_balance()
    setup_bills()
    setup_credit_cards()
    print_summary()

    print("Setup complete! You can now run: python main.py")


if __name__ == "__main__":
    main()
