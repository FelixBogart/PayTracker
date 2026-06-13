from app.calc import calculate_daily_pay


def test_calculate_daily_pay_basic():
    out = calculate_daily_pay(points=1200, tipped_hours=4.5, untipped_hours=3.0, point_value=0.007)

    # Expected intermediate values (from the same formula used in the app)
    assert round(out["untipped_gross"], 2) == 45.00
    assert round(out["tipped_gross"], 2) == 24.75
    assert round(out["points_gross"], 2) == 8.40
    assert round(out["driving_gross"], 2) == 33.15
    assert round(out["total_gross"], 2) == 78.15
    assert round(out["total_hours"], 2) == 7.5
    assert round(out["gross_hourly"], 2) == 10.42
