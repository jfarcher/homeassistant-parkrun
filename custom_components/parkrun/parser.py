"""Parse public parkrun athlete result pages."""

from __future__ import annotations

import re
from dataclasses import replace
from datetime import date, datetime
from html.parser import HTMLParser
from typing import Any

from .const import ADULT_MILESTONES, VOLUNTEER_MILESTONES
from .models import ParkrunAthleteData, ParkrunResult

_TOTAL_RUNS = re.compile(r"(\d+)\s+parkruns total", re.I)
_JUNIOR_RUNS = re.compile(r"(\d+)\s+junior parkruns", re.I)
_AGE_CATEGORY = re.compile(r"Most recent age category was\s+([A-Z0-9-]+)", re.I)
_NAME = re.compile(r"<h2>([^<]+)", re.I)
_ATHLETE_ID = re.compile(r"\(A(\d+)\)")
_RUN_CLUB = re.compile(
    r"Member of the (?:parkrun )?(\d+) Club",
    re.I,
)
_VOLUNTEER_CLUB = re.compile(r"Member of the Volunteer (\d+) Club", re.I)
_CHALLENGE = re.compile(
    r"confirm you are human|just a moment|cf-challenge",
    re.I,
)


class ParkrunParseError(Exception):
    """The page was not a parkrun athlete profile."""


def looks_like_challenge(html: str) -> bool:
    """Return True if parkrun served a bot-challenge page."""
    return bool(_CHALLENGE.search(html))


def normalize_athlete_id(value: str) -> str:
    """Return the numeric athlete ID, stripping a leading A."""
    athlete_id = value.strip().upper()
    if athlete_id.startswith("A"):
        athlete_id = athlete_id[1:]
    athlete_id = athlete_id.replace(" ", "")
    if not athlete_id.isdigit():
        msg = "Athlete ID must be a number, optionally prefixed with A"
        raise ValueError(msg)
    return athlete_id


def parse_athlete_pages(
    athlete_id: str,
    profile_html: str,
    all_html: str | None,
    profile_url: str,
) -> ParkrunAthleteData:
    """Build athlete statistics from the public profile and optional /all/ page."""
    if looks_like_challenge(profile_html) or (all_html and looks_like_challenge(all_html)):
        msg = "parkrun returned a bot challenge page"
        raise ParkrunParseError(msg)

    profile_tables = HTMLTableParser.parse(profile_html)
    all_tables = HTMLTableParser.parse(all_html) if all_html else []

    recent = _find_table(profile_tables, headings=("Event", "Run Date"))
    events = _find_table(profile_tables, headings=("Event", "parkruns"))
    volunteer = _find_table(profile_tables, headings=("Role", "Occasions"))
    summary = _find_table(all_tables, caption="Summary Stats")
    all_results = _find_table(all_tables, caption="All Results") or _find_table(
        all_tables, headings=("Event", "Run Date", "Run Number")
    )

    parsed_results = _parse_all_results(all_results)
    if not parsed_results:
        parsed_results = _parse_recent_results(recent)

    heading_total = _first_int(_TOTAL_RUNS.search(profile_html))
    junior_from_text = _first_int(_JUNIOR_RUNS.search(profile_html))
    junior_from_results = sum(
        1
        for item in parsed_results
        if item.event_name and "junior" in item.event_name.lower()
    )
    junior_runs = (
        junior_from_text if junior_from_text is not None else junior_from_results
    )
    volunteer_count = _volunteer_credits(volunteer)
    events_attended = _events_attended(events, parsed_results)

    if heading_total is not None:
        total_runs = heading_total
        adult_runs = max(heading_total - junior_runs, 0)
    else:
        total_runs = len(parsed_results)
        adult_runs = max(total_runs - junior_runs, 0)

    fastest_time, best_age_grade = _summary_bests(summary)
    timed = [item for item in parsed_results if item.finish_seconds is not None]
    if fastest_time is None and timed:
        personal_best = min(timed, key=lambda item: item.finish_seconds or 0)
        fastest_time = personal_best.finish_time
        fastest_seconds = personal_best.finish_seconds
    else:
        _, fastest_seconds = _parse_run_time(fastest_time)

    if best_age_grade is None:
        graded = [item for item in parsed_results if item.age_grade is not None]
        if graded:
            best_age_grade = max(item.age_grade or 0 for item in graded)

    latest = parsed_results[0] if parsed_results else None
    first = parsed_results[-1] if parsed_results else None
    recent_latest = (_parse_recent_results(recent) or [None])[0]
    if latest and recent_latest and recent_latest.event_date == latest.event_date:
        latest = replace(
            latest,
            gender_position=recent_latest.gender_position or latest.gender_position,
            event_name=recent_latest.event_name or latest.event_name,
        )

    latest_was_pb = None
    if latest:
        latest_was_pb = latest.was_pb
        if latest_was_pb is False and fastest_seconds and latest.finish_seconds:
            latest_was_pb = latest.finish_seconds == fastest_seconds

    latest_first_timer = None
    if latest and events:
        latest_first_timer = _event_count(events, latest.event_name) == 1

    full_name = _athlete_name(profile_html)
    parsed_id = _first_group(_ATHLETE_ID.search(profile_html)) or athlete_id
    age_category = _first_group(_AGE_CATEGORY.search(profile_html))
    if latest and not latest.age_category and age_category:
        latest = replace(latest, age_category=age_category)

    run_club = _club_label(_RUN_CLUB.findall(profile_html))
    volunteer_club = _club_label(_VOLUNTEER_CLUB.findall(profile_html))
    if not run_club:
        run_club = _current_club(adult_runs, ADULT_MILESTONES)
    if not volunteer_club:
        volunteer_club = _current_club(volunteer_count, VOLUNTEER_MILESTONES)

    next_run = _next_milestone(adult_runs, ADULT_MILESTONES)
    next_volunteer = _next_milestone(volunteer_count, VOLUNTEER_MILESTONES)

    if not full_name:
        msg = "Page did not contain a parkrun athlete profile"
        raise ParkrunParseError(msg)

    return ParkrunAthleteData(
        athlete_id=parsed_id,
        first_name=full_name.split(" ", 1)[0],
        last_name=full_name.split(" ", 1)[1] if " " in full_name else "",
        full_name=full_name,
        club_name=None,
        home_run_name=_home_event(events),
        home_run_location=None,
        avatar_url=None,
        profile_url=profile_url,
        total_runs=total_runs,
        junior_runs=junior_runs,
        volunteer_count=volunteer_count,
        events_attended=events_attended,
        personal_best_time=fastest_time,
        personal_best_seconds=fastest_seconds,
        best_age_grade=best_age_grade,
        latest_event_name=latest.event_name if latest else None,
        latest_event_date=latest.event_date if latest else None,
        latest_time=latest.finish_time if latest else None,
        latest_time_seconds=latest.finish_seconds if latest else None,
        latest_position=latest.finish_position if latest else None,
        latest_gender_position=latest.gender_position if latest else None,
        latest_age_grade=latest.age_grade if latest else None,
        latest_age_category=(latest.age_category if latest else None) or age_category,
        latest_was_pb=latest_was_pb,
        latest_first_timer=latest_first_timer,
        first_event_name=first.event_name if first else None,
        first_event_date=first.event_date if first else None,
        run_club=run_club,
        next_run_milestone=next_run,
        runs_to_next_milestone=(next_run - adult_runs) if next_run else None,
        volunteer_club=volunteer_club,
        next_volunteer_milestone=next_volunteer,
        volunteer_to_next_milestone=(
            next_volunteer - volunteer_count if next_volunteer else None
        ),
    )


class HTMLTableParser(HTMLParser):
    """Extract tables as lists of text cells."""

    def __init__(self) -> None:
        """Initialize the parser."""
        super().__init__()
        self.tables: list[dict[str, Any]] = []
        self._table: dict[str, Any] | None = None
        self._row: list[str] | None = None
        self._cell = False
        self._cell_text: list[str] = []
        self._section = "body"
        self._in_caption = False
        self._caption: list[str] = []
        self._skip_depth = 0

    @classmethod
    def parse(cls, html: str) -> list[dict[str, Any]]:
        """Return every HTML table in the document."""
        parser = cls()
        parser.feed(html)
        parser.close()
        return parser.tables

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Track table structure."""
        if tag in {"script", "style"}:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag == "table":
            self._table = {"caption": "", "head": [], "body": [], "foot": []}
            self._section = "body"
        elif tag == "caption" and self._table is not None:
            self._in_caption = True
            self._caption = []
        elif tag in {"thead", "tbody", "tfoot"} and self._table is not None:
            self._section = {"thead": "head", "tbody": "body", "tfoot": "foot"}[tag]
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in {"td", "th"} and self._row is not None:
            self._cell = True
            self._cell_text = []

    def handle_endtag(self, tag: str) -> None:
        """Close table cells and rows."""
        if tag in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag == "caption" and self._in_caption:
            self._in_caption = False
            if self._table is not None:
                self._table["caption"] = _norm("".join(self._caption))
        elif tag in {"td", "th"} and self._cell:
            self._row.append(_norm("".join(self._cell_text)))
            self._cell = False
        elif tag == "tr" and self._row is not None:
            if any(self._row) and self._table is not None:
                self._table[self._section].append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            self.tables.append(self._table)
            self._table = None

    def handle_data(self, data: str) -> None:
        """Collect visible text."""
        if self._skip_depth:
            return
        if self._in_caption:
            self._caption.append(data)
        elif self._cell:
            self._cell_text.append(data)


def _find_table(
    tables: list[dict[str, Any]],
    *,
    caption: str | None = None,
    headings: tuple[str, ...] | None = None,
) -> dict[str, Any] | None:
    for table in tables:
        if caption and caption.lower() in str(table.get("caption", "")).lower():
            return table
        if headings:
            head = tuple(table["head"][0]) if table["head"] else ()
            if all(any(heading.lower() == cell.lower() for cell in head) for heading in headings):
                return table
    return None


def _parse_all_results(table: dict[str, Any] | None) -> list[ParkrunResult]:
    if not table:
        return []
    results: list[ParkrunResult] = []
    for row in table["body"]:
        if len(row) < 6:
            continue
        event, run_date, _run_number, position, time, age_grade, *rest = row
        pb_cell = rest[0] if rest else ""
        finish_time, finish_seconds = _parse_run_time(time)
        results.append(
            ParkrunResult(
                event_date=_parse_date(run_date),
                event_name=event or None,
                event_number=None,
                series_id=None,
                finish_time=finish_time,
                finish_seconds=finish_seconds,
                finish_position=_parse_int(position),
                gender_position=None,
                age_grade=_parse_float(age_grade),
                age_category=None,
                was_pb="pb" in pb_cell.lower(),
                was_genuine_pb="pb" in pb_cell.lower(),
                first_timer=False,
            )
        )
    return results


def _parse_recent_results(table: dict[str, Any] | None) -> list[ParkrunResult]:
    if not table:
        return []
    results: list[ParkrunResult] = []
    for row in table["body"]:
        if len(row) < 6:
            continue
        event, run_date, gender_pos, overall, time, age_grade = row[:6]
        finish_time, finish_seconds = _parse_run_time(time)
        results.append(
            ParkrunResult(
                event_date=_parse_date(run_date),
                event_name=event or None,
                event_number=None,
                series_id=None,
                finish_time=finish_time,
                finish_seconds=finish_seconds,
                finish_position=_parse_int(overall),
                gender_position=_parse_int(gender_pos),
                age_grade=_parse_float(age_grade),
                age_category=None,
                was_pb=False,
                was_genuine_pb=False,
                first_timer=False,
            )
        )
    return results


def _summary_bests(table: dict[str, Any] | None) -> tuple[str | None, float | None]:
    if not table:
        return None, None
    fastest_time = None
    best_grade = None
    for row in table["body"]:
        if not row:
            continue
        label = row[0].lower()
        if label == "time" and len(row) > 1:
            fastest_time = row[1] or None
        elif "age" in label and len(row) > 1:
            best_grade = _parse_float(row[1])
    return fastest_time, best_grade


def _volunteer_credits(table: dict[str, Any] | None) -> int:
    if not table:
        return 0
    for row in table["foot"] + table["body"]:
        if row and "total" in row[0].lower() and len(row) > 1:
            return _parse_int(row[1]) or 0
    return 0


def _events_attended(
    events: dict[str, Any] | None, results: list[ParkrunResult]
) -> int:
    if events and events["body"]:
        return len(events["body"])
    return len({_event_key(item.event_name) for item in results if item.event_name})


def _home_event(events: dict[str, Any] | None) -> str | None:
    if not events or not events["body"]:
        return None
    best = max(
        events["body"],
        key=lambda row: _parse_int(row[1]) or 0 if len(row) > 1 else 0,
    )
    return best[0] or None


def _event_count(events: dict[str, Any], event_name: str | None) -> int | None:
    if not event_name:
        return None
    key = _event_key(event_name)
    for row in events["body"]:
        if _event_key(row[0]) == key and len(row) > 1:
            return _parse_int(row[1])
    return None


def _event_key(name: str | None) -> str:
    text = (name or "").lower().strip()
    text = re.sub(r"\s+junior parkrun$", "", text)
    return re.sub(r"\s+parkrun$", "", text)


def _athlete_name(html: str) -> str:
    match = _NAME.search(html)
    if not match:
        return ""
    return _norm(match.group(1))


def _club_label(matches: list[str]) -> str | None:
    values = [_parse_int(item) for item in matches]
    values = [item for item in values if item]
    if not values:
        return None
    return f"{max(values)} Club"


def _next_milestone(count: int, milestones: tuple[int, ...]) -> int | None:
    for milestone in milestones:
        if count < milestone:
            return milestone
    return None


def _current_club(count: int, milestones: tuple[int, ...]) -> str | None:
    achieved = [milestone for milestone in milestones if count >= milestone]
    if not achieved:
        return None
    return f"{max(achieved)} Club"


def _parse_run_time(value: str | None) -> tuple[str | None, int | None]:
    if not value:
        return None, None
    text = value.strip()
    parts = text.split(":")
    try:
        if len(parts) == 3:
            hours, minutes, seconds = (int(part) for part in parts)
        elif len(parts) == 2:
            hours = 0
            minutes, seconds = (int(part) for part in parts)
        else:
            return text, None
    except ValueError:
        return text, None
    return text, hours * 3600 + minutes * 60 + seconds


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    text = value.strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[:10], fmt).date()
        except ValueError:
            continue
    return None


def _parse_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(str(value).strip().replace(",", ""))
    except (TypeError, ValueError):
        return None


def _parse_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).strip().rstrip("%"))
    except (TypeError, ValueError):
        return None


def _first_int(match: re.Match[str] | None) -> int | None:
    if not match:
        return None
    return _parse_int(match.group(1))


def _first_group(match: re.Match[str] | None) -> str | None:
    if not match:
        return None
    return match.group(1).strip()


def _norm(value: str) -> str:
    return " ".join(value.replace("\xa0", " ").split())
