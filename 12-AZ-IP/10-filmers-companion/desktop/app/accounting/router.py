"""Accounting router — chart of accounts, AP/AR, and payments."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/accounting", tags=["accounting"])


def _service():
    from ..config import get_config
    from .service import AccountingService

    return AccountingService(get_config().db_path)


@router.get("/{project_id}/dashboard")
def dashboard(project_id: str):
    return _service().accounting_dashboard(project_id)


@router.post("/{project_id}/chart-of-accounts/seed")
def seed_chart_of_accounts(project_id: str):
    return _service().seed_default_chart_of_accounts(project_id)


@router.get("/{project_id}/chart-of-accounts")
def chart_of_accounts(project_id: str):
    return _service().chart_of_accounts(project_id)


@router.post("/vendors")
def create_vendor(body: dict):
    return _service().create_vendor(
        project_id=body.get("project_id", ""),
        name=body.get("name", ""),
        category=body.get("category", ""),
        contact=body.get("contact", ""),
        terms=body.get("terms", "Net 30"),
        tax_id=body.get("tax_id", ""),
        notes=body.get("notes", ""),
    )


@router.post("/clients")
def create_client(body: dict):
    return _service().create_client(
        project_id=body.get("project_id", ""),
        name=body.get("name", ""),
        contact=body.get("contact", ""),
        billing_address=body.get("billing_address", ""),
        notes=body.get("notes", ""),
    )


@router.post("/ap/invoices")
def create_ap_invoice(body: dict):
    try:
        return _service().create_ap_invoice(
            project_id=body.get("project_id", ""),
            vendor_id=body.get("vendor_id", ""),
            amount=float(body.get("amount", 0.0)),
            invoice_number=body.get("invoice_number", ""),
            account_code=body.get("account_code", "5100"),
            issue_date=body.get("issue_date", ""),
            due_date=body.get("due_date", ""),
            notes=body.get("notes", ""),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/ar/invoices")
def create_ar_invoice(body: dict):
    try:
        return _service().create_ar_invoice(
            project_id=body.get("project_id", ""),
            client_id=body.get("client_id", ""),
            amount=float(body.get("amount", 0.0)),
            invoice_number=body.get("invoice_number", ""),
            account_code=body.get("account_code", "4000"),
            issue_date=body.get("issue_date", ""),
            due_date=body.get("due_date", ""),
            notes=body.get("notes", ""),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/payments")
def record_payment(body: dict):
    try:
        return _service().record_payment(
            project_id=body.get("project_id", ""),
            invoice_id=body.get("invoice_id", ""),
            invoice_kind=body.get("invoice_kind", "ap"),
            amount=float(body.get("amount", 0.0)),
            paid_date=body.get("paid_date", ""),
            method=body.get("method", ""),
            notes=body.get("notes", ""),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{project_id}/ap/aging")
def ap_aging(project_id: str):
    return _service().ap_aging_report(project_id)


@router.get("/{project_id}/ar/aging")
def ar_aging(project_id: str):
    return _service().ar_aging_report(project_id)


@router.get("/{project_id}/general-ledger.csv")
def general_ledger_csv(project_id: str):
    return PlainTextResponse(_service().export_general_ledger_csv(project_id), media_type="text/csv")
