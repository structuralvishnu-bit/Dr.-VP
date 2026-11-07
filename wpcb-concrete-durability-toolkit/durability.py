"""Analyze concrete durability measurements from a CSV file."""

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import linear_regression, mean


def load_series(path, measurement_column):
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        required = {"time_min", measurement_column}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"CSV requires columns: time_min, {measurement_column}")

        rows = []
        for line, row in enumerate(reader, start=2):
            try:
                time, value = (float(row[key]) for key in ("time_min", measurement_column))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid number on CSV line {line}") from exc
            if not all(math.isfinite(item) and item >= 0 for item in (time, value)):
                raise ValueError(f"Expected finite, nonnegative values on CSV line {line}")
            if rows and time <= rows[-1][0]:
                raise ValueError(f"Times must increase strictly (CSV line {line})")
            rows.append((time, value))

    if not rows or rows[0][0] != 0:
        raise ValueError("The first measurement must be at time zero")
    return rows


def sorptivity(rows, diameter_mm, start_min, end_min):
    area_mm2 = math.pi * (diameter_mm / 2) ** 2
    baseline_g = rows[0][1]
    # Water density is assumed to be 0.001 g/mm³.
    selected = [
        (math.sqrt(time), (mass - baseline_g) / (0.001 * area_mm2))
        for time, mass in rows
        if time > 0 and start_min <= time <= end_min
    ]
    if len(selected) < 3:
        raise ValueError("The fit window needs at least three positive-time measurements")

    times, depths = zip(*selected)
    fit = linear_regression(times, depths)
    mean_depth = mean(depths)
    total = sum((depth - mean_depth) ** 2 for depth in depths)
    residual = sum(
        (depth - (fit.intercept + fit.slope * time)) ** 2
        for time, depth in selected
    )
    return {
        "sorptivity_mm_per_sqrt_min": fit.slope,
        "intercept_mm": fit.intercept,
        "r_squared": 1 - residual / total if total else None,
        "measurements_used": len(selected),
        "fit_window_min": [start_min, end_min],
    }


def rcpt(rows):
    if rows[-1][0] != 360:
        raise ValueError("A six-hour RCPT series must end at 360 minutes")
    charge = sum(
        (next_time - time) * 60 * (current + next_current) / 2000
        for (time, current), (next_time, next_current) in zip(rows, rows[1:])
    )
    return {"charge_c": charge, "duration_min": 360, "measurements_used": len(rows)}


def finite_number(value):
    number = float(value)
    if not math.isfinite(number):
        raise argparse.ArgumentTypeError("expected a finite number")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    absorption = commands.add_parser("sorptivity", help="fit capillary absorption")
    absorption.add_argument("csv", type=Path)
    absorption.add_argument("--diameter-mm", type=finite_number, required=True)
    absorption.add_argument("--start-min", type=finite_number, required=True)
    absorption.add_argument("--end-min", type=finite_number, required=True)
    chloride = commands.add_parser("rcpt", help="integrate a six-hour current series")
    chloride.add_argument("csv", type=Path)
    args = parser.parse_args()

    try:
        if args.command == "sorptivity":
            if args.diameter_mm <= 0 or not 0 <= args.start_min < args.end_min:
                raise ValueError("Use a positive diameter and an increasing, nonnegative fit window")
            result = sorptivity(
                load_series(args.csv, "mass_g"),
                args.diameter_mm,
                args.start_min,
                args.end_min,
            )
        else:
            result = rcpt(load_series(args.csv, "current_ma"))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
