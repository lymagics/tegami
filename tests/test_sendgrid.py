import asyncio
import json

import httpx
from hamcrest import assert_that, calling, equal_to, has_entry, raises

from tegami.address import Address
from tegami.content import Text
from tegami.email import Email
from tegami.headers import From, Subject, To
from tegami.sendgrid import SendGrid
from tests.fakes import FakeSendGrid


def _email(marker: str) -> Email:
    return Email(
        From(Address(f"{marker}@sendgrid.example")),
        To(Address(f"{marker}.target@sendgrid.example")),
        Subject(f"Subject {marker}"),
        Text(f"Body {marker}"),
    )


async def test_reports_provider_message_id():
    api = FakeSendGrid(httpx.Response(202, headers={"X-Message-Id": "sg-9f8e7d"}))
    assert_that(
        (
            await SendGrid("SG.key-one", httpx.MockTransport(api)).deliver(
                _email("one").mime()
            )
        ).id(),
        equal_to("sg-9f8e7d"),
        "SendGrid receipt must carry the X-Message-Id response header",
    )


async def test_sends_bearer_token():
    api = FakeSendGrid(httpx.Response(202, headers={"X-Message-Id": "sg-auth"}))
    await SendGrid("SG.secret-two", httpx.MockTransport(api)).deliver(
        _email("two").mime()
    )
    assert_that(
        api.requests[0].headers["Authorization"],
        equal_to("Bearer SG.secret-two"),
        "SendGrid must authorize with the API key as a bearer token",
    )


async def test_posts_to_mail_send_endpoint():
    api = FakeSendGrid(httpx.Response(202, headers={"X-Message-Id": "sg-url"}))
    await SendGrid("SG.key-three", httpx.MockTransport(api)).deliver(
        _email("three").mime()
    )
    assert_that(
        str(api.requests[0].url),
        equal_to("https://api.sendgrid.com/v3/mail/send"),
        "SendGrid must post to the v3 mail send endpoint",
    )


async def test_posts_json_payload():
    api = FakeSendGrid(httpx.Response(202, headers={"X-Message-Id": "sg-json"}))
    await SendGrid("SG.key-four", httpx.MockTransport(api)).deliver(
        _email("four").mime()
    )
    assert_that(
        json.loads(api.requests[0].content),
        has_entry("subject", "Subject four"),
        "SendGrid must post the mapped payload as JSON",
    )


async def test_reports_all_recipients():
    api = FakeSendGrid(httpx.Response(202, headers={"X-Message-Id": "sg-rcpt"}))
    assert_that(
        (
            await SendGrid("SG.key-five", httpx.MockTransport(api)).deliver(
                _email("five").mime()
            )
        ).recipients(),
        equal_to(
            ("five.target@sendgrid.example",),
        ),
        "SendGrid receipt must list the recipients of the message",
    )


def test_fails_on_rejected_request():
    api = FakeSendGrid(httpx.Response(400, json={"errors": [{"message": "bad"}]}))
    assert_that(
        calling(asyncio.run).with_args(
            SendGrid("SG.key-six", httpx.MockTransport(api)).deliver(
                _email("six").mime()
            )
        ),
        raises(Exception, "SendGrid rejected email"),
        "SendGrid must fail clearly on a non-success status",
    )


def test_fails_on_connection_error():
    def refuse(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    assert_that(
        calling(asyncio.run).with_args(
            SendGrid("SG.key-seven", httpx.MockTransport(refuse)).deliver(
                _email("seven").mime()
            )
        ),
        raises(Exception, "Can't deliver email"),
        "SendGrid must fail clearly when the network is down",
    )
