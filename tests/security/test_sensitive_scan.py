"""Sensitive scan uses git ls-files and includes docs/archive."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


class SensitiveScanGitFilesTests(unittest.TestCase):
    def test_git_ls_files_includes_archive(self) -> None:
        repo = Path(__file__).resolve().parents[2]
        files = subprocess.check_output(["git", "ls-files"], cwd=repo, text=True).splitlines()
        self.assertTrue(any(f.startswith("docs/archive/") for f in files))

    def test_scan_repository_passes_on_repo(self) -> None:
        repo = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            [sys.executable, str(repo / "security" / "precommit_sensitive_scan.py")],
            cwd=repo,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
