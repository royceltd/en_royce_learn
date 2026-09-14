"""Fast permission/evidence tests. Real DB integration tests are separate."""

import importlib
import sys
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch


class AttrDict(dict):
    __getattr__ = dict.__getitem__


def fake_frappe():
    module = ModuleType("frappe")
    module._ = lambda message: message
    module.PermissionError = PermissionError
    module.session = SimpleNamespace(user="owner@example.com")
    module.db = Mock()
    module.db.get_value.return_value = "System User"
    module.has_permission = Mock(return_value=True)
    module.get_installed_apps = Mock(return_value=["erpnext"])
    module.get_list = Mock(return_value=[])
    module.get_doc = Mock(
        return_value=SimpleNamespace(check_permission=Mock(), has_permission=Mock(return_value=True))
    )
    module.whitelist = lambda **kwargs: lambda function: function

    def throw(message, exc=ValueError):
        raise exc(message)

    module.throw = throw
    utils = ModuleType("frappe.utils")
    utils.now_datetime = Mock(return_value="2026-09-14 12:00:00")
    return module, utils


class AccessTests(unittest.TestCase):
    def setUp(self):
        self.frappe, utils = fake_frappe()
        self.modules = patch.dict(sys.modules, {"frappe": self.frappe, "frappe.utils": utils})
        self.modules.start()
        for key in (
            "royce_learn.access",
            "royce_learn.onboarding",
            "royce_learn.permissions",
            "royce_learn.api",
        ):
            sys.modules.pop(key, None)
        self.access = importlib.import_module("royce_learn.access")
        self.onboarding = importlib.import_module("royce_learn.onboarding")
        self.permissions = importlib.import_module("royce_learn.permissions")

    def tearDown(self):
        for key in (
            "royce_learn.access",
            "royce_learn.onboarding",
            "royce_learn.permissions",
            "royce_learn.api",
        ):
            sys.modules.pop(key, None)
        self.modules.stop()

    def test_guests_and_website_users_cannot_use_learn(self):
        self.frappe.session.user = "Guest"
        with self.assertRaises(PermissionError):
            self.access.require_user()
        self.frappe.session.user = "web@example.com"
        self.frappe.db.get_value.return_value = "Website User"
        with self.assertRaises(PermissionError):
            self.access.require_user()

    def test_direct_guide_lookup_checks_apps_and_permissions(self):
        with self.assertRaises(PermissionError):
            self.access.get_guide("payroll-getting-started")
        self.frappe.has_permission.return_value = False
        with self.assertRaises(PermissionError):
            self.access.get_guide("sales-invoice")

    def test_generic_rest_writes_and_other_users_progress_are_denied(self):
        own = SimpleNamespace(user=self.frappe.session.user)
        other = SimpleNamespace(user="other@example.com")
        self.assertTrue(self.permissions.progress_permission(own, ptype="read"))
        self.assertFalse(self.permissions.progress_permission(own, ptype="write"))
        self.assertFalse(self.permissions.progress_permission(other, ptype="read"))
        guide = SimpleNamespace(name="sales-invoice")
        self.assertFalse(self.permissions.guide_permission(guide, ptype="write"))

    def test_setup_keys_are_company_scoped(self):
        self.assertNotEqual(
            self.onboarding.record_name("A", "team"), self.onboarding.record_name("B", "team")
        )

    def test_invoice_requires_submission_company_and_non_return(self):
        self.onboarding.invoice_evidence("A")
        args = self.frappe.get_list.call_args.kwargs
        self.assertEqual(args["filters"], {"company": "A", "docstatus": 1, "is_return": 0})

    def test_payments_require_positive_invoice_allocation(self):
        self.onboarding.payment_evidence("B")
        filters = self.frappe.get_list.call_args.kwargs["filters"]
        self.assertIn(["Payment Entry", "company", "=", "B"], filters)
        self.assertIn(["Payment Entry Reference", "allocated_amount", ">", 0], filters)
        self.assertIn(["Payment Entry Reference", "reference_doctype", "=", "Sales Invoice"], filters)

    def test_evidence_steps_cannot_be_manually_completed(self):
        with self.assertRaises(PermissionError):
            self.onboarding.confirm("A", "first-invoice", "Complete")
        self.frappe.db.sql.assert_not_called()

    def test_only_optional_steps_allow_not_applicable_with_reason(self):
        with self.assertRaises(ValueError):
            self.onboarding.confirm("A", "team", "Not Applicable", "No staff")
        with self.assertRaises(ValueError):
            self.onboarding.confirm("A", "opening-balances", "Not Applicable", "")
        self.frappe.db.sql.assert_not_called()

    def test_company_write_check_precedes_confirmation(self):
        self.frappe.get_doc.return_value.check_permission.side_effect = PermissionError
        with self.assertRaises(PermissionError):
            self.onboarding.confirm("Restricted", "team", "Complete")
        self.frappe.db.sql.assert_not_called()

    def test_learning_only_targets_authenticated_user(self):
        api = importlib.import_module("royce_learn.api")
        self.frappe.get_all = Mock(return_value=[])
        api.mark_learning("sales-invoice", "Completed")
        parameters = self.frappe.db.sql.call_args.args[1]
        self.assertEqual(parameters[3], "owner@example.com")
        self.assertEqual(parameters[4], "sales-invoice")


if __name__ == "__main__":
    unittest.main()
