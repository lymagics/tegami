from email.message import EmailMessage

import pytest
from hamcrest import assert_that, contains_exactly, empty

from tegami.sendgrid import Newcomers, People


def test_drops_address_listed_in_earlier_header():
    message = EmailMessage()
    message["To"] = "Ψ <same-ψ@newcomers.example>"
    message["Bcc"] = "same-ψ@newcomers.example, fresh-0@newcomers.example"
    assert_that(
        Newcomers(People(message, "Bcc"), (People(message, "To"),)).json(),
        contains_exactly({"email": "fresh-0@newcomers.example"}),
        "Newcomers must leave out an address that an earlier header lists",
    )


def test_drops_address_listed_in_any_earlier_header():
    message = EmailMessage()
    message["To"] = "first-1@newcomers.example"
    message["Cc"] = "Second Two <second-2@newcomers.example>"
    message["Bcc"] = "second-2@newcomers.example"
    assert_that(
        Newcomers(
            People(message, "Bcc"),
            (People(message, "To"), People(message, "Cc")),
        ).json(),
        empty(),
        "Newcomers must leave out an address that any earlier header lists",
    )


def test_keeps_everyone_without_earlier_headers():
    message = EmailMessage()
    message["Cc"] = "Lone Wolf <lone-wolf+99@newcomers.example>"
    assert_that(
        Newcomers(People(message, "Cc"), ()).json(),
        contains_exactly(
            {"email": "lone-wolf+99@newcomers.example", "name": "Lone Wolf"}
        ),
        "Newcomers must keep everyone when there are no earlier headers",
    )


def test_drops_address_whose_domain_differs_only_in_case():
    message = EmailMessage()
    message["To"] = "kai-7@MiXeD.Newcomers.Example"
    message["Cc"] = "kai-7@mixed.newcomers.example"
    assert_that(
        Newcomers(People(message, "Cc"), (People(message, "To"),)).json(),
        empty(),
        "Newcomers must drop an address whose domain differs only in case",
    )
