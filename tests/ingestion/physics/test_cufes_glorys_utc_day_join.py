"""CUFES event mid-time must map to GLORYS daily fields on the UTC calendar day."""

from __future__ import annotations

import datetime as dt

import pandas as pd
import pytest

from fishai.ingestion.physics.covariates import COL_EVENT_ID, COL_START_TIME, COL_STOP_TIME, event_mid_time
from fishai.ingestion.physics.cufes_training_covariates import unique_event_days


def test_unique_event_days_use_utc_calendar_day_of_mid_time() -> None:
    events = pd.DataFrame(
        [
            {
                COL_EVENT_ID: "CUFES:199603:JD:1",
                COL_START_TIME: pd.Timestamp("1996-03-16T04:47:00Z"),
                COL_STOP_TIME: pd.Timestamp("1996-03-16T04:52:00Z"),
            },
            {
                COL_EVENT_ID: "CUFES:199603:JD:2",
                COL_START_TIME: pd.Timestamp("1996-03-16T23:50:00Z"),
                COL_STOP_TIME: pd.Timestamp("1996-03-17T00:10:00Z"),
            },
        ]
    )
    days = unique_event_days(events)
    assert days == [dt.date(1996, 3, 16), dt.date(1996, 3, 17)]
    mid2 = event_mid_time(events.iloc[1])
    assert mid2.date() == dt.date(1996, 3, 17)
    assert mid2.tzinfo is not None


def test_event_mid_time_requires_utc_timestamps() -> None:
    row = pd.Series(
        {
            COL_START_TIME: "1996-03-16T04:47:00+00:00",
            COL_STOP_TIME: "1996-03-16T04:52:00+00:00",
        }
    )
    mid = event_mid_time(row)
    assert mid == pd.Timestamp("1996-03-16T04:49:30+00:00")
