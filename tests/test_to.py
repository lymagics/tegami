from email.message import EmailMessage

from hamcrest import assert_that, has_length

from tegami.address import Address
from tegami.headers import To


def test_writes_several_recipients():
    message = EmailMessage()
    To(Address("one@to.example"), Address("two@to.example"), Address("3@to.x")).write(
        message
    )
    assert_that(
        message["To"].addresses,
        has_length(3),
        "To must write every recipient into the To header",
    )
