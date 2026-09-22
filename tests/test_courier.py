from hamcrest import assert_that, equal_to

from tegami.courier import Courier
from tegami.email import Email
from tegami.headers import Subject
from tests.fakes import FakeTransport, receipt


async def test_returns_transport_receipt():
    assert_that(
        (await Courier(FakeTransport(receipt("courier-77"))).send(Email())).id(),
        equal_to("courier-77"),
        "Courier must hand back the receipt from the transport",
    )


async def test_passes_mime_message_to_transport():
    transport = FakeTransport(receipt("courier-78"))
    await Courier(transport).send(Email(Subject("Through the courier")))
    assert_that(
        str(transport.messages[0]["Subject"]),
        equal_to("Through the courier"),
        "Courier must convert the email to MIME before delivering",
    )
