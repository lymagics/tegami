from email.message import EmailMessage

from hamcrest import assert_that, equal_to

from tegami.address import Address
from tegami.headers import Cc


def test_writes_cc_header():
    message = EmailMessage()
    Cc(Address("copy@cc.example", "Carbon Copy")).write(message)
    assert_that(
        str(message["Cc"]),
        equal_to("Carbon Copy <copy@cc.example>"),
        "Cc must write recipients into the Cc header",
    )
