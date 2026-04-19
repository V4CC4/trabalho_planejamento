from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pse_confiabilidade import build_default_case, enumerate_indices


class EnumerationTests(unittest.TestCase):
    def test_enumeration_matches_reference_indices(self) -> None:
        case = build_default_case()

        indices = enumerate_indices(case)

        self.assertTrue(math.isclose(indices.lolp, 0.12336303665406873, rel_tol=0.0, abs_tol=1e-12))
        self.assertTrue(math.isclose(indices.lole_hours_per_year, 1080.660201089642, rel_tol=0.0, abs_tol=1e-9))
        self.assertTrue(math.isclose(indices.epns_mw, 27.58385848141273, rel_tol=0.0, abs_tol=1e-9))
        self.assertTrue(math.isclose(indices.eens_mwh_per_year, 241634.60029717552, rel_tol=0.0, abs_tol=1e-6))

    def test_enumeration_preserves_index_identities(self) -> None:
        case = build_default_case()

        indices = enumerate_indices(case)

        self.assertTrue(math.isclose(indices.lole_hours_per_year, 8760.0 * indices.lolp))
        self.assertTrue(math.isclose(indices.eens_mwh_per_year, 8760.0 * indices.epns_mw))


if __name__ == "__main__":
    unittest.main()
