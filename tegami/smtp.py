from abc import ABC, abstractmethod
from email.message import EmailMessage

import aiosmtplib

from tegami.envelope import Envelope
from tegami.receipt import Confirmation, Receipt
from tegami.transport import Transport


class Credentials(ABC):
    @abstractmethod
    async def authenticate(self, client: aiosmtplib.SMTP) -> None:
        pass


class Login(Credentials):
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password

    async def authenticate(self, client: aiosmtplib.SMTP) -> None:
        await client.login(self.user, self.password)


class Anonymous(Credentials):
    async def authenticate(self, client: aiosmtplib.SMTP) -> None:
        pass


class Smtp(Transport):
    def __init__(self, host: str, port: int, credentials: Credentials):
        self.host = host
        self.port = port
        self.credentials = credentials

    async def deliver(self, message: EmailMessage) -> Receipt:
        envelope = Envelope(message)
        try:
            async with aiosmtplib.SMTP(
                hostname=self.host,
                port=self.port,
                use_tls=self.port == 465,
                start_tls=self.port == 587,
            ) as client:
                await self.credentials.authenticate(client)
                refused, response = await client.send_message(
                    envelope.content(),
                    recipients=envelope.recipients(),
                )
        except aiosmtplib.SMTPException as e:
            raise Exception(
                f"Can't deliver email {message['Message-ID']} "
                f"through {self.host}:{self.port}"
            ) from e
        return Confirmation(
            str(message["Message-ID"]),
            tuple(r for r in envelope.recipients() if r not in refused),
            {"response": response},
        )
