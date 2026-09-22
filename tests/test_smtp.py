import asyncio

from hamcrest import (
    assert_that,
    calling,
    contains_exactly,
    contains_string,
    equal_to,
    has_item,
    is_not,
    raises,
)

from tegami.address import Address
from tegami.content import Text
from tegami.email import Email
from tegami.headers import Bcc, From, To
from tegami.smtp import Anonymous, Smtp
from tests.fakes import Inbox, Port, Server


def test_reports_message_id_in_receipt():
    port = Port().number()
    message = Email(
        From(Address("id@smtp.example")),
        To(Address("dest@smtp.example")),
        Text("receipt id"),
    ).mime()
    with Server(Inbox(), port, "", ""):
        receipt = asyncio.run(Smtp("127.0.0.1", port, Anonymous()).deliver(message))
    assert_that(
        receipt.id(),
        equal_to(str(message["Message-ID"])),
        "Smtp receipt must carry the Message-ID of the sent message",
    )


def test_reports_accepted_recipients():
    port = Port().number()
    with Server(Inbox(), port, "", ""):
        receipt = asyncio.run(
            Smtp("127.0.0.1", port, Anonymous()).deliver(
                Email(
                    From(Address("acc@smtp.example")),
                    To(Address("first@smtp.example")),
                    Bcc(Address("second@smtp.example")),
                    Text("recipients"),
                ).mime()
            )
        )
    assert_that(
        receipt.recipients(),
        contains_exactly("first@smtp.example", "second@smtp.example"),
        "Smtp receipt must list every accepted recipient",
    )


def test_sends_bcc_recipient_in_envelope():
    inbox = Inbox()
    port = Port().number()
    with Server(inbox, port, "", ""):
        asyncio.run(
            Smtp("127.0.0.1", port, Anonymous()).deliver(
                Email(
                    From(Address("env@smtp.example")),
                    To(Address("shown@smtp.example")),
                    Bcc(Address("blind@smtp.example")),
                    Text("bcc envelope"),
                ).mime()
            )
        )
    assert_that(
        inbox.envelopes[0].rcpt_tos,
        has_item("blind@smtp.example"),
        "Smtp must send the message to Bcc recipients",
    )


def test_hides_bcc_header_from_receiver():
    inbox = Inbox()
    port = Port().number()
    with Server(inbox, port, "", ""):
        asyncio.run(
            Smtp("127.0.0.1", port, Anonymous()).deliver(
                Email(
                    From(Address("hide@smtp.example")),
                    To(Address("open@smtp.example")),
                    Bcc(Address("ghost@smtp.example")),
                    Text("bcc header"),
                ).mime()
            )
        )
    assert_that(
        inbox.envelopes[0].content.decode(),
        is_not(contains_string("ghost@smtp.example")),
        "Smtp must strip the Bcc header before sending",
    )


def test_fails_when_nobody_listens():
    assert_that(
        calling(asyncio.run).with_args(
            Smtp("127.0.0.1", Port().number(), Anonymous()).deliver(
                Email(
                    From(Address("lost@smtp.example")),
                    To(Address("void@smtp.example")),
                    Text("connection refused"),
                ).mime()
            )
        ),
        raises(Exception, "Can't deliver email"),
        "Smtp must fail with a clear message when the server is unreachable",
    )
