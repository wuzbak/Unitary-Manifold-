"""Accounting service — chart of accounts, AP/AR, and payments.

Modeled on the free/open-source double-entry accounting conventions used by
GnuCash and ledger-cli (plain-text accounting), adapted to a lightweight
production-friendly schema: a flat chart of accounts plus accounts-payable
(vendor bills) and accounts-receivable (client invoices) ledgers tied to
payments. Designed to integrate with (not replace) full bookkeeping systems —
``export_general_ledger_csv`` produces a CSV importable into GnuCash, Wave,
or QuickBooks-compatible tools.
"""
from __future__ import annotations

import csv
import io
import uuid
from datetime import date
from pathlib import Path

from ..db.schema import get_conn

DEFAULT_CHART_OF_ACCOUNTS = [
    ("1000", "Cash / Production Account", "asset"),
    ("1100", "Accounts Receivable", "asset"),
    ("2000", "Accounts Payable", "liability"),
    ("3000", "Equity / Financing", "equity"),
    ("4000", "Revenue — Sales & Licensing", "revenue"),
    ("4100", "Revenue — Tax Incentives / Rebates", "revenue"),
    ("5000", "Above-the-Line", "expense"),
    ("5100", "Below-the-Line — Production", "expense"),
    ("5200", "Below-the-Line — Post Production", "expense"),
    ("5300", "Other — Marketing & Distribution", "expense"),
]

GNUCASH_CAPABILITY_PACKET = {
    "project": "Gnucash/gnucash",
    "research_basis": ["README", "gnucash-cli", "libgnucash/engine"],
    "why": "Free, open-source, double-entry accounting with multi-currency, "
    "invoicing, and reporting — the most mature FOSS alternative to QuickBooks.",
    "integration": "Export the production chart of accounts and AP/AR ledgers "
    "as CSV/QIF for import into GnuCash for full double-entry bookkeeping, "
    "payroll, and tax reporting beyond this production-tracking layer.",
}

LEDGER_CLI_CAPABILITY_PACKET = {
    "project": "ledger/ledger",
    "research_basis": ["README.md", "doc/ledger3.texi"],
    "why": "Plain-text, command-line double-entry accounting — scriptable, "
    "auditable, and diffable in version control alongside the production repo.",
    "integration": "export_general_ledger_csv() output converts 1:1 into "
    "ledger-cli journal entries for teams that prefer plain-text accounting.",
}


class AccountingService:
    """Chart of accounts, vendor/client ledgers, AP/AR, and payments."""

    def __init__(self, db_path: Path):
        self.db_path = db_path

    # ------------------------------------------------------------------
    # Chart of accounts
    # ------------------------------------------------------------------

    def seed_default_chart_of_accounts(self, project_id: str) -> list[dict]:
        with get_conn(self.db_path) as conn:
            self._ensure_project(conn, project_id)
            existing = conn.execute(
                "SELECT COUNT(*) FROM chart_of_accounts WHERE project_id=?", (project_id,)
            ).fetchone()[0]
            if existing:
                return self.chart_of_accounts(project_id)
            for code, name, account_type in DEFAULT_CHART_OF_ACCOUNTS:
                conn.execute(
                    """INSERT INTO chart_of_accounts (id, project_id, code, name, account_type)
                       VALUES (?, ?, ?, ?, ?)""",
                    (str(uuid.uuid4()), project_id, code, name, account_type),
                )
        return self.chart_of_accounts(project_id)

    def chart_of_accounts(self, project_id: str) -> list[dict]:
        with get_conn(self.db_path) as conn:
            return _fetch_all(
                conn,
                "SELECT * FROM chart_of_accounts WHERE project_id=? ORDER BY code",
                (project_id,),
            )

    # ------------------------------------------------------------------
    # Vendors / clients
    # ------------------------------------------------------------------

    def create_vendor(self, project_id: str, name: str, category: str = "", contact: str = "",
                       terms: str = "Net 30", tax_id: str = "", notes: str = "") -> dict:
        if not name.strip():
            raise ValueError("Vendor name is required.")
        vendor_id = str(uuid.uuid4())
        with get_conn(self.db_path) as conn:
            self._ensure_project(conn, project_id)
            conn.execute(
                """INSERT INTO vendors (id, project_id, name, category, contact, terms, tax_id, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (vendor_id, project_id, name, category, contact, terms, tax_id, notes),
            )
        return {"id": vendor_id, "project_id": project_id, "name": name}

    def create_client(self, project_id: str, name: str, contact: str = "",
                       billing_address: str = "", notes: str = "") -> dict:
        if not name.strip():
            raise ValueError("Client name is required.")
        client_id = str(uuid.uuid4())
        with get_conn(self.db_path) as conn:
            self._ensure_project(conn, project_id)
            conn.execute(
                """INSERT INTO clients (id, project_id, name, contact, billing_address, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (client_id, project_id, name, contact, billing_address, notes),
            )
        return {"id": client_id, "project_id": project_id, "name": name}

    def list_vendors(self, project_id: str) -> list[dict]:
        with get_conn(self.db_path) as conn:
            return _fetch_all(conn, "SELECT * FROM vendors WHERE project_id=? ORDER BY name", (project_id,))

    def list_clients(self, project_id: str) -> list[dict]:
        with get_conn(self.db_path) as conn:
            return _fetch_all(conn, "SELECT * FROM clients WHERE project_id=? ORDER BY name", (project_id,))

    # ------------------------------------------------------------------
    # Accounts payable
    # ------------------------------------------------------------------

    def create_ap_invoice(self, project_id: str, vendor_id: str, amount: float,
                           invoice_number: str = "", account_code: str = "5100",
                           issue_date: str = "", due_date: str = "", notes: str = "") -> dict:
        if amount <= 0:
            raise ValueError("Invoice amount must be positive.")
        invoice_id = str(uuid.uuid4())
        with get_conn(self.db_path) as conn:
            self._ensure_project(conn, project_id)
            vendor = conn.execute("SELECT id FROM vendors WHERE id=?", (vendor_id,)).fetchone()
            if vendor is None:
                raise ValueError(f"Unknown vendor: {vendor_id}")
            conn.execute(
                """INSERT INTO ap_invoices
                   (id, project_id, vendor_id, invoice_number, account_code, amount,
                    amount_paid, status, issue_date, due_date, notes)
                   VALUES (?, ?, ?, ?, ?, ?, 0.0, 'pending', ?, ?, ?)""",
                (invoice_id, project_id, vendor_id, invoice_number, account_code,
                 amount, issue_date, due_date, notes),
            )
        return {"id": invoice_id, "project_id": project_id, "vendor_id": vendor_id, "amount": amount}

    def create_ar_invoice(self, project_id: str, client_id: str, amount: float,
                           invoice_number: str = "", account_code: str = "4000",
                           issue_date: str = "", due_date: str = "", notes: str = "") -> dict:
        if amount <= 0:
            raise ValueError("Invoice amount must be positive.")
        invoice_id = str(uuid.uuid4())
        with get_conn(self.db_path) as conn:
            self._ensure_project(conn, project_id)
            client = conn.execute("SELECT id FROM clients WHERE id=?", (client_id,)).fetchone()
            if client is None:
                raise ValueError(f"Unknown client: {client_id}")
            conn.execute(
                """INSERT INTO ar_invoices
                   (id, project_id, client_id, invoice_number, account_code, amount,
                    amount_received, status, issue_date, due_date, notes)
                   VALUES (?, ?, ?, ?, ?, ?, 0.0, 'pending', ?, ?, ?)""",
                (invoice_id, project_id, client_id, invoice_number, account_code,
                 amount, issue_date, due_date, notes),
            )
        return {"id": invoice_id, "project_id": project_id, "client_id": client_id, "amount": amount}

    def record_payment(self, project_id: str, invoice_id: str, invoice_kind: str,
                        amount: float, paid_date: str = "", method: str = "", notes: str = "") -> dict:
        if invoice_kind not in ("ap", "ar"):
            raise ValueError("invoice_kind must be 'ap' or 'ar'")
        if amount <= 0:
            raise ValueError("Payment amount must be positive.")
        payment_id = str(uuid.uuid4())
        table = "ap_invoices" if invoice_kind == "ap" else "ar_invoices"
        paid_column = "amount_paid" if invoice_kind == "ap" else "amount_received"
        with get_conn(self.db_path) as conn:
            row = conn.execute(f"SELECT * FROM {table} WHERE id=?", (invoice_id,)).fetchone()
            if row is None:
                raise ValueError(f"Unknown {invoice_kind} invoice: {invoice_id}")
            conn.execute(
                """INSERT INTO payments (id, project_id, invoice_id, invoice_kind, amount, paid_date, method, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (payment_id, project_id, invoice_id, invoice_kind, amount, paid_date, method, notes),
            )
            new_paid = float(row[paid_column] or 0.0) + amount
            status = "paid" if new_paid >= float(row["amount"]) else "partial"
            conn.execute(
                f"UPDATE {table} SET {paid_column}=?, status=? WHERE id=?",
                (new_paid, status, invoice_id),
            )
        return {"id": payment_id, "invoice_id": invoice_id, "amount": amount, "status": status}

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def ap_aging_report(self, project_id: str, as_of: str | None = None) -> dict:
        today = as_of or date.today().isoformat()
        with get_conn(self.db_path) as conn:
            invoices = _fetch_all(
                conn,
                """SELECT ap.*, v.name AS vendor_name FROM ap_invoices ap
                   LEFT JOIN vendors v ON v.id = ap.vendor_id
                   WHERE ap.project_id=? ORDER BY ap.due_date""",
                (project_id,),
            )
        outstanding = [
            {
                **inv,
                "balance": round(float(inv["amount"]) - float(inv["amount_paid"]), 2),
                "overdue": bool(inv["due_date"]) and inv["due_date"] < today,
            }
            for inv in invoices
            if inv["status"] != "paid"
        ]
        return {
            "project_id": project_id,
            "as_of": today,
            "total_invoiced": round(sum(float(i["amount"]) for i in invoices), 2),
            "total_paid": round(sum(float(i["amount_paid"]) for i in invoices), 2),
            "total_outstanding": round(sum(i["balance"] for i in outstanding), 2),
            "total_overdue": round(sum(i["balance"] for i in outstanding if i["overdue"]), 2),
            "overdue_count": sum(1 for i in outstanding if i["overdue"]),
            "outstanding_invoices": outstanding,
        }

    def ar_aging_report(self, project_id: str, as_of: str | None = None) -> dict:
        today = as_of or date.today().isoformat()
        with get_conn(self.db_path) as conn:
            invoices = _fetch_all(
                conn,
                """SELECT ar.*, c.name AS client_name FROM ar_invoices ar
                   LEFT JOIN clients c ON c.id = ar.client_id
                   WHERE ar.project_id=? ORDER BY ar.due_date""",
                (project_id,),
            )
        outstanding = [
            {
                **inv,
                "balance": round(float(inv["amount"]) - float(inv["amount_received"]), 2),
                "overdue": bool(inv["due_date"]) and inv["due_date"] < today,
            }
            for inv in invoices
            if inv["status"] != "paid"
        ]
        return {
            "project_id": project_id,
            "as_of": today,
            "total_invoiced": round(sum(float(i["amount"]) for i in invoices), 2),
            "total_received": round(sum(float(i["amount_received"]) for i in invoices), 2),
            "total_outstanding": round(sum(i["balance"] for i in outstanding), 2),
            "total_overdue": round(sum(i["balance"] for i in outstanding if i["overdue"]), 2),
            "overdue_count": sum(1 for i in outstanding if i["overdue"]),
            "outstanding_invoices": outstanding,
        }

    def accounting_dashboard(self, project_id: str) -> dict:
        ap = self.ap_aging_report(project_id)
        ar = self.ar_aging_report(project_id)
        with get_conn(self.db_path) as conn:
            budget_lines = _fetch_all(
                conn, "SELECT * FROM budget_lines WHERE project_id=?", (project_id,)
            )
        budgeted = round(sum(float(b["budgeted"]) for b in budget_lines), 2)
        actual = round(sum(float(b["actual"]) for b in budget_lines), 2)
        net_cash_position = round(ar["total_received"] - ap["total_paid"], 2)
        return {
            "project_id": project_id,
            "accounts_payable": ap,
            "accounts_receivable": ar,
            "budgeted": budgeted,
            "actual_spend": actual,
            "cash_on_hand_estimate": net_cash_position,
            "chart_of_accounts_size": len(self.chart_of_accounts(project_id)),
        }

    def export_general_ledger_csv(self, project_id: str) -> str:
        """Export AP/AR activity as a GnuCash/ledger-cli-importable CSV."""
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["date", "account_code", "description", "debit", "credit"])
        with get_conn(self.db_path) as conn:
            ap_rows = _fetch_all(conn, "SELECT * FROM ap_invoices WHERE project_id=?", (project_id,))
            ar_rows = _fetch_all(conn, "SELECT * FROM ar_invoices WHERE project_id=?", (project_id,))
        for row in ap_rows:
            writer.writerow([row["issue_date"] or "", row["account_code"], row["invoice_number"] or row["id"],
                              f"{float(row['amount']):.2f}", ""])
        for row in ar_rows:
            writer.writerow([row["issue_date"] or "", row["account_code"], row["invoice_number"] or row["id"],
                              "", f"{float(row['amount']):.2f}"])
        return buf.getvalue()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _ensure_project(self, conn, project_id: str) -> None:
        conn.execute(
            """INSERT OR IGNORE INTO projects
               (id, title, format, stage, logline, status, shoot_days, target_day_hours, contingency_pct)
               VALUES (?, ?, 'feature', 'prep', '', 'active', 0, 10.0, 12.0)""",
            (project_id, project_id),
        )


def _fetch_all(conn, query: str, params: tuple = ()) -> list[dict]:
    return [dict(r) for r in conn.execute(query, params).fetchall()]
