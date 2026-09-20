"""Data models for parkrun athlete statistics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class ParkrunResult:
    """A single parkrun result."""

    event_date: date | None
    event_name: str | None
    event_number: int | None
    series_id: int | None
    finish_time: str | None
    finish_seconds: int | None
    finish_position: int | None
    gender_position: int | None
    age_grade: float | None
    age_category: str | None
    was_pb: bool
    was_genuine_pb: bool
    first_timer: bool


@dataclass(frozen=True, slots=True)
class ParkrunAthleteData:
    """Aggregated parkrun athlete statistics exposed as Home Assistant sensors."""

    athlete_id: str
    first_name: str
    last_name: str
    full_name: str
    club_name: str | None
    home_run_name: str | None
    home_run_location: str | None
    avatar_url: str | None
    profile_url: str

    total_runs: int
    junior_runs: int
    volunteer_count: int
    events_attended: int

    personal_best_time: str | None
    personal_best_seconds: int | None
    best_age_grade: float | None

    latest_event_name: str | None
    latest_event_date: date | None
    latest_time: str | None
    latest_time_seconds: int | None
    latest_position: int | None
    latest_gender_position: int | None
    latest_age_grade: float | None
    latest_age_category: str | None
    latest_was_pb: bool | None
    latest_first_timer: bool | None

    first_event_name: str | None
    first_event_date: date | None

    run_club: str | None
    next_run_milestone: int | None
    runs_to_next_milestone: int | None

    volunteer_club: str | None
    next_volunteer_milestone: int | None
    volunteer_to_next_milestone: int | None
