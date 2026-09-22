from email.message import EmailMessage

from hamcrest import assert_that, contains_exactly, empty

from tegami.sendgrid import People


def test_lists_everyone_in_header():
    message = EmailMessage()
    message["Cc"] = "Uno <uno@people.example>, dos@people.example"
    assert_that(
        People(message, "Cc").json(),
        contains_exactly(
            {"email": "uno@people.example", "name": "Uno"},
            {"email": "dos@people.example"},
        ),
        "People must convert every address in the header",
    )


def test_lists_nobody_for_missing_header():
    assert_that(
        People(EmailMessage(), "Bcc").json(),
        empty(),
        "People must be empty when the header is absent",
    )
