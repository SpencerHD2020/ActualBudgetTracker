import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QDateEdit, QDoubleSpinBox, QTextEdit, QSpinBox, QMessageBox, QDialog,
    QFormLayout, QAbstractItemView
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime
import database


class LoginDialog(QDialog):
    """Dialog for user login and first-time registration."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Budget Tracker – Login")
        self.setMinimumWidth(360)
        self._authenticated = False
        self._no_users = database.get_user_count() == 0
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Budget Tracker")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(title_font)
        layout.addWidget(title)

        if self._no_users:
            subtitle = QLabel("No accounts found. Create your account to get started.")
            subtitle.setWordWrap(True)
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(subtitle)

        form = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        form.addRow("Username:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Password")
        form.addRow("Password:", self.password_input)

        if self._no_users:
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_input.setPlaceholderText("Confirm password")
            form.addRow("Confirm:", self.confirm_input)

        layout.addLayout(form)
        layout.addSpacing(10)

        if self._no_users:
            self.action_btn = QPushButton("Create Account")
            self.action_btn.clicked.connect(self._register)
        else:
            self.action_btn = QPushButton("Log In")
            self.action_btn.clicked.connect(self._login)

        self.action_btn.setDefault(True)
        layout.addWidget(self.action_btn)

        if not self._no_users:
            register_btn = QPushButton("Register New Account")
            register_btn.setFlat(True)
            register_btn.clicked.connect(self._open_register)
            layout.addWidget(register_btn)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    # ------------------------------------------------------------------
    def _login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.status_label.setText("Please enter username and password.")
            return
        if database.authenticate_user(username, password):
            self._authenticated = True
            self.accept()
        else:
            self.status_label.setText("Invalid username or password.")
            self.password_input.clear()
            self.password_input.setFocus()

    def _register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        if not username or not password:
            self.status_label.setText("Please fill in all fields.")
            return
        if password != confirm:
            self.status_label.setText("Passwords do not match.")
            self.confirm_input.clear()
            return
        if len(password) < 8:
            self.status_label.setText("Password must be at least 8 characters.")
            return
        try:
            database.register_user(username, password)
            self._authenticated = True
            self.accept()
        except ValueError as exc:
            self.status_label.setText(str(exc))

    def _open_register(self):
        reg = _RegisterDialog(self)
        reg.exec()

    # ------------------------------------------------------------------
    def authenticated(self) -> bool:
        return self._authenticated


class _RegisterDialog(QDialog):
    """Simple registration dialog (available from the login screen)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register New Account")
        self.setMinimumWidth(320)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        form = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")
        form.addRow("Username:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Choose a password (min 8 chars)")
        form.addRow("Password:", self.password_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirm password")
        form.addRow("Confirm:", self.confirm_input)

        layout.addLayout(form)
        layout.addSpacing(10)

        register_btn = QPushButton("Register")
        register_btn.setDefault(True)
        register_btn.clicked.connect(self._register)
        layout.addWidget(register_btn)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def _register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        if not username or not password:
            self.status_label.setText("Please fill in all fields.")
            return
        if password != confirm:
            self.status_label.setText("Passwords do not match.")
            self.confirm_input.clear()
            return
        if len(password) < 8:
            self.status_label.setText("Password must be at least 8 characters.")
            return
        try:
            database.register_user(username, password)
            self.status_label.setStyleSheet("color: green;")
            self.status_label.setText("Account created! You can now log in.")
            self.username_input.clear()
            self.password_input.clear()
            self.confirm_input.clear()
        except ValueError as exc:
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setText(str(exc))

class DashboardPage(QWidget):
    """Dashboard/home page showing totals overview."""
    
    def __init__(self, refresh_callback=None):
        super().__init__()
        self.refresh_callback = refresh_callback
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Budget Dashboard")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Create labels for each metric
        self.total_amount_label = self._create_metric_label("Total Amount in Account", "$0.00")
        self.after_bills_label = self._create_metric_label("After Bi-Weekly Bills", "$0.00")
        self.cc_debt_label = self._create_metric_label("Total CC Debt", "$0.00")
        self.net_available_label = self._create_metric_label("Net Available (After Bills & CC)", "$0.00")
        
        layout.addWidget(self.total_amount_label[0])
        layout.addWidget(self.total_amount_label[1])
        layout.addSpacing(20)
        
        layout.addWidget(self.after_bills_label[0])
        layout.addWidget(self.after_bills_label[1])
        layout.addSpacing(20)
        
        layout.addWidget(self.cc_debt_label[0])
        layout.addWidget(self.cc_debt_label[1])
        layout.addSpacing(20)
        
        layout.addWidget(self.net_available_label[0])
        layout.addWidget(self.net_available_label[1])
        
        layout.addStretch()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
    
    def _create_metric_label(self, title: str, value: str):
        """Create a metric display with title and value."""
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(11)
        title_label.setFont(title_font)
        
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(14)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet("color: #0066CC;")
        
        return (title_label, value_label)
    
    def refresh_data(self):
        """Refresh all data from database."""
        total_amount = database.get_account_total()
        bi_weekly_bills = database.get_total_bi_weekly_bills()
        cc_debt = database.get_total_cc_debt()
        
        after_bills = total_amount - bi_weekly_bills
        net_available = total_amount - bi_weekly_bills - cc_debt
        
        self.total_amount_label[1].setText(f"${total_amount:,.2f}")
        self.after_bills_label[1].setText(f"${after_bills:,.2f}")
        self.cc_debt_label[1].setText(f"${cc_debt:,.2f}")
        self.net_available_label[1].setText(f"${net_available:,.2f}")


class TransactionsPage(QWidget):
    """Page for managing transactions."""
    
    def __init__(self, refresh_callback=None):
        super().__init__()
        self.refresh_callback = refresh_callback
        self.init_ui()
        self.load_transactions()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Form for adding transaction
        form_layout = QFormLayout()
        
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_input)
        
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("e.g., Grocery store, Gas, Salary")
        form_layout.addRow("Description:", self.description_input)
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(-1000000, 1000000)
        self.amount_input.setSingleStep(0.01)
        form_layout.addRow("Amount:", self.amount_input)
        
        add_btn = QPushButton("Add Transaction")
        add_btn.clicked.connect(self.add_transaction)
        form_layout.addRow(add_btn)
        
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        
        # Table for transactions
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Description", "Amount", "Delete", "Edit"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def add_transaction(self):
        """Add a new transaction."""
        date = self.date_input.date().toString("yyyy-MM-dd")
        description = self.description_input.text().strip()
        amount = self.amount_input.value()
        
        if not description:
            QMessageBox.warning(self, "Input Error", "Please enter a description")
            return
        
        try:
            database.add_transaction(date, description, amount)
            # Update account total
            current_total = database.get_account_total()
            database.set_account_total(current_total + amount)
            
            self.description_input.clear()
            self.amount_input.setValue(0)
            self.load_transactions()
            if self.refresh_callback:
                self.refresh_callback()
            QMessageBox.information(self, "Success", "Transaction added successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add transaction: {str(e)}")
    
    def load_transactions(self):
        """Load and display transactions."""
        transactions = database.get_all_transactions()
        self.table.setRowCount(len(transactions))
        
        for row, trans in enumerate(transactions):
            self.table.setItem(row, 0, QTableWidgetItem(trans['date']))
            self.table.setItem(row, 1, QTableWidgetItem(trans['description']))
            amount_text = f"${trans['amount']:,.2f}"
            self.table.setItem(row, 2, QTableWidgetItem(amount_text))
            
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, tid=trans['id']: self.delete_transaction(tid))
            self.table.setCellWidget(row, 3, delete_btn)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, t=trans: self.edit_transaction(t))
            self.table.setCellWidget(row, 4, edit_btn)
    
    def edit_transaction(self, trans: dict):
        """Open a dialog to edit an existing transaction."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Transaction")
        layout = QFormLayout()

        date_input = QDateEdit()
        date_input.setDate(QDate.fromString(trans['date'], "yyyy-MM-dd"))
        layout.addRow("Date:", date_input)

        desc_input = QLineEdit(trans['description'])
        layout.addRow("Description:", desc_input)

        amount_input = QDoubleSpinBox()
        amount_input.setRange(-1000000, 1000000)
        amount_input.setDecimals(2)
        amount_input.setSingleStep(0.01)
        amount_input.setValue(trans['amount'])
        layout.addRow("Amount:", amount_input)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        dialog.setLayout(layout)

        def save():
            new_date = date_input.date().toString("yyyy-MM-dd")
            new_desc = desc_input.text().strip()
            new_amount = amount_input.value()

            if not new_desc:
                QMessageBox.warning(dialog, "Input Error", "Please enter a description")
                return

            old_amount = trans['amount']
            database.update_transaction(trans['id'], new_date, new_desc, new_amount)
            # Adjust account total by the difference
            current_total = database.get_account_total()
            database.set_account_total(current_total - old_amount + new_amount)

            self.load_transactions()
            if self.refresh_callback:
                self.refresh_callback()
            dialog.accept()

        save_btn.clicked.connect(save)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec()

    def delete_transaction(self, transaction_id: int):
        """Delete a transaction."""
        reply = QMessageBox.question(self, "Confirm Delete", "Delete this transaction?")
        if reply == QMessageBox.StandardButton.Yes:
            trans = database.get_all_transactions()
            # Find the amount
            amount = next((t['amount'] for t in trans if t['id'] == transaction_id), 0)
            
            database.delete_transaction(transaction_id)
            # Update account total
            current_total = database.get_account_total()
            database.set_account_total(current_total - amount)
            
            self.load_transactions()
            if self.refresh_callback:
                self.refresh_callback()


class BillsPage(QWidget):
    """Page for managing bi-weekly bills."""
    
    def __init__(self, refresh_callback=None):
        super().__init__()
        self.refresh_callback = refresh_callback
        self.init_ui()
        self.load_bills()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Form for adding bill
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Rent, Insurance, Utilities")
        form_layout.addRow("Bill Name:", self.name_input)
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 1000000)
        self.amount_input.setSingleStep(0.01)
        form_layout.addRow("Bi-Weekly Amount:", self.amount_input)
        
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Optional description")
        form_layout.addRow("Description:", self.description_input)
        
        add_btn = QPushButton("Add Bill")
        add_btn.clicked.connect(self.add_bill)
        form_layout.addRow(add_btn)
        
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        
        # Table for bills
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Bi-Weekly Amount", "Description", "Delete", "Edit"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def add_bill(self):
        """Add a new bill."""
        name = self.name_input.text().strip()
        amount = self.amount_input.value()
        description = self.description_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a bill name")
            return
        
        try:
            database.add_bill(name, amount, description)
            self.name_input.clear()
            self.amount_input.setValue(0)
            self.description_input.clear()
            self.load_bills()
            if self.refresh_callback:
                self.refresh_callback()
            QMessageBox.information(self, "Success", "Bill added successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add bill: {str(e)}")
    
    def load_bills(self):
        """Load and display bills."""
        bills = database.get_bills(active_only=True)
        self.table.setRowCount(len(bills))
        
        for row, bill in enumerate(bills):
            self.table.setItem(row, 0, QTableWidgetItem(bill['name']))
            amount_text = f"${bill['amount_bi_weekly']:,.2f}"
            self.table.setItem(row, 1, QTableWidgetItem(amount_text))
            self.table.setItem(row, 2, QTableWidgetItem(bill['description'] or ""))
            
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, bid=bill['id']: self.delete_bill(bid))
            self.table.setCellWidget(row, 3, delete_btn)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, b=bill: self.edit_bill(b))
            self.table.setCellWidget(row, 4, edit_btn)
    
    def edit_bill(self, bill: dict):
        """Open a dialog to edit an existing bill."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Bill")
        layout = QFormLayout()

        name_input = QLineEdit(bill['name'])
        layout.addRow("Bill Name:", name_input)

        amount_input = QDoubleSpinBox()
        amount_input.setRange(0, 1000000)
        amount_input.setDecimals(2)
        amount_input.setSingleStep(0.01)
        amount_input.setValue(bill['amount_bi_weekly'])
        layout.addRow("Bi-Weekly Amount:", amount_input)

        desc_input = QLineEdit(bill['description'] or "")
        layout.addRow("Description:", desc_input)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        dialog.setLayout(layout)

        def save():
            new_name = name_input.text().strip()
            new_amount = amount_input.value()
            new_desc = desc_input.text().strip()

            if not new_name:
                QMessageBox.warning(dialog, "Input Error", "Please enter a bill name")
                return

            database.update_bill(bill['id'], new_name, new_amount, new_desc)

            self.load_bills()
            if self.refresh_callback:
                self.refresh_callback()
            dialog.accept()

        save_btn.clicked.connect(save)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec()

    def delete_bill(self, bill_id: int):
        """Delete a bill."""
        reply = QMessageBox.question(self, "Confirm Delete", "Delete this bill?")
        if reply == QMessageBox.StandardButton.Yes:
            database.delete_bill(bill_id)
            self.load_bills()
            if self.refresh_callback:
                self.refresh_callback()


class CreditCardsPage(QWidget):
    """Page for managing credit card debt."""
    
    def __init__(self, refresh_callback=None):
        super().__init__()
        self.refresh_callback = refresh_callback
        self.init_ui()
        self.load_cards()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Form for adding credit card
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Chase Sapphire, Amex Blue")
        form_layout.addRow("Card Name:", self.name_input)
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 1000000)
        self.amount_input.setSingleStep(0.01)
        form_layout.addRow("Amount Owed:", self.amount_input)
        
        add_btn = QPushButton("Add Credit Card")
        add_btn.clicked.connect(self.add_card)
        form_layout.addRow(add_btn)
        
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        
        # Table for credit cards
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Card Name", "Amount Owed", "Delete", "Edit"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def add_card(self):
        """Add a new credit card."""
        name = self.name_input.text().strip()
        amount = self.amount_input.value()
        
        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a card name")
            return
        
        try:
            database.add_credit_card(name, amount)
            self.name_input.clear()
            self.amount_input.setValue(0)
            self.load_cards()
            if self.refresh_callback:
                self.refresh_callback()
            QMessageBox.information(self, "Success", "Credit card added successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add credit card: {str(e)}")
    
    def load_cards(self):
        """Load and display credit cards."""
        cards = database.get_credit_cards()
        self.table.setRowCount(len(cards))
        
        for row, card in enumerate(cards):
            self.table.setItem(row, 0, QTableWidgetItem(card['name']))
            amount_text = f"${card['amount_owed']:,.2f}"
            self.table.setItem(row, 1, QTableWidgetItem(amount_text))
            
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, ccid=card['id']: self.delete_card(ccid))
            self.table.setCellWidget(row, 2, delete_btn)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, c=card: self.edit_card(c))
            self.table.setCellWidget(row, 3, edit_btn)
    
    def edit_card(self, card: dict):
        """Open a dialog to edit an existing credit card entry."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Credit Card")
        layout = QFormLayout()

        name_input = QLineEdit(card['name'])
        layout.addRow("Card Name:", name_input)

        amount_input = QDoubleSpinBox()
        amount_input.setRange(0, 1000000)
        amount_input.setDecimals(2)
        amount_input.setSingleStep(0.01)
        amount_input.setValue(card['amount_owed'])
        layout.addRow("Amount Owed:", amount_input)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        dialog.setLayout(layout)

        def save():
            new_name = name_input.text().strip()
            new_amount = amount_input.value()

            if not new_name:
                QMessageBox.warning(dialog, "Input Error", "Please enter a card name")
                return

            database.update_credit_card(card['id'], new_name, new_amount)

            self.load_cards()
            if self.refresh_callback:
                self.refresh_callback()
            dialog.accept()

        save_btn.clicked.connect(save)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec()

    def delete_card(self, cc_id: int):
        """Delete a credit card."""
        reply = QMessageBox.question(self, "Confirm Delete", "Delete this credit card entry?")
        if reply == QMessageBox.StandardButton.Yes:
            database.delete_credit_card(cc_id)
            self.load_cards()
            if self.refresh_callback:
                self.refresh_callback()


class BudgetApp(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Budget Tracker")
        self.setGeometry(100, 100, 1000, 700)
        
        # Initialize database
        database.init_database()
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        self.dashboard = DashboardPage(refresh_callback=self.refresh_dashboard)
        self.transactions = TransactionsPage(refresh_callback=self.refresh_dashboard)
        self.bills = BillsPage(refresh_callback=self.refresh_dashboard)
        self.credit_cards = CreditCardsPage(refresh_callback=self.refresh_dashboard)
        
        self.tabs.addTab(self.dashboard, "Dashboard")
        self.tabs.addTab(self.transactions, "Transactions")
        self.tabs.addTab(self.bills, "Bills")
        self.tabs.addTab(self.credit_cards, "Credit Cards")
        
        self.setCentralWidget(self.tabs)
    
    def refresh_dashboard(self):
        """Refresh dashboard data."""
        self.dashboard.refresh_data()


def main():
    app = QApplication(sys.argv)

    # Ensure the database is ready before showing the login dialog
    database.init_database()

    login = LoginDialog()
    if login.exec() != QDialog.DialogCode.Accepted or not login.authenticated():
        sys.exit(0)

    window = BudgetApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
