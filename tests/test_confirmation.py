from hamcrest import assert_that, contains_exactly, equal_to, has_entry

from tegami.receipt import Confirmation


def test_reports_id():
    assert_that(
        Confirmation("<abc.123@host>", (), {}).id(),
        equal_to("<abc.123@host>"),
        "Confirmation must report the provider id",
    )


def test_reports_recipients():
    assert_that(
        Confirmation("r1", ("x@a.io", "y@b.io"), {}).recipients(),
        contains_exactly("x@a.io", "y@b.io"),
        "Confirmation must report accepted recipients",
    )


def test_reports_metadata():
    assert_that(
        Confirmation("r2", (), {"response": "250 Queued"}).metadata(),
        has_entry("response", "250 Queued"),
        "Confirmation must expose provider metadata",
    )
