from email.message import EmailMessage

from hamcrest import assert_that, equal_to

from tegami.address import Address
from tegami.headers import From


def test_writes_from_header():
    message = EmailMessage()
    From(Address("sender@corp.example", "The Sender")).write(message)
    assert_that(
        str(message["From"]),
        equal_to("The Sender <sender@corp.example>"),
        "From must write the sender into the From header",
    )
