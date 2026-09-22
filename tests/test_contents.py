from email.message import EmailMessage

from hamcrest import assert_that, contains_exactly, has_length

from tegami.attachment import Attachment, Bytes
from tegami.content import Html, Multipart, Text
from tegami.sendgrid import Contents


def test_lists_text_and_html_alternatives():
    message = EmailMessage()
    Multipart(Text("plain words"), Html("<em>rich words</em>")).write(message)
    assert_that(
        Contents(message).json(),
        contains_exactly(
            {"type": "text/plain", "value": "plain words\n"},
            {"type": "text/html", "value": "<em>rich words</em>\n"},
        ),
        "Contents must list every text alternative with its type",
    )


def test_skips_text_attachments():
    message = EmailMessage()
    Text("only body").write(message)
    Attachment("notes.txt", Bytes(b"attached text")).write(message)
    assert_that(
        Contents(message).json(),
        has_length(1),
        "Contents must not treat a text attachment as body",
    )
