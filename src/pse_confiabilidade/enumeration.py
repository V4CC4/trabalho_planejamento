from __future__ import annotations

from itertools import product

from pse_confiabilidade.domain import HOURS_PER_YEAR, ReliabilityIndices, SystemCase, state_shed_mw


def enumerate_indices(case: SystemCase) -> ReliabilityIndices:
    lolp = 0.0
    epns = 0.0
    line_count = len(case.transmission_lines)

    for generator_up, *line_states in product((False, True), repeat=1 + line_count):
        line_states_up = tuple(line_states)
        state_probability = _state_probability(case, generator_up, line_states_up)

        for block in case.time_blocks:
            shed = state_shed_mw(case, block, generator_up, line_states_up)
            block_weight = block.weight
            if shed > 0.0:
                lolp += state_probability * block_weight
            epns += state_probability * block_weight * shed

    return ReliabilityIndices(
        lolp=lolp,
        lole_hours_per_year=HOURS_PER_YEAR * lolp,
        epns_mw=epns,
        eens_mwh_per_year=HOURS_PER_YEAR * epns,
    )


def _state_probability(case: SystemCase, generator_up: bool, line_states_up: tuple[bool, ...]) -> float:
    probability = case.generator.availability if generator_up else case.generator.unavailability
    for line, line_up in zip(case.transmission_lines, line_states_up, strict=True):
        probability *= line.availability if line_up else line.unavailability
    return probability
