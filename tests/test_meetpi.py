"""Tests for meetpi."""

import datetime
from unittest import mock

import pytest

from meetpi import meetpi

today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)
tomorrow = today + datetime.timedelta(days=1)


@pytest.mark.parametrize(
    "mock_datetime,expected",
    [
        (datetime.datetime(2021, 2, 26, 8), False),  # friday before 9am
        (datetime.datetime(2021, 2, 26, 20), False),  # friday after 8pm
        (datetime.datetime(2021, 2, 27), False),  # saturday
        (datetime.datetime(2021, 2, 28), False),  # sunday
        (datetime.datetime(2021, 2, 26, 9), True),  # friday after 9am
        (datetime.datetime(2021, 2, 26, 19), True),  # friday before 8pm
    ],
)
def test_office_hours(mock_datetime, expected):
    """Test that we correctly return the office hours status."""
    with mock.patch("meetpi.meetpi.get_today", return_value=mock_datetime):
        assert meetpi.office_hours() == expected


@pytest.mark.parametrize(
    "office_hours,events,expected",
    [
        (False, [], "OUT OF OFFICE"),
        (True, [], "FREE"),
        (True, ["event"], "BUSY"),
    ],
)
def test_get_status(office_hours, events, expected):
    """Test that we correctly return the meeting status."""
    with mock.patch("meetpi.meetpi.office_hours", return_value=office_hours):
        with mock.patch("meetpi.meetpi.get_events", return_value=events):
            assert meetpi.get_status("foo") == expected


@pytest.mark.parametrize(
    "started,attending,expected",
    [
        (True, True, True),  # started and attending
        (True, False, False),  # started but not attending
        (False, False, False),  # not started and not attending
        (False, True, False),  # not started and attending
    ],
)
def test_valid_event(started, attending, expected):
    """Test that we correctly identify valid events."""
    with mock.patch("meetpi.meetpi.started", return_value=started):
        with mock.patch("meetpi.meetpi.attending", return_value=attending):
            assert meetpi.valid_event(None) == expected


@pytest.mark.parametrize(
    "is_self,response,expected",
    [
        (True, "accepted", True),  # attendee is self and has accepted
        (True, "needsAction", False),  # attendee is self and has not responded
        (False, "accepted", False),  # attendee is not self and has accepted
        (False, "needsAction", False),  # attendee is not self and has not responded
    ],
)
def test_attendees(is_self, response, expected):
    """Test that we correctly return the attendee status."""
    event = {"attendees": [{"self": is_self, "responseStatus": response}]}
    assert meetpi.attending(event) == expected


def test_no_attendees():
    """Test that handle when events have no attendees."""
    event = {"attendees": []}
    assert not meetpi.attending(event)


@pytest.mark.parametrize(
    "key,value,expected",
    [
        ("dateTime", today.isoformat(), True),  # event in progress
        ("date", today.strftime("%Y-%m-%d"), True),  # all day event in progress
        ("dateTime", yesterday.isoformat(), True),  # event in the past
        ("date", yesterday.strftime("%Y-%m-%d"), True),  # all day event in the past
        ("dateTime", tomorrow.isoformat(), False),  # event in the future
        ("date", tomorrow.strftime("%Y-%m-%d"), False),  # all day event in the future
    ],
)
def test_started(key, value, expected):
    """Test that we correctly identify events that have started."""
    event = {"start": {key: value}}
    assert meetpi.started(event) == expected
