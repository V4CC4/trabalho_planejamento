from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pse_confiabilidade import (
    MonteCarloConfig,
    build_default_case,
    enumerate_indices,
    simulate_indices,
)


class MonteCarloTests(unittest.TestCase):
    def test_monte_carlo_converges_close_to_enumeration_with_fixed_seed(self) -> None:
        case = build_default_case()
        reference = enumerate_indices(case)
        config = MonteCarloConfig(
            seed=42,
            target_cv_epns=0.05,
            min_samples=20_000,
            batch_size=5_000,
            max_samples=200_000,
        )

        result = simulate_indices(case, config)

        self.assertEqual(result.seed, 42)
        self.assertGreaterEqual(result.samples, config.min_samples)
        self.assertLessEqual(result.cv_epns, config.target_cv_epns)
        self.assertGreaterEqual(result.cv_lolp, 0.0)
        self.assertGreaterEqual(result.cv_lole, 0.0)
        self.assertGreaterEqual(result.cv_eens, 0.0)
        self.assertLessEqual(abs(result.indices.lolp - reference.lolp), 0.01)
        self.assertLessEqual(abs(result.indices.lole_hours_per_year - reference.lole_hours_per_year), 100.0)
        self.assertLessEqual(abs(result.indices.epns_mw - reference.epns_mw), 2.0)
        self.assertLessEqual(abs(result.indices.eens_mwh_per_year - reference.eens_mwh_per_year), 20_000.0)

    def test_monte_carlo_preserves_index_identities(self) -> None:
        case = build_default_case()
        config = MonteCarloConfig(
            seed=7,
            target_cv_epns=0.05,
            min_samples=10_000,
            batch_size=2_000,
            max_samples=100_000,
        )

        result = simulate_indices(case, config)

        self.assertTrue(math.isclose(result.indices.lole_hours_per_year, 8760.0 * result.indices.lolp))
        self.assertTrue(math.isclose(result.indices.eens_mwh_per_year, 8760.0 * result.indices.epns_mw))
        self.assertTrue(math.isclose(result.cv_lole, result.cv_lolp))
        self.assertTrue(math.isclose(result.cv_eens, result.cv_epns))


if __name__ == "__main__":
    unittest.main()
