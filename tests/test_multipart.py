from email.message import EmailMessage

from hamcrest import assert_that, contains_exactly, equal_to

from tegami.content import Html, Multipart, Text


def test_writes_alternative_container():
    message = EmailMessage()
    Multipart(Text("fallback"), Html("<i>rich</i>")).write(message)
    assert_that(
        message.get_content_type(),
        equal_to("multipart/alternative"),
        "Multipart must produce a multipart/alternative message",
    )


def test_keeps_alternatives_in_order():
    message = EmailMessage()
    Multipart(Text("first plain"), Html("<b>second html</b>")).write(message)
    assert_that(
        [part.get_content_type() for part in message.iter_parts()],
        contains_exactly("text/plain", "text/html"),
        "Multipart must attach alternatives in the given order",
    )
