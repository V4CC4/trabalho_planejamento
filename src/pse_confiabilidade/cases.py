from __future__ import annotations

from pse_confiabilidade.domain import Component, SystemCase, TimeBlock


def build_default_case() -> SystemCase:
    generator = Component(
        name="G",
        failure_rate_per_year=4.0,
        repair_time_hours=100.0,
        installed_capacity_mw=600.0,
    )
    transmission_lines = (
        Component(
            name="LT1",
            failure_rate_per_year=1.8,
            repair_time_hours=4.0,
            installed_capacity_mw=400.0,
        ),
        Component(
            name="LT2",
            failure_rate_per_year=1.8,
            repair_time_hours=4.0,
            installed_capacity_mw=400.0,
        ),
    )
    energy_availability = (200.0, 400.0, 600.0, 600.0, 200.0, 400.0, 600.0, 400.0, 200.0, 400.0, 600.0, 600.0)
    load = (400.0, 300.0, 100.0, 100.0, 200.0, 300.0, 300.0, 300.0, 200.0, 400.0, 400.0, 200.0)
    time_blocks = tuple(
        TimeBlock(duration_hours=730.0, energy_availability_mw=energy_mw, load_mw=load_mw)
        for energy_mw, load_mw in zip(energy_availability, load, strict=True)
    )
    return SystemCase(
        generator=generator,
        transmission_lines=transmission_lines,
        time_blocks=time_blocks,
    )
