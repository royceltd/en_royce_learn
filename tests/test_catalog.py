import copy
import unittest

from royce_learn.catalog import load_catalog, permitted, search_guides, validate_catalog


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_catalog()

    def test_search_matches_written_instructions_and_keywords(self):
        results = search_guides(self.catalog["guides"], "allocated amount")
        self.assertIn("receive-payment", [g["id"] for g in results])
        self.assertEqual(
            [g["id"] for g in search_guides(self.catalog["guides"], "product", doctype="Item")], ["items"]
        )

    def test_required_apps_and_permissions_both_gate_content(self):
        payroll = next(g for g in self.catalog["guides"] if g["id"] == "payroll-getting-started")
        self.assertFalse(permitted(payroll, ["erpnext"], lambda *args: True))
        self.assertFalse(permitted(payroll, payroll["required_apps"], lambda *args: False))
        self.assertTrue(permitted(payroll, payroll["required_apps"], lambda *args: True))

    def test_duplicate_ids_and_unknown_path_references_are_rejected(self):
        invalid = copy.deepcopy(self.catalog)
        invalid["guides"].append(invalid["guides"][0])
        with self.assertRaises(ValueError):
            validate_catalog(invalid)
        invalid = copy.deepcopy(self.catalog)
        invalid["paths"][0]["guides"].append("missing-guide")
        with self.assertRaises(ValueError):
            validate_catalog(invalid)

    def test_arbitrary_video_urls_are_rejected(self):
        invalid = copy.deepcopy(self.catalog)
        invalid["guides"][0]["video_id"] = "https://example.invalid/video"
        with self.assertRaises(ValueError):
            validate_catalog(invalid)


if __name__ == "__main__":
    unittest.main()
