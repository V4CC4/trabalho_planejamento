from __future__ import annotations

import argparse

from pse_confiabilidade.cases import build_default_case
from pse_confiabilidade.domain import MonteCarloConfig, ReliabilityIndices
from pse_confiabilidade.enumeration import enumerate_indices
from pse_confiabilidade.monte_carlo import simulate_indices


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command != "run":
        parser.error("a command is required")

    case = build_default_case()

    if args.method == "enumeration":
        indices = enumerate_indices(case)
        print(_format_indices_table("enumeration", indices))
        return 0

    config = MonteCarloConfig(
        seed=args.seed,
        target_cv_epns=args.target_cv_epns,
        min_samples=args.min_samples,
        batch_size=args.batch_size,
        max_samples=args.max_samples,
    )

    if args.method == "smc":
        result = simulate_indices(case, config)
        print(_format_indices_table("smc", result.indices))
        print(_format_smc_metadata(result))
        return 0

    enumeration = enumerate_indices(case)
    result = simulate_indices(case, config)
    print(_format_indices_table("enumeration", enumeration))
    print()
    print(_format_indices_table("smc", result.indices))
    print(_format_smc_metadata(result))
    print()
    print(_format_comparison(enumeration, result.indices))
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Composite reliability indices for the Trabalho 2 case.")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run the reliability study for the default case.")
    run_parser.add_argument("--method", choices=("enumeration", "smc", "both"), default="both")
    run_parser.add_argument("--seed", type=int, default=42)
    run_parser.add_argument("--target-cv-epns", type=float, default=0.05)
    run_parser.add_argument("--min-samples", type=int, default=20_000)
    run_parser.add_argument("--batch-size", type=int, default=5_000)
    run_parser.add_argument("--max-samples", type=int, default=200_000)

    return parser


def _format_indices_table(method: str, indices: ReliabilityIndices) -> str:
    return "\n".join(
        (
            "Method       LOLP           LOLE (h/yr)     EPNS (MW)       EENS (MWh/yr)",
            f"{method:<12} {indices.lolp:>12.9f} {indices.lole_hours_per_year:>15.6f} {indices.epns_mw:>15.6f} {indices.eens_mwh_per_year:>17.6f}",
        )
    )


def _format_smc_metadata(result) -> str:
    return (
        f"samples={result.samples}  "
        f"cv_lolp={result.cv_lolp:.6f}  "
        f"cv_lole={result.cv_lole:.6f}  "
        f"cv_epns={result.cv_epns:.6f}  "
        f"cv_eens={result.cv_eens:.6f}  "
        f"seed={result.seed}"
    )


def _format_comparison(reference: ReliabilityIndices, estimate: ReliabilityIndices) -> str:
    rows = ["Absolute error / Relative error"]
    for label, reference_value, estimate_value in (
        ("LOLP", reference.lolp, estimate.lolp),
        ("LOLE", reference.lole_hours_per_year, estimate.lole_hours_per_year),
        ("EPNS", reference.epns_mw, estimate.epns_mw),
        ("EENS", reference.eens_mwh_per_year, estimate.eens_mwh_per_year),
    ):
        absolute_error = abs(estimate_value - reference_value)
        relative_error = absolute_error / reference_value if reference_value else 0.0
        rows.append(f"{label:<5} abs={absolute_error:.6f}  rel={relative_error:.6%}")
    return "\n".join(rows)
