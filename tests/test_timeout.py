import asyncio

from hamcrest import assert_that, calling, equal_to, raises

from tegami.email import Email
from tegami.timeout import Timeout
from tests.fakes import SlowDelivery, receipt


def test_fails_when_delivery_is_too_slow():
    assert_that(
        calling(asyncio.run).with_args(
            Timeout(SlowDelivery(2.0, receipt("late")), 0.05).send(Email())
        ),
        raises(Exception, "Can't send email within 0.05 seconds"),
        "Timeout must fail once the deadline passes",
    )


async def test_returns_receipt_when_fast_enough():
    assert_that(
        (await Timeout(SlowDelivery(0.0, receipt("in-time")), 1.5).send(Email())).id(),
        equal_to("in-time"),
        "Timeout must pass through a receipt delivered in time",
    )
