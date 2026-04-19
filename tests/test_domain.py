from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pse_confiabilidade import build_default_case
from pse_confiabilidade.domain import HOURS_PER_YEAR, state_supply_mw


class ComponentModelTests(unittest.TestCase):
    def test_component_stationary_probabilities_match_reference_case(self) -> None:
        case = build_default_case()

        generator = case.generator
        line = case.transmission_lines[0]

        self.assertTrue(math.isclose(generator.unavailability, 0.043668122270742356))
        self.assertTrue(math.isclose(generator.availability, 0.9563318777292577))
        self.assertTrue(math.isclose(line.unavailability, 0.0008212428141253765))
        self.assertTrue(math.isclose(line.availability, 0.9991787571858747))

    def test_default_case_spans_full_year(self) -> None:
        case = build_default_case()

        self.assertEqual(len(case.time_blocks), 12)
        self.assertTrue(math.isclose(case.total_hours, HOURS_PER_YEAR))


class StateAdequacyTests(unittest.TestCase):
    def test_state_supply_for_all_component_combinations(self) -> None:
        case = build_default_case()
        peak_energy_block = case.time_blocks[2]

        expected_supply = {
            (False, False, False): 0.0,
            (False, False, True): 0.0,
            (False, True, False): 0.0,
            (False, True, True): 0.0,
            (True, False, False): 0.0,
            (True, False, True): 400.0,
            (True, True, False): 400.0,
            (True, True, True): 600.0,
        }

        for states, expected in expected_supply.items():
            with self.subTest(states=states):
                generator_up, line_1_up, line_2_up = states
                supply = state_supply_mw(
                    case,
                    peak_energy_block,
                    generator_up,
                    (line_1_up, line_2_up),
                )
                self.assertEqual(supply, expected)

    def test_state_supply_is_limited_by_block_energy(self) -> None:
        case = build_default_case()
        low_energy_block = case.time_blocks[0]

        supply = state_supply_mw(case, low_energy_block, True, (True, True))

        self.assertEqual(supply, 200.0)


if __name__ == "__main__":
    unittest.main()
