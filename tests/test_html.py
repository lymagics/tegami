from email.message import EmailMessage

from hamcrest import assert_that, contains_string, equal_to

from tegami.content import Html


def test_writes_html_body():
    message = EmailMessage()
    Html("<p>Ünïcode &amp; entities</p>").write(message)
    assert_that(
        message.get_content(),
        contains_string("<p>Ünïcode &amp; entities</p>"),
        "Html must write the markup as the message content",
    )


def test_marks_body_as_html():
    message = EmailMessage()
    Html("<h1>Title</h1>").write(message)
    assert_that(
        message.get_content_type(),
        equal_to("text/html"),
        "Html must produce a text/html part",
    )
