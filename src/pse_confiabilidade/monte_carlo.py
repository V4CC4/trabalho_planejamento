from __future__ import annotations

import math
import random

from pse_confiabilidade.domain import (
    HOURS_PER_YEAR,
    MonteCarloConfig,
    MonteCarloResult,
    ReliabilityIndices,
    SystemCase,
    state_shed_mw,
)


def simulate_indices(case: SystemCase, config: MonteCarloConfig) -> MonteCarloResult:
    rng = random.Random(config.seed)
    weights = [block.duration_hours for block in case.time_blocks]

    failures = 0.0
    failures_sum_squares = 0.0
    shed_sum = 0.0
    shed_sum_squares = 0.0
    samples = 0
    cv_epns = math.inf

    while samples < config.max_samples:
        draws = min(config.batch_size, config.max_samples - samples)
        for _ in range(draws):
            block = rng.choices(case.time_blocks, weights=weights, k=1)[0]
            generator_up = rng.random() <= case.generator.availability
            line_states_up = tuple(rng.random() <= line.availability for line in case.transmission_lines)
            shed = state_shed_mw(case, block, generator_up, line_states_up)
            failure = 1.0 if shed > 0.0 else 0.0

            failures += failure
            failures_sum_squares += failure * failure
            shed_sum += shed
            shed_sum_squares += shed * shed
            samples += 1

        if samples >= config.min_samples:
            cv_epns = _estimate_cv(shed_sum, shed_sum_squares, samples)
            if cv_epns <= config.target_cv_epns:
                break

    lolp = failures / samples
    epns = shed_sum / samples
    cv_lolp = _estimate_cv(failures, failures_sum_squares, samples)
    indices = ReliabilityIndices(
        lolp=lolp,
        lole_hours_per_year=HOURS_PER_YEAR * lolp,
        epns_mw=epns,
        eens_mwh_per_year=HOURS_PER_YEAR * epns,
    )
    return MonteCarloResult(
        indices=indices,
        samples=samples,
        cv_lolp=cv_lolp,
        cv_lole=cv_lolp,
        cv_epns=cv_epns,
        cv_eens=cv_epns,
        seed=config.seed,
    )


def _estimate_cv(sum_values: float, sum_squares: float, samples: int) -> float:
    mean = sum_values / samples
    if mean <= 0.0:
        return math.inf
    variance = max((sum_squares / samples) - (mean * mean), 0.0)
    return math.sqrt(variance / samples) / mean
