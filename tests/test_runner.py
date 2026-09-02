import unittest
import json
import os

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICT_PATH = os.path.join(REPO_DIR, "dist", "zh-CN.json")

class TestClaudeChinesePatch(unittest.TestCase):
    def test_01_dictionary_exists_and_valid_json(self):
        self.assertTrue(os.path.exists(DICT_PATH), "dist/zh-CN.json must exist")
        with open(DICT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)
        self.assertGreaterEqual(len(data), 15000, "Dictionary should have at least 15,000 keys")

    def test_02_no_mojibake_or_corrupted_characters(self):
        with open(DICT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in list(data.items())[:500]:
            self.assertNotIn("�", v, f"Found replacement char in key: {k}")

    def test_03_installer_scripts_exist(self):
        self.assertTrue(os.path.exists(os.path.join(REPO_DIR, "install.ps1")))
        self.assertTrue(os.path.exists(os.path.join(REPO_DIR, "install.sh")))
        self.assertTrue(os.path.exists(os.path.join(REPO_DIR, "patch_claude.ps1")))
        self.assertTrue(os.path.exists(os.path.join(REPO_DIR, "watcher", "watcher.ps1")))

if __name__ == "__main__":
    unittest.main()
