from email.message import EmailMessage

from tegami.address import Mailbox
from tegami.part import Part


class Mailboxes(Part):
    def __init__(self, header: str, *addresses: Mailbox):
        self.header = header
        self.addresses = addresses

    def write(self, message: EmailMessage) -> None:
        message[self.header] = ", ".join(address.value() for address in self.addresses)


class From(Part):
    def __init__(self, address: Mailbox):
        self.address = address

    def write(self, message: EmailMessage) -> None:
        Mailboxes("From", self.address).write(message)


class To(Part):
    def __init__(self, *addresses: Mailbox):
        self.addresses = addresses

    def write(self, message: EmailMessage) -> None:
        Mailboxes("To", *self.addresses).write(message)


class Cc(Part):
    def __init__(self, *addresses: Mailbox):
        self.addresses = addresses

    def write(self, message: EmailMessage) -> None:
        Mailboxes("Cc", *self.addresses).write(message)


class Bcc(Part):
    def __init__(self, *addresses: Mailbox):
        self.addresses = addresses

    def write(self, message: EmailMessage) -> None:
        Mailboxes("Bcc", *self.addresses).write(message)


class ReplyTo(Part):
    def __init__(self, *addresses: Mailbox):
        self.addresses = addresses

    def write(self, message: EmailMessage) -> None:
        Mailboxes("Reply-To", *self.addresses).write(message)


class Subject(Part):
    def __init__(self, text: str):
        self.text = text

    def write(self, message: EmailMessage) -> None:
        message["Subject"] = self.text
