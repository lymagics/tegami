from email.message import EmailMessage
from email.utils import make_msgid

from tegami.part import Part


class Email:
    def __init__(self, *parts: Part):
        self.parts = parts

    def mime(self) -> EmailMessage:
        message = EmailMessage()
        message["Message-ID"] = make_msgid()
        for part in self.parts:
            part.write(message)
        return message
