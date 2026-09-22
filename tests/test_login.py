import asyncio

from hamcrest import assert_that, calling, has_length, raises

from tegami.address import Address
from tegami.content import Text
from tegami.email import Email
from tegami.headers import From, To
from tegami.smtp import Login, Smtp
from tests.fakes import Inbox, Port, Server


def test_authenticates_with_password():
    inbox = Inbox()
    port = Port().number()
    with Server(inbox, port, "alice", "s3cr3t!"):
        asyncio.run(
            Smtp("127.0.0.1", port, Login("alice", "s3cr3t!")).deliver(
                Email(
                    From(Address("alice@login.example")),
                    To(Address("bob@login.example")),
                    Text("authenticated"),
                ).mime()
            )
        )
    assert_that(
        inbox.envelopes,
        has_length(1),
        "Login must authenticate so that the server accepts the message",
    )


def test_fails_with_wrong_password():
    port = Port().number()
    with Server(Inbox(), port, "carol", "right"):
        assert_that(
            calling(asyncio.run).with_args(
                Smtp("127.0.0.1", port, Login("carol", "wrong")).deliver(
                    Email(
                        From(Address("carol@login.example")),
                        To(Address("dave@login.example")),
                        Text("rejected"),
                    ).mime()
                )
            ),
            raises(Exception, "Can't deliver email"),
            "Login with a wrong password must fail delivery",
        )
