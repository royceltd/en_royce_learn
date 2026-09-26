"""Company-specific evidence checks; shared masters require explicit confirmation."""

import hashlib

import frappe
from frappe import _
from frappe.utils import now_datetime

from royce_learn.access import can, require_company, require_user

STEPS = [
    {
        "id": "company-details",
        "label": "Confirm company details",
        "guide": "company-details",
        "doctype": "Company",
        "mode": "confirm",
    },
    {
        "id": "team",
        "label": "Review users and roles",
        "guide": "users-and-roles",
        "doctype": "User",
        "mode": "confirm",
    },
    {
        "id": "items",
        "label": "Add products or services",
        "guide": "items",
        "doctype": "Item",
        "mode": "confirm",
    },
    {
        "id": "customers",
        "label": "Add customers",
        "guide": "customers",
        "doctype": "Customer",
        "mode": "confirm",
    },
    {
        "id": "opening-balances",
        "label": "Review opening balances",
        "guide": "opening-balances",
        "doctype": "Journal Entry",
        "mode": "confirm",
        "optional": True,
    },
    {
        "id": "first-invoice",
        "label": "Submit the first sales invoice",
        "guide": "sales-invoice",
        "doctype": "Sales Invoice",
        "mode": "evidence",
    },
    {
        "id": "first-payment",
        "label": "Receive payment against an invoice",
        "guide": "receive-payment",
        "doctype": "Payment Entry",
        "mode": "evidence",
    },
]


def record_name(company, step):
    return hashlib.sha256(f"{company}\0{step}".encode()).hexdigest()


def available_steps():
    return [step for step in STEPS if can(step["doctype"])]


def invoice_evidence(company):
    rows = frappe.get_list(
        "Sales Invoice",
        filters={"company": company, "docstatus": 1, "is_return": 0},
        fields=["name"],
        limit_page_length=1,
    )
    return rows[0]["name"] if rows else None


def payment_evidence(company):
    # Child-table joins through get_list retain Payment Entry permissions.
    rows = frappe.get_list(
        "Payment Entry",
        filters=[
            ["Payment Entry", "company", "=", company],
            ["Payment Entry", "docstatus", "=", 1],
            ["Payment Entry", "payment_type", "=", "Receive"],
            ["Payment Entry", "party_type", "=", "Customer"],
            ["Payment Entry Reference", "reference_doctype", "=", "Sales Invoice"],
            ["Payment Entry Reference", "allocated_amount", ">", 0],
        ],
        fields=["name"],
        limit_page_length=1,
    )
    return rows[0]["name"] if rows else None


def get_setup(company):
    doc = require_company(company)
    result = []
    for step in available_steps():
        evidence = None
        saved = None
        if step["mode"] == "evidence":
            evidence = (
                invoice_evidence(company) if step["id"] == "first-invoice" else payment_evidence(company)
            )
            status = "Complete" if evidence else "Pending"
        else:
            saved = frappe.db.get_value(
                "Learning Setup Task",
                record_name(company, step["id"]),
                ["status", "confirmed_by", "confirmed_at", "note"],
                as_dict=True,
            )
            status = saved.status if saved else "Pending"
        result.append({**step, "status": status, "evidence": evidence, "confirmation": saved})
    # Visible progress intentionally describes tasks accessible to the current user.
    complete = sum(s["status"] in ("Complete", "Not Applicable") for s in result)
    return {
        "company": company,
        "can_confirm": bool(doc.has_permission("write")),
        "steps": result,
        "completed": complete,
        "total": len(result),
        "percent": round(100 * complete / len(result)) if result else 0,
        "progress_scope": "Tasks visible to your permissions",
    }


def confirm(company, step_id, status, note=""):
    user = require_user()
    require_company(company, write=True)
    step = next((s for s in available_steps() if s["id"] == step_id), None)
    if not step or step["mode"] != "confirm":
        frappe.throw(_("This task requires ERP evidence or is unavailable."), frappe.PermissionError)
    if status not in ("Pending", "Complete", "Not Applicable"):
        frappe.throw(_("Invalid setup status."))
    if status == "Not Applicable" and not step.get("optional"):
        frappe.throw(_("This task cannot be marked not applicable."))
    if len(note) > 1000:
        frappe.throw(_("Notes must be 1,000 characters or fewer."))
    if status == "Not Applicable" and not note.strip():
        frappe.throw(_("Explain why this task does not apply."))
    name = record_name(company, step_id)
    values = {
        "company": company,
        "step_id": step_id,
        "status": status,
        "confirmed_by": user,
        "confirmed_at": now_datetime(),
        "note": note,
    }
    # SQL upsert avoids duplicate-name races. Fields are fixed, all values parameterized.
    frappe.db.sql(
        """INSERT INTO `tabLearning Setup Task`
        (name, creation, modified, owner, modified_by, docstatus, idx,
         company, step_id, status, confirmed_by, confirmed_at, note)
        VALUES (%s, NOW(), NOW(), %s, %s, 0, 0, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE status=VALUES(status), confirmed_by=VALUES(confirmed_by),
        confirmed_at=VALUES(confirmed_at), note=VALUES(note), modified=NOW(), modified_by=VALUES(modified_by)""",
        (name, user, user, company, step_id, status, user, values["confirmed_at"], note),
    )
    return get_setup(company)
