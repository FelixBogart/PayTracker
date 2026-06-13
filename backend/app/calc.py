from typing import Dict


def calculate_daily_pay(
    points: int,
    tipped_hours: float,
    untipped_hours: float,
    point_value: float,
    tax_rate: float = 0.0,
    other_deductions: float = 0.0,
) -> Dict[str, float]:
    """Calculate gross and net pay for a single shift.

    Returns driving_gross, total_gross, gross_hourly, gross_drive_hourly,
    driving_net, total_net, total_hours.
    """
    untipped_gross = untipped_hours * 15.00
    tipped_gross = tipped_hours * 5.50
    points_gross = points * float(point_value)

    driving_gross = tipped_gross + points_gross
    total_gross = driving_gross + untipped_gross

    total_hours = tipped_hours + untipped_hours
    gross_hourly = total_gross / total_hours if total_hours > 0 else 0.0
    gross_drive_hourly = driving_gross / tipped_hours if tipped_hours > 0 else 0.0

    # Apply simple tax/deduction model to compute nets
    total_net = total_gross * (1.0 - tax_rate) - other_deductions
    driving_net = driving_gross * (1.0 - tax_rate)

    return {
        "untipped_gross": float(untipped_gross),
        "tipped_gross": float(tipped_gross),
        "points_gross": float(points_gross),
        "driving_gross": float(driving_gross),
        "total_gross": float(total_gross),
        "total_hours": float(total_hours),
        "gross_hourly": float(gross_hourly),
        "gross_drive_hourly": float(gross_drive_hourly),
        "driving_net": float(driving_net),
        "total_net": float(total_net),
    }


__all__ = ["calculate_daily_pay"]
