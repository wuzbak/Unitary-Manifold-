"""Tests for the accounting module: chart of accounts, AP/AR, payments."""
from __future__ import annotations

import pytest

from desktop.app.accounting.service import AccountingService
from desktop.app.config import get_config


@pytest.fixture
def svc():
    from desktop.app.db.schema import init_db
    cfg = get_config()
    init_db(cfg.db_path)
    return AccountingService(cfg.db_path)


def test_seed_default_chart_of_accounts(svc):
    accounts = svc.seed_default_chart_of_accounts("proj-1")
    assert len(accounts) == 10
    codes = {a["code"] for a in accounts}
    assert "1000" in codes and "5100" in codes

    # Idempotent: seeding twice does not duplicate.
    accounts_again = svc.seed_default_chart_of_accounts("proj-1")
    assert len(accounts_again) == 10


def test_vendor_ap_invoice_and_payment_flow(svc):
    vendor = svc.create_vendor("proj-1", "Acme Grip & Electric", category="G&E")
    invoice = svc.create_ap_invoice(
        "proj-1", vendor["id"], amount=1000.0, invoice_number="INV-001", due_date="2026-11-01"
    )

    aging_before = svc.ap_aging_report("proj-1")
    assert aging_before["total_outstanding"] == 1000.0

    payment = svc.record_payment("proj-1", invoice["id"], "ap", amount=400.0)
    assert payment["status"] == "partial"

    aging_partial = svc.ap_aging_report("proj-1")
    assert aging_partial["total_outstanding"] == 600.0

    final_payment = svc.record_payment("proj-1", invoice["id"], "ap", amount=600.0)
    assert final_payment["status"] == "paid"

    aging_final = svc.ap_aging_report("proj-1")
    assert aging_final["total_outstanding"] == 0.0


def test_client_ar_invoice_and_payment_flow(svc):
    client = svc.create_client("proj-1", "Streaming Distributor LLC")
    invoice = svc.create_ar_invoice("proj-1", client["id"], amount=5000.0, invoice_number="AR-001")

    svc.record_payment("proj-1", invoice["id"], "ar", amount=5000.0)
    aging = svc.ar_aging_report("proj-1")
    assert aging["total_received"] == 5000.0
    assert aging["total_outstanding"] == 0.0


def test_record_payment_rejects_invalid_kind(svc):
    vendor = svc.create_vendor("proj-1", "Acme")
    invoice = svc.create_ap_invoice("proj-1", vendor["id"], amount=100.0)
    with pytest.raises(ValueError):
        svc.record_payment("proj-1", invoice["id"], "gl", amount=10.0)


def test_record_payment_rejects_unknown_invoice(svc):
    with pytest.raises(ValueError):
        svc.record_payment("proj-1", "does-not-exist", "ap", amount=10.0)


def test_accounting_dashboard_aggregates(svc):
    svc.seed_default_chart_of_accounts("proj-1")
    vendor = svc.create_vendor("proj-1", "Acme")
    client = svc.create_client("proj-1", "Buyer Co")
    ap_invoice = svc.create_ap_invoice("proj-1", vendor["id"], amount=200.0)
    ar_invoice = svc.create_ar_invoice("proj-1", client["id"], amount=300.0)
    svc.record_payment("proj-1", ap_invoice["id"], "ap", amount=200.0)
    svc.record_payment("proj-1", ar_invoice["id"], "ar", amount=300.0)

    dashboard = svc.accounting_dashboard("proj-1")
    assert dashboard["cash_on_hand_estimate"] == 100.0
    assert dashboard["chart_of_accounts_size"] == 10


def test_export_general_ledger_csv_contains_invoice_rows(svc):
    vendor = svc.create_vendor("proj-1", "Acme")
    svc.create_ap_invoice("proj-1", vendor["id"], amount=150.0, invoice_number="INV-010")
    csv_text = svc.export_general_ledger_csv("proj-1")
    assert "INV-010" in csv_text
    assert "150.00" in csv_text
