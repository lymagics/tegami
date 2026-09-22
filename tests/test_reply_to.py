from email.message import EmailMessage

from hamcrest import assert_that, equal_to

from tegami.address import Address
from tegami.headers import ReplyTo


def test_writes_reply_to_header():
    message = EmailMessage()
    ReplyTo(Address("replies@support.example", "Support")).write(message)
    assert_that(
        str(message["Reply-To"]),
        equal_to("Support <replies@support.example>"),
        "ReplyTo must write recipients into the Reply-To header",
    )
