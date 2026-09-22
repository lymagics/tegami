import asyncio
import socket
from email.message import EmailMessage
from typing import Self

import httpx
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult, LoginPassword

from tegami.delivery import Delivery
from tegami.email import Email
from tegami.receipt import Confirmation, Receipt
from tegami.transport import Transport


class FakeTransport(Transport):
    def __init__(self, receipt: Receipt):
        self.receipt = receipt
        self.messages: list[EmailMessage] = []

    async def deliver(self, message: EmailMessage) -> Receipt:
        self.messages.append(message)
        return self.receipt


class FakeDelivery(Delivery):
    def __init__(self, failures: int, receipt: Receipt):
        self.failures = failures
        self.receipt = receipt
        self.calls = 0

    async def send(self, email: Email) -> Receipt:
        self.calls += 1
        if self.calls <= self.failures:
            raise Exception(f"Attempt {self.calls} failed")
        return self.receipt


class SlowDelivery(Delivery):
    def __init__(self, seconds: float, receipt: Receipt):
        self.seconds = seconds
        self.receipt = receipt

    async def send(self, email: Email) -> Receipt:
        await asyncio.sleep(self.seconds)
        return self.receipt


class FakeSendGrid:
    def __init__(self, response: httpx.Response):
        self.response = response
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.response


class Inbox:
    def __init__(self):
        self.envelopes = []

    async def handle_DATA(self, server, session, envelope) -> str:
        self.envelopes.append(envelope)
        return "250 OK"


class Port:
    def number(self) -> int:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]


class Server:
    def __init__(self, inbox: Inbox, port: int, user: str, password: str):
        self.inbox = inbox
        self.port = port
        self.user = user
        self.password = password

    def __enter__(self) -> Self:
        self.controller = Controller(
            self.inbox,
            hostname="127.0.0.1",
            port=self.port,
            authenticator=self._authenticator,
            auth_required=bool(self.user),
            auth_require_tls=False,
        )
        self.controller.start()
        return self

    def __exit__(self, *args) -> None:
        self.controller.stop()

    def _authenticator(self, server, session, envelope, mechanism, data):
        expected = LoginPassword(self.user.encode(), self.password.encode())
        return AuthResult(success=data == expected, handled=False)


def receipt(label: str) -> Receipt:
    return Confirmation(label, ("someone@example.com",), {})
