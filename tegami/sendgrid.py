import base64
from email.message import EmailMessage
from email.utils import getaddresses

import httpx
from plum import dispatch

from tegami.envelope import Envelope
from tegami.receipt import Confirmation, Receipt
from tegami.transport import Transport


class Person:
    def __init__(self, name: str, spec: str):
        self.name = name
        self.spec = spec

    def json(self) -> dict:
        person = {"email": self.spec}
        if self.name:
            person["name"] = self.name
        return person


class People:
    def __init__(self, message: EmailMessage, header: str):
        self.message = message
        self.header = header

    def json(self) -> list[dict]:
        return [
            Person(name, spec).json()
            for name, spec in getaddresses(self.message.get_all(self.header, ()))
        ]


class Contents:
    def __init__(self, message: EmailMessage):
        self.message = message

    def json(self) -> list[dict]:
        return [
            {"type": part.get_content_type(), "value": part.get_content()}
            for part in self.message.walk()
            if part.get_content_maintype() == "text" and not part.is_attachment()
        ]


class Attachments:
    def __init__(self, message: EmailMessage):
        self.message = message

    def json(self) -> list[dict]:
        return [
            {
                "content": base64.b64encode(part.get_payload(decode=True)).decode(),
                "type": part.get_content_type(),
                "filename": part.get_filename(),
                "disposition": "attachment",
            }
            for part in self.message.iter_attachments()
        ]


class Payload:
    def __init__(self, message: EmailMessage):
        self.message = message

    def json(self) -> dict:
        body = {
            "personalizations": [self._personalization()],
            "from": People(self.message, "From").json()[0],
            "reply_to_list": People(self.message, "Reply-To").json(),
            "subject": str(self.message["Subject"]),
            "content": Contents(self.message).json(),
            "attachments": Attachments(self.message).json(),
        }
        return {key: value for key, value in body.items() if value}

    def _personalization(self) -> dict:
        targets = {
            "to": People(self.message, "To").json(),
            "cc": People(self.message, "Cc").json(),
            "bcc": People(self.message, "Bcc").json(),
        }
        return {key: value for key, value in targets.items() if value}


class SendGrid(Transport):
    @dispatch
    def __init__(self, key: str):
        self.__init__(key, httpx.AsyncHTTPTransport())

    @dispatch
    def __init__(self, key: str, transport: httpx.AsyncBaseTransport):
        self.key = key
        self.transport = transport

    async def deliver(self, message: EmailMessage) -> Receipt:
        try:
            async with httpx.AsyncClient(
                base_url="https://api.sendgrid.com",
                transport=self.transport,
            ) as client:
                response = await client.post(
                    "/v3/mail/send",
                    json=Payload(message).json(),
                    headers={"Authorization": f"Bearer {self.key}"},
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"SendGrid rejected email {message['Message-ID']}: "
                f"{e.response.text}"
            ) from e
        except httpx.HTTPError as e:
            raise Exception(
                f"Can't deliver email {message['Message-ID']} through SendGrid"
            ) from e
        return Confirmation(
            response.headers["X-Message-Id"],
            Envelope(message).recipients(),
            {"status": str(response.status_code)},
        )
