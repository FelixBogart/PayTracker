from datetime import date
from pydantic import BaseModel
from typing import Optional


class ShiftCreate(BaseModel):
    shift_date: date
    role: Optional[str] = None
    points: int
    tipped_hours: float
    untipped_hours: float
    point_value: float


class ShiftUpdate(BaseModel):
    shift_date: Optional[date] = None
    role: Optional[str] = None
    points: Optional[int] = None
    tipped_hours: Optional[float] = None
    untipped_hours: Optional[float] = None
    point_value: Optional[float] = None


class ShiftCalculated(BaseModel):
    shift_date: date
    role: Optional[str] = None
    points: int
    tipped_hours: float
    untipped_hours: float
    point_value: float
    untipped_gross: float
    tipped_gross: float
    points_gross: float
    driving_gross: float
    total_gross: float
    total_hours: float
    gross_hourly: float
    gross_drive_hourly: float
    driving_net: float
    total_net: float


class PayPeriod(BaseModel):
    period_start: date
    period_end: date
    point_value: float
