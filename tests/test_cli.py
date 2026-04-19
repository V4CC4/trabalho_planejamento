from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_cli_reports_enumeration_indices(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")

        completed = subprocess.run(
            [sys.executable, "-m", "pse_confiabilidade", "run", "--method", "enumeration"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertIn("Method", completed.stdout)
        self.assertIn("LOLP", completed.stdout)
        self.assertIn("enumeration", completed.stdout)

    def test_cli_reports_smc_metadata_and_comparison(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")

        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "pse_confiabilidade",
                "run",
                "--method",
                "both",
                "--seed",
                "42",
                "--min-samples",
                "20000",
                "--batch-size",
                "5000",
                "--max-samples",
                "200000",
            ],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertIn("smc", completed.stdout)
        self.assertIn("samples", completed.stdout)
        self.assertIn("cv_lolp", completed.stdout)
        self.assertIn("cv_lole", completed.stdout)
        self.assertIn("cv_epns", completed.stdout)
        self.assertIn("cv_eens", completed.stdout)
        self.assertIn("Absolute error", completed.stdout)
        self.assertIn("Relative error", completed.stdout)


if __name__ == "__main__":
    unittest.main()
