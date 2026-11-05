import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "ig-unfollow-check" / "scripts" / "analyze.py"


def followers(names):
    return [{"title": "", "string_list_data": [{"href": f"https://www.instagram.com/{n}", "value": n, "timestamp": 1}]} for n in names]


def following(names):
    return {"relationships_following": [{"title": n, "string_list_data": [{"href": f"https://www.instagram.com/_u/{n}", "timestamp": 1}]} for n in names]}


def make_export(root, fl, fg):
    root.mkdir(parents=True)
    (root / "followers_1.json").write_text(json.dumps(followers(fl)))
    (root / "following.json").write_text(json.dumps(following(fg)))


def run(export, state, *extra):
    out = subprocess.run([sys.executable, str(SCRIPT), str(export), "--state-dir", str(state), "--json", *extra],
                         capture_output=True, text=True, encoding="utf-8")
    return out, (json.loads(out.stdout) if out.returncode == 0 else None)


class AnalyzeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.state = self.tmp / "state"

    def test_not_following_back_and_keep_list(self):
        make_export(self.tmp / "e1", ["amy", "bob"], ["amy", "eve", "Brand"])
        self.state.mkdir()
        (self.state / "keep.txt").write_text("# comment\n@brand\n")
        _, r = run(self.tmp / "e1", self.state)
        self.assertEqual(r["not_following_back"], ["eve"])
        self.assertEqual(r["counts"]["kept_excluded"], 1)
        self.assertIsNone(r["since"])

    def test_diff_against_previous_snapshot(self):
        make_export(self.tmp / "e1", ["amy", "bob", "dan"], ["amy"])
        make_export(self.tmp / "e2", ["amy", "fay"], ["amy"])
        run(self.tmp / "e1", self.state)
        import time
        time.sleep(1.1)  # snapshot filenames have 1s resolution
        _, r = run(self.tmp / "e2", self.state)
        self.assertEqual(r["new_unfollowers"], ["bob", "dan"])
        self.assertEqual(r["new_followers"], ["fay"])

    def test_no_save_leaves_no_snapshot(self):
        make_export(self.tmp / "e1", ["amy"], ["amy"])
        run(self.tmp / "e1", self.state, "--no-save")
        self.assertEqual(list((self.state / "snapshots").glob("*.json")), [])

    def test_missing_files_errors(self):
        (self.tmp / "empty").mkdir()
        out, _ = run(self.tmp / "empty", self.state)
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("JSON", out.stderr)


if __name__ == "__main__":
    unittest.main()
