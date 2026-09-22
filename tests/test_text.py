from email.message import EmailMessage

from hamcrest import assert_that, equal_to

from tegami.content import Text


def test_writes_plain_body():
    message = EmailMessage()
    Text("Line one\nLine two\ttabbed").write(message)
    assert_that(
        message.get_content(),
        equal_to("Line one\nLine two\ttabbed\n"),
        "Text must write the body as the message content",
    )


def test_marks_body_as_plain_text():
    message = EmailMessage()
    Text("<b>not html</b>").write(message)
    assert_that(
        message.get_content_type(),
        equal_to("text/plain"),
        "Text must produce a text/plain part",
    )
