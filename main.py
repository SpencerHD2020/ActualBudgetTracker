import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QDateEdit, QDoubleSpinBox, QTextEdit, QSpinBox, QMessageBox, QDialog,
    QFormLayout, QAbstractItemView, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
from datetime import datetime
import database

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    _MATPLOTLIB_AVAILABLE = True
except ImportError:
    _MATPLOTLIB_AVAILABLE = False

_MAX_TRANSACTION_AMOUNT = 1_000_000

class DashboardPage(QWidget):
    """Dashboard/home page showing totals overview."""

    _CARD_COLORS = {
        "balance":    "#3498DB",
        "after_bills": "#E67E22",
        "cc_debt":    "#E74C3C",
        "net":        "#27AE60",
    }

    def __init__(self, refresh_callback=None):
        super().__init__()
        self.refresh_callback = refresh_callback
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        self.setStyleSheet("background-color: #F0F4F8;")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        # ── Title ────────────────────────────────────────────────────────────
        title = QLabel("💰  Budget Dashboard")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2C3E50; background: transparent;")
        main_layout.addWidget(title)

        # ── Metric cards row ─────────────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(14)

        self.total_card   = self._create_metric_card("Account Balance",      "$0.00", self._CARD_COLORS["balance"])
        self.bills_card   = self._create_metric_card("After Bi-Weekly Bills","$0.00", self._CARD_COLORS["after_bills"])
        self.cc_card      = self._create_metric_card("Total CC Debt",        "$0.00", self._CARD_COLORS["cc_debt"])
        self.net_card     = self._create_metric_card("Net Available",        "$0.00", self._CARD_COLORS["net"])

        for card_frame, _ in (self.total_card, self.bills_card, self.cc_card, self.net_card):
            cards_row.addWidget(card_frame)

        main_layout.addLayout(cards_row)

        # ── Chart ────────────────────────────────────────────────────────────
        if _MATPLOTLIB_AVAILABLE:
            self.figure = Figure(figsize=(8, 3), dpi=80)
            self.figure.patch.set_facecolor("#F0F4F8")
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setMinimumHeight(220)
            self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            main_layout.addWidget(self.canvas)
        else:
            self.figure = None
            self.canvas = None

        # ── Refresh button ───────────────────────────────────────────────────
        refresh_btn = QPushButton("🔄  Refresh")
        refresh_btn.setFixedWidth(120)
        refresh_btn.setStyleSheet(
            "QPushButton { background-color: #2C3E50; color: white; font-weight: bold; "
            "border-radius: 6px; padding: 6px 14px; border: none; }"
            "QPushButton:hover { background-color: #34495E; }"
        )
        refresh_btn.clicked.connect(self.refresh_data)
        main_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def _create_metric_card(self, title: str, value: str, color: str):
        """Return (QFrame, value_QLabel) for a colored metric card."""
        frame = QFrame()
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        frame.setStyleSheet(
            f"QFrame {{ background-color: {color}; border-radius: 10px; padding: 4px; }}"
        )

        vbox = QVBoxLayout()
        vbox.setContentsMargins(14, 12, 14, 12)
        vbox.setSpacing(4)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 9))
        title_lbl.setStyleSheet("color: rgba(255,255,255,200); background: transparent;")
        title_lbl.setWordWrap(True)

        value_lbl = QLabel(value)
        value_lbl.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        value_lbl.setStyleSheet("color: white; background: transparent;")

        vbox.addWidget(title_lbl)
        vbox.addWidget(value_lbl)
        frame.setLayout(vbox)
        return (frame, value_lbl)

    def _update_chart(self, account_balance: float, after_bills: float, cc_debt: float, net: float):
        """Redraw the matplotlib bar chart."""
        if not _MATPLOTLIB_AVAILABLE or self.figure is None:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        labels = ["Balance", "After Bills", "CC Debt", "Net Available"]
        values = [account_balance, after_bills, cc_debt, net]
        colors = [
            self._CARD_COLORS["balance"],
            self._CARD_COLORS["after_bills"],
            self._CARD_COLORS["cc_debt"],
            self._CARD_COLORS["net"] if net >= 0 else self._CARD_COLORS["cc_debt"],
        ]

        bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=0.7, width=0.55)
        ax.axhline(y=0, color="#2C3E50", linewidth=0.8, alpha=0.35)

        for bar, val in zip(bars, values):
            y_pos = bar.get_height()          # positive: top of bar; negative: bottom of bar
            va = "bottom" if val >= 0 else "top"
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                y_pos,
                f"${val:,.0f}",
                ha="center", va=va,
                fontsize=8.5, fontweight="bold", color="#2C3E50",
            )

        ax.set_title("Financial Overview", fontsize=11, fontweight="bold", pad=8, color="#2C3E50")
        ax.set_ylabel("Amount ($)", fontsize=9, color="#555")
        ax.tick_params(labelsize=8.5, colors="#555")
        ax.set_facecolor("#F0F4F8")
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        for spine in ("bottom", "left"):
            ax.spines[spine].set_color("#CBD5E0")

        self.figure.tight_layout(pad=1.2)
        self.canvas.draw()

    def refresh_data(self):
        """Refresh all data from database."""
        total_amount    = database.get_account_total()
        bi_weekly_bills = database.get_total_bi_weekly_bills()
        cc_debt         = database.get_total_cc_debt()

        after_bills   = total_amount - bi_weekly_bills
        net_available = total_amount - bi_weekly_bills - cc_debt

        self.total_card[1].setText(f"${total_amount:,.2f}")
        self.bills_card[1].setText(f"${after_bills:,.2f}")
        self.cc_card[1].setText(f"${cc_debt:,.2f}")
        self.net_card[1].setText(f"${net_available:,.2f}")

        # Colour net card red when negative
        net_color = self._CARD_COLORS["net"] if net_available >= 0 else self._CARD_COLORS["cc_debt"]
        self.net_card[0].setStyleSheet(
            f"QFrame {{ background-color: {net_color}; border-radius: 10px; padding: 4px; }}"
        )

        self._update_chart(total_amount, after_bills, cc_debt, net_available)


class TransactionsPage(QWidget):
    """Page for managing transactions."""

    def __init__(self, refresh_callback=None):
        super().__init__()
        self.refresh_callback = refresh_callback
        self.init_ui()
        self.load_transactions()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Section title
        form_title = QLabel("Add Transaction")
        form_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        form_title.setStyleSheet("color: #2C3E50;")
        layout.addWidget(form_title)

        # Form for adding transaction
        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addRow("Date:", self.date_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("e.g., Grocery store, Gas, Salary")
        form_layout.addRow("Description:", self.description_input)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, _MAX_TRANSACTION_AMOUNT)
        self.amount_input.setSingleStep(0.01)
        form_layout.addRow("Amount ($):", self.amount_input)

        # Income / Expense toggle switch
        toggle_row = QHBoxLayout()
        self.sign_toggle = QPushButton("➖  Expense")
        self.sign_toggle.setCheckable(True)
        self.sign_toggle.setChecked(False)   # False = Expense (negative), True = Income (positive)
        self.sign_toggle.setFixedWidth(130)
        self.sign_toggle.toggled.connect(self._on_sign_toggle)
        self._on_sign_toggle(False)           # apply initial style
        toggle_row.addWidget(self.sign_toggle)
        toggle_row.addStretch()
        form_layout.addRow("Type:", toggle_row)

        add_btn = QPushButton("Add Transaction")
        add_btn.setStyleSheet(
            "QPushButton { background-color: #2C3E50; color: white; font-weight: bold; "
            "border-radius: 5px; padding: 6px 16px; border: none; }"
            "QPushButton:hover { background-color: #34495E; }"
        )
        add_btn.clicked.connect(self.add_transaction)
        form_layout.addRow(add_btn)

        layout.addLayout(form_layout)
        layout.addSpacing(10)

        # Table for transactions
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Description", "Amount", "Delete", "Edit"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def _on_sign_toggle(self, is_income: bool):
        """Update the toggle button appearance based on income/expense state."""
        if is_income:
            self.sign_toggle.setText("➕  Income")
            self.sign_toggle.setStyleSheet(
                "QPushButton { background-color: #27AE60; color: white; font-weight: bold; "
                "border-radius: 5px; padding: 4px 10px; border: none; }"
                "QPushButton:hover { background-color: #229954; }"
            )
        else:
            self.sign_toggle.setText("➖  Expense")
            self.sign_toggle.setStyleSheet(
                "QPushButton { background-color: #E74C3C; color: white; font-weight: bold; "
                "border-radius: 5px; padding: 4px 10px; border: none; }"
                "QPushButton:hover { background-color: #C0392B; }"
            )
    
    def add_transaction(self):
        """Add a new transaction."""
        date = self.date_input.date().toString("yyyy-MM-dd")
        description = self.description_input.text().strip()
        amount = self.amount_input.value()

        # Apply sign based on toggle: Income = positive, Expense = negative
        if not self.sign_toggle.isChecked():
            amount = -amount

        if not description:
            QMessageBox.warning(self, "Input Error", "Please enter a description")
            return

        try:
            database.add_transaction(date, description, amount)
            # Update account total
            current_total = database.get_account_total()
            database.set_account_total(current_total + amount)

            # Clear form and reset toggle to Expense for fast batch entry
            self.description_input.clear()
            self.amount_input.setValue(0)
            self.sign_toggle.setChecked(False)
            self.load_transactions()
            if self.refresh_callback:
                self.refresh_callback()
            # No success dialog — allows rapid back-to-back entry
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add transaction: {str(e)}")
    
    def load_transactions(self):
        """Load and display transactions."""
        transactions = database.get_all_transactions()
        self.table.setRowCount(len(transactions))

        green = QColor(39, 174, 96)

        for row, trans in enumerate(transactions):
            date_item   = QTableWidgetItem(trans['date'])
            desc_item   = QTableWidgetItem(trans['description'])
            amount_text = f"${trans['amount']:,.2f}"
            amount_item = QTableWidgetItem(amount_text)

            if trans['amount'] > 0:
                for item in (date_item, desc_item, amount_item):
                    item.setForeground(green)

            self.table.setItem(row, 0, date_item)
            self.table.setItem(row, 1, desc_item)
            self.table.setItem(row, 2, amount_item)

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
        date_input.setCalendarPopup(True)
        layout.addRow("Date:", date_input)

        desc_input = QLineEdit(trans['description'])
        layout.addRow("Description:", desc_input)

        amount_input = QDoubleSpinBox()
        amount_input.setRange(-_MAX_TRANSACTION_AMOUNT, _MAX_TRANSACTION_AMOUNT)
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
        self.amount_input.setRange(0, _MAX_TRANSACTION_AMOUNT)
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
        amount_input.setRange(0, _MAX_TRANSACTION_AMOUNT)
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
        self.amount_input.setRange(0, _MAX_TRANSACTION_AMOUNT)
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
        amount_input.setRange(0, _MAX_TRANSACTION_AMOUNT)
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
    window = BudgetApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
