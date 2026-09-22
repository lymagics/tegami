from email.message import EmailMessage

from hamcrest import assert_that, equal_to

from tegami.attachment import Attachment, Bytes


def test_attaches_payload_bytes():
    message = EmailMessage()
    Attachment("raw.bin", Bytes(b"\x89PNG\r\n\x1a\n")).write(message)
    assert_that(
        next(message.iter_attachments()).get_payload(decode=True),
        equal_to(b"\x89PNG\r\n\x1a\n"),
        "Attachment must carry the blob bytes unchanged",
    )


def test_names_attachment_file():
    message = EmailMessage()
    Attachment("invoice 2024.pdf", Bytes(b"%PDF-1.7")).write(message)
    assert_that(
        next(message.iter_attachments()).get_filename(),
        equal_to("invoice 2024.pdf"),
        "Attachment must keep the given file name",
    )


def test_guesses_content_type():
    message = EmailMessage()
    Attachment("picture.png", Bytes(b"\x89PNG")).write(message)
    assert_that(
        next(message.iter_attachments()).get_content_type(),
        equal_to("image/png"),
        "Attachment must guess the MIME type from the name",
    )


def test_uses_explicit_content_type():
    message = EmailMessage()
    Attachment("payload.dat", Bytes(b"custom"), "application/x-custom").write(message)
    assert_that(
        next(message.iter_attachments()).get_content_type(),
        equal_to("application/x-custom"),
        "Attachment must prefer an explicit MIME type",
    )
