from hamcrest import assert_that, equal_to, is_not, matches_regexp

from tegami.attachment import Attachment, Bytes
from tegami.content import Text
from tegami.email import Email
from tegami.headers import Subject


def test_stamps_message_id():
    assert_that(
        str(Email().mime()["Message-ID"]),
        matches_regexp(r"^<.+@.+>$"),
        "Email must stamp a Message-ID on every MIME message",
    )


def test_builds_fresh_message_on_every_call():
    mail = Email(Subject("Same email, two messages"))
    assert_that(
        str(mail.mime()["Message-ID"]),
        is_not(equal_to(str(mail.mime()["Message-ID"]))),
        "Each mime() call must produce a new Message-ID",
    )


def test_writes_parts_into_message():
    assert_that(
        str(Email(Subject("Quarterly numbers: 42%")).mime()["Subject"]),
        equal_to("Quarterly numbers: 42%"),
        "Email must let every part write itself into the message",
    )


def test_keeps_parts_in_given_order():
    assert_that(
        Email(Text("Body first"), Attachment("last.bin", Bytes(b"\x00\xff")))
        .mime()
        .get_content_type(),
        equal_to("multipart/mixed"),
        "Content written before an attachment must yield a mixed message",
    )
