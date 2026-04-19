from __future__ import annotations

from dataclasses import dataclass

HOURS_PER_YEAR = 8760.0


@dataclass(frozen=True)
class Component:
    name: str
    failure_rate_per_year: float
    repair_time_hours: float
    installed_capacity_mw: float

    @property
    def failure_rate_per_hour(self) -> float:
        return self.failure_rate_per_year / HOURS_PER_YEAR

    @property
    def repair_rate_per_hour(self) -> float:
        return 1.0 / self.repair_time_hours

    @property
    def unavailability(self) -> float:
        lambda_h = self.failure_rate_per_hour
        mu = self.repair_rate_per_hour
        return lambda_h / (lambda_h + mu)

    @property
    def availability(self) -> float:
        return 1.0 - self.unavailability


@dataclass(frozen=True)
class TimeBlock:
    duration_hours: float
    energy_availability_mw: float
    load_mw: float

    @property
    def weight(self) -> float:
        return self.duration_hours / HOURS_PER_YEAR


@dataclass(frozen=True)
class SystemCase:
    generator: Component
    transmission_lines: tuple[Component, ...]
    time_blocks: tuple[TimeBlock, ...]

    @property
    def total_hours(self) -> float:
        return sum(block.duration_hours for block in self.time_blocks)


@dataclass(frozen=True)
class ReliabilityIndices:
    lolp: float
    lole_hours_per_year: float
    epns_mw: float
    eens_mwh_per_year: float


@dataclass(frozen=True)
class MonteCarloConfig:
    seed: int | None = None
    target_cv_epns: float = 0.05
    min_samples: int = 20_000
    batch_size: int = 5_000
    max_samples: int = 200_000

    def __post_init__(self) -> None:
        if self.target_cv_epns <= 0:
            raise ValueError("target_cv_epns must be positive")
        if self.min_samples <= 0:
            raise ValueError("min_samples must be positive")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.max_samples < self.min_samples:
            raise ValueError("max_samples must be greater than or equal to min_samples")


@dataclass(frozen=True)
class MonteCarloResult:
    indices: ReliabilityIndices
    samples: int
    cv_lolp: float
    cv_lole: float
    cv_epns: float
    cv_eens: float
    seed: int | None


def generator_available_power_mw(case: SystemCase, block: TimeBlock, generator_up: bool) -> float:
    if not generator_up:
        return 0.0
    return min(case.generator.installed_capacity_mw, block.energy_availability_mw)


def transmission_available_power_mw(
    case: SystemCase,
    line_states_up: tuple[bool, ...],
) -> float:
    return sum(
        line.installed_capacity_mw
        for line, line_up in zip(case.transmission_lines, line_states_up, strict=True)
        if line_up
    )


def state_supply_mw(
    case: SystemCase,
    block: TimeBlock,
    generator_up: bool,
    line_states_up: tuple[bool, ...],
) -> float:
    generation_limit = generator_available_power_mw(case, block, generator_up)
    transmission_limit = transmission_available_power_mw(case, line_states_up)
    return min(generation_limit, transmission_limit)


def state_shed_mw(
    case: SystemCase,
    block: TimeBlock,
    generator_up: bool,
    line_states_up: tuple[bool, ...],
) -> float:
    return max(block.load_mw - state_supply_mw(case, block, generator_up, line_states_up), 0.0)
