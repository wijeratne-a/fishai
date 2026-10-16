"""72-hour egg-encounter forecast plan.

Scoring runs in ``scripts/products/refresh_forecast.R`` inside the CI R image,
using the same prediction schema and public-map doctrine as the nowcast.
"""

from __future__ import annotations

import datetime as dt


def forecast_plan(issue_day: str, horizon_hours: int = 72) -> list[dict[str, object]]:
    if horizon_hours != 72:
        raise ValueError("forecast horizon must be 72 hours")
    issue = dt.date.fromisoformat(issue_day)
    steps = []
    for lead, age in ((1, 24), (2, 48), (3, 72)):
        valid = issue + dt.timedelta(days=lead)
        steps.append(
            {
                "mode": "forecast",
                "issue_day": issue_day,
                "valid_day": valid.isoformat(),
                "lead_days": lead,
                "forecast_age_hours": age,
                "evidence_state": "FORECAST",
                "source_run_time": f"{issue_day}T00:00:00Z",
                "life_stage": "egg",
            }
        )
    return steps
