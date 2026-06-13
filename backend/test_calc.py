import sys
import os

# Ensure the package path resolves when running this script directly
ROOT = os.path.dirname(os.path.abspath(__file__))
APP_PATH = os.path.join(ROOT, "app")
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)

from calc import calculate_daily_pay


def _pretty(d):
    for k, v in d.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    sample = calculate_daily_pay(points=1200, tipped_hours=4.5, untipped_hours=3.0, point_value=0.007)
    _pretty(sample)
