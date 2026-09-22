from email.message import EmailMessage

from hamcrest import assert_that, equal_to

from tegami.address import Address
from tegami.headers import Bcc


def test_writes_bcc_header():
    message = EmailMessage()
    Bcc(Address("hidden@bcc.example"), Address("secret@bcc.example")).write(message)
    assert_that(
        str(message["Bcc"]),
        equal_to("hidden@bcc.example, secret@bcc.example"),
        "Bcc must write recipients into the Bcc header",
    )
