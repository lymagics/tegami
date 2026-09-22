from email.message import EmailMessage

from hamcrest import assert_that, equal_to

from tegami.headers import Subject


def test_writes_unicode_subject():
    message = EmailMessage()
    Subject("Héllo wörld — 日本語").write(message)
    assert_that(
        str(message["Subject"]),
        equal_to("Héllo wörld — 日本語"),
        "Subject must keep unicode text intact",
    )
