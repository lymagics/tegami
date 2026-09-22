import asyncio

from hamcrest import assert_that, calling, equal_to, greater_than_or_equal_to, raises

from tegami.email import Email
from tegami.retry import Retry
from tests.fakes import FakeDelivery, receipt


async def test_succeeds_after_failures():
    assert_that(
        (await Retry(FakeDelivery(2, receipt("after-two")), 3, 0.0).send(Email())).id(),
        equal_to("after-two"),
        "Retry must return the receipt once an attempt succeeds",
    )


async def test_stops_after_first_success():
    delivery = FakeDelivery(0, receipt("first-try"))
    await Retry(delivery, 5, 0.0).send(Email())
    assert_that(
        delivery.calls,
        equal_to(1),
        "Retry must not call again after a success",
    )


def test_raises_last_error_when_exhausted():
    assert_that(
        calling(asyncio.run).with_args(
            Retry(FakeDelivery(9, receipt("never")), 4, 0.0).send(Email())
        ),
        raises(Exception, "Attempt 4 failed"),
        "Retry must raise the error of the last attempt",
    )


async def test_waits_a_second_by_default():
    started = asyncio.get_running_loop().time()
    await Retry(FakeDelivery(1, receipt("default-wait")), 2).send(Email())
    assert_that(
        asyncio.get_running_loop().time() - started,
        greater_than_or_equal_to(0.9),
        "Retry must pause about one second between attempts by default",
    )
