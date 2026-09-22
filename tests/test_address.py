from hamcrest import assert_that, equal_to
from hypothesis import given
from hypothesis import strategies as st

from tegami.address import Address


def test_renders_bare_email():
    assert_that(
        Address("zoe.q+tag@sub.example.org").value(),
        equal_to("zoe.q+tag@sub.example.org"),
        "Address without a name must render as the bare email",
    )


def test_renders_name_with_email():
    assert_that(
        Address("bob@example.com", "Bob Smith").value(),
        equal_to("Bob Smith <bob@example.com>"),
        "Address with a name must render as name <email>",
    )


def test_quotes_name_with_comma():
    assert_that(
        Address("smith@example.net", "Smith, Robert").value(),
        equal_to('"Smith, Robert" <smith@example.net>'),
        "A display name with a comma must be quoted",
    )


@given(st.emails())
def test_keeps_any_valid_email_untouched(email: str):
    assert_that(
        Address(email).value(),
        equal_to(email),
        "Address must not alter a bare email",
    )
