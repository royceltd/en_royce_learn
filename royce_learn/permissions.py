"""Protect generic REST/list/export access as well as custom endpoints."""

import frappe

from royce_learn.access import allowed_guides


def _system_user(user):
    return user != "Guest" and frappe.db.get_value("User", user, "user_type") == "System User"


def guide_query(user=None):
    user = user or frappe.session.user
    if not _system_user(user):
        return "1=0"
    names = [frappe.db.escape(g["id"]) for g in allowed_guides(user)]
    return "`tabLearning Guide`.`name` IN (" + ",".join(names) + ")" if names else "1=0"


def guide_permission(doc, user=None, ptype="read", **kwargs):
    user = user or frappe.session.user
    if not _system_user(user) or ptype not in ("read", "select", "print", "export"):
        return False
    return doc.name in {g["id"] for g in allowed_guides(user)}


def progress_query(user=None):
    user = user or frappe.session.user
    if not _system_user(user):
        return "1=0"
    return "`tabLearning Progress`.`user` = " + frappe.db.escape(user)


def progress_permission(doc, user=None, ptype="read", **kwargs):
    user = user or frappe.session.user
    return _system_user(user) and doc.user == user and ptype in ("read", "select")


def setup_query(user=None):
    user = user or frappe.session.user
    if not _system_user(user):
        return "1=0"
    companies = frappe.get_list("Company", pluck="name", user=user, limit_page_length=0)
    names = [frappe.db.escape(c) for c in companies]
    return "`tabLearning Setup Task`.`company` IN (" + ",".join(names) + ")" if names else "1=0"


def setup_permission(doc, user=None, ptype="read", **kwargs):
    user = user or frappe.session.user
    if not _system_user(user) or ptype not in ("read", "select"):
        return False
    return frappe.has_permission("Company", "read", doc=frappe.get_doc("Company", doc.company), user=user)
