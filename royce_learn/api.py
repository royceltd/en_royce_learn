import hashlib

import frappe
from frappe import _
from frappe.utils import now_datetime

from royce_learn import onboarding
from royce_learn.access import allowed_guides, get_guide, require_user
from royce_learn.catalog import load_catalog, search_guides


def _progress_name(user, guide):
    return hashlib.sha256(f"{user}\0{guide}".encode()).hexdigest()


def _progress():
    user = require_user()
    rows = frappe.get_all(
        "Royce Learn Progress",
        filters={"user": user},
        fields=["guide", "status", "completed_version", "modified"],
    )
    return {r.guide: dict(r) for r in rows}


def _summary(guide, progress):
    result = {k: guide.get(k) for k in ("id", "title", "summary", "category", "doctype", "minutes")}
    saved = progress.get(guide["id"], {})
    result.update(
        {
            "status": saved.get("status", "Not Started"),
            "version": guide["version"],
            "updated_since_completion": bool(
                saved.get("completed_version") and saved["completed_version"] != guide["version"]
            ),
        }
    )
    return result


@frappe.whitelist(methods=["GET"])
def dashboard(company=None):
    require_user()
    companies = frappe.get_list("Company", fields=["name"], order_by="name", limit_page_length=0)
    names = [c.name for c in companies]
    selected = company or (names[0] if names else None)
    if selected and selected not in names:
        frappe.throw(_("Company unavailable or access denied."), frappe.PermissionError)
    guides = allowed_guides()
    progress = _progress()
    paths = []
    visible = {g["id"] for g in guides}
    for path in load_catalog()["paths"]:
        keys = [key for key in path["guides"] if key in visible]
        if keys:
            paths.append(
                {
                    **path,
                    "guides": keys,
                    "completed": sum(progress.get(k, {}).get("status") == "Completed" for k in keys),
                    "total": len(keys),
                }
            )
    return {
        "companies": names,
        "company": selected,
        "setup": onboarding.get_setup(selected) if selected else None,
        "learning": {
            "completed": sum(progress.get(g["id"], {}).get("status") == "Completed" for g in guides),
            "total": len(guides),
        },
        "paths": paths,
        "guides": [_summary(g, progress) for g in guides],
    }


@frappe.whitelist(methods=["GET"])
def guides(query="", category="", doctype=""):
    require_user()
    if len(query) > 200:
        frappe.throw(_("Search must be 200 characters or fewer."))
    progress = _progress()
    return [_summary(g, progress) for g in search_guides(allowed_guides(), query, category, doctype)]


@frappe.whitelist(methods=["GET"])
def guide(guide_id):
    item = get_guide(guide_id)
    # Rendering is text-only in the client. Raw HTML and arbitrary URLs are never injected.
    return {**item, **_summary(item, _progress())}


@frappe.whitelist(methods=["POST"])
def mark_learning(guide_id, status):
    user = require_user()
    item = get_guide(guide_id)
    if status not in ("In Progress", "Completed"):
        frappe.throw(_("Invalid learning status."))
    name = _progress_name(user, guide_id)
    completed = now_datetime() if status == "Completed" else None
    version = item["version"] if completed else None
    frappe.db.sql(
        """INSERT INTO `tabRoyce Learn Progress`
        (name, creation, modified, owner, modified_by, docstatus, idx,
         user, guide, status, completed_at, completed_version)
        VALUES (%s, NOW(), NOW(), %s, %s, 0, 0, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        completed_at=IF(VALUES(status)='Completed', VALUES(completed_at), completed_at),
        completed_version=IF(VALUES(status)='Completed', VALUES(completed_version), completed_version),
        status=IF(status='Completed', 'Completed', VALUES(status)), modified=NOW()""",
        (name, user, user, user, guide_id, status, completed, version),
    )
    return _summary(item, _progress())


@frappe.whitelist(methods=["POST"])
def confirm_setup(company, step_id, status, note=""):
    return onboarding.confirm(company, step_id, status, note)
