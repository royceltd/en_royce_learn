import frappe
from frappe import _

from royce_learn.catalog import load_catalog, permitted


def require_user():
    user = frappe.session.user
    if user == "Guest" or frappe.db.get_value("User", user, "user_type") != "System User":
        frappe.throw(_("Royce Learn is available to signed-in ERP users."), frappe.PermissionError)
    return user


def can(doctype, ptype="read", user=None):
    return bool(frappe.has_permission(doctype, ptype=ptype, user=user))


def allowed_guides(user=None):
    apps = frappe.get_installed_apps()
    return [g for g in load_catalog()["guides"] if permitted(g, apps, lambda dt, pt: can(dt, pt, user))]


def get_guide(key):
    require_user()
    for guide in allowed_guides():
        if guide["id"] == key:
            return guide
    frappe.throw(_("Guide unavailable or access denied."), frappe.PermissionError)


def require_company(company, write=False):
    require_user()
    doc = frappe.get_doc("Company", company)
    doc.check_permission("write" if write else "read")
    return doc
