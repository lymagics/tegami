from email.message import EmailMessage

from hamcrest import assert_that, equal_to

from tegami.address import Address
from tegami.headers import Mailboxes


def test_joins_addresses_with_commas():
    message = EmailMessage()
    Mailboxes("Cc", Address("a@x.io"), Address("b@y.io", "Bee")).write(message)
    assert_that(
        str(message["Cc"]),
        equal_to("a@x.io, Bee <b@y.io>"),
        "Mailboxes must join rendered addresses with a comma",
    )
