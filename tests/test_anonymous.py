import asyncio

from hamcrest import assert_that, calling, has_length, raises

from tegami.address import Address
from tegami.content import Text
from tegami.email import Email
from tegami.headers import From, To
from tegami.smtp import Anonymous, Smtp
from tests.fakes import Inbox, Port, Server


def test_delivers_to_open_server():
    inbox = Inbox()
    port = Port().number()
    with Server(inbox, port, "", ""):
        asyncio.run(
            Smtp("127.0.0.1", port, Anonymous()).deliver(
                Email(
                    From(Address("anon@open.example")),
                    To(Address("anyone@open.example")),
                    Text("no credentials"),
                ).mime()
            )
        )
    assert_that(
        inbox.envelopes,
        has_length(1),
        "Anonymous must deliver to a server without authentication",
    )


def test_fails_when_server_requires_auth():
    port = Port().number()
    with Server(Inbox(), port, "gate", "keeper"):
        assert_that(
            calling(asyncio.run).with_args(
                Smtp("127.0.0.1", port, Anonymous()).deliver(
                    Email(
                        From(Address("anon@closed.example")),
                        To(Address("nobody@closed.example")),
                        Text("refused"),
                    ).mime()
                )
            ),
            raises(Exception, "Can't deliver email"),
            "Anonymous must fail against a server that requires authentication",
        )
