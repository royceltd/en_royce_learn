import frappe
from frappe import _

from royce_learn.catalog import load_catalog


def before_install():
    from erpnext import __version__ as erpnext_version
    from frappe import __version__ as frappe_version

    if any(v.split(".")[0] != "16" for v in (frappe_version, erpnext_version)):
        frappe.throw(_("Learning requires Frappe and ERPNext version 16."))


def sync_content():
    """Idempotent reconciliation. Never resets progress or touches ERP masters."""
    catalog = load_catalog()
    active = []
    for guide in catalog["guides"]:
        active.append(guide["id"])
        values = {
            "title": guide["title"],
            "summary": guide["summary"],
            "category": guide["category"],
            "content_version": guide["version"],
            "body": guide["body"],
            "video_id": guide.get("video_id", ""),
            "reference_doctype": guide.get("doctype", ""),
            "required_apps": "\n".join(guide.get("required_apps", [])),
            "keywords": " ".join(guide.get("keywords", [])),
            "published": 1,
        }
        if frappe.db.exists("Learning Guide", guide["id"]):
            frappe.db.set_value("Learning Guide", guide["id"], values)
        else:
            frappe.get_doc({"doctype": "Learning Guide", "name": guide["id"], **values}).insert(
                ignore_permissions=True, set_name=guide["id"]
            )
    # Retire rather than delete, keeping linked history intact.
    for name in frappe.get_all("Learning Guide", pluck="name"):
        if name not in active:
            frappe.db.set_value("Learning Guide", name, "published", 0)
