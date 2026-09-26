"""Run only on a disposable v16 staging/test site with allow_tests enabled."""

import frappe
from frappe.tests import IntegrationTestCase

from royce_learn.api import mark_learning
from royce_learn.install import sync_content
from royce_learn.onboarding import confirm, get_setup


class TestLearning(IntegrationTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        sync_content()

    def tearDown(self):
        frappe.set_user("Administrator")

    def test_sync_keeps_ids_and_learning_progress(self):
        mark_learning("sales-invoice", "Completed")
        sync_content()
        self.assertTrue(frappe.db.exists("Learning Guide", "sales-invoice"))
        self.assertEqual(
            frappe.db.get_value(
                "Learning Progress", {"user": "Administrator", "guide": "sales-invoice"}, "status"
            ),
            "Completed",
        )
        mark_learning("sales-invoice", "In Progress")
        self.assertEqual(
            frappe.db.get_value(
                "Learning Progress", {"user": "Administrator", "guide": "sales-invoice"}, "status"
            ),
            "Completed",
        )

    def test_confirm_is_repeatable_and_company_scoped(self):
        companies = frappe.get_all("Company", pluck="name", limit_page_length=2)
        if len(companies) < 2:
            self.skipTest("Create two companies on the staging test site")
        confirm(companies[0], "team", "Complete")
        confirm(companies[0], "team", "Complete")
        a = next(s for s in get_setup(companies[0])["steps"] if s["id"] == "team")
        b = next(s for s in get_setup(companies[1])["steps"] if s["id"] == "team")
        self.assertEqual(a["status"], "Complete")
        self.assertEqual(b["status"], "Pending")

    def test_guest_is_denied(self):
        frappe.set_user("Guest")
        with self.assertRaises(frappe.PermissionError):
            mark_learning("sales-invoice", "Completed")
