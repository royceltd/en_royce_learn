"""build_assets.py and the committed metadata it generates must never drift apart."""

import runpy
import shutil
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CRLF, LF = bytes([13, 10]), bytes([10])


class GeneratedAssetsTests(unittest.TestCase):
    def test_generator_output_matches_committed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "build_assets.py"
            shutil.copy(REPO / "build_assets.py", script)
            runpy.run_path(str(script), run_name="__main__")

            generated = [p for p in Path(tmp, "royce_learn").rglob("*") if p.is_file()]
            self.assertTrue(generated, "build_assets.py wrote nothing")
            for path in generated:
                rel = path.relative_to(tmp)
                committed = REPO / rel
                with self.subTest(file=str(rel)):
                    self.assertTrue(committed.exists(), f"{rel} is generated but not committed")
                    # Line endings aside: a Windows checkout (core.autocrlf) is still the same file.
                    self.assertEqual(
                        path.read_bytes().replace(CRLF, LF),
                        committed.read_bytes().replace(CRLF, LF),
                        f"{rel} differs from build_assets.py's output: edit the generator and "
                        "re-run it, never the generated file",
                    )

    def test_generator_does_not_touch_the_guide_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "build_assets.py"
            shutil.copy(REPO / "build_assets.py", script)
            runpy.run_path(str(script), run_name="__main__")
            self.assertFalse(Path(tmp, "royce_learn", "content", "catalog.json").exists())


if __name__ == "__main__":
    unittest.main()
