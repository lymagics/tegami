from email.message import EmailMessage

from hamcrest import assert_that, contains_exactly, empty

from tegami.attachment import Attachment, Bytes
from tegami.content import Text
from tegami.sendgrid import Attachments


def test_encodes_attachment_as_base64():
    message = EmailMessage()
    Text("with file").write(message)
    Attachment("hello.txt", Bytes(b"hello world")).write(message)
    assert_that(
        Attachments(message).json(),
        contains_exactly(
            {
                "content": "aGVsbG8gd29ybGQ=",
                "type": "text/plain",
                "filename": "hello.txt",
                "disposition": "attachment",
            }
        ),
        "Attachments must encode file bytes as base64",
    )


def test_lists_nothing_without_attachments():
    message = EmailMessage()
    Text("bare body").write(message)
    assert_that(
        Attachments(message).json(),
        empty(),
        "Attachments must be empty for a message without files",
    )
