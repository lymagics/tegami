import copy
from email.message import EmailMessage
from email.utils import getaddresses


class Envelope:
    def __init__(self, message: EmailMessage):
        self.message = message

    def recipients(self) -> tuple[str, ...]:
        return tuple(
            spec
            for header in ("To", "Cc", "Bcc")
            for _, spec in getaddresses(self.message.get_all(header, ()))
        )

    def content(self) -> EmailMessage:
        stripped = copy.copy(self.message)
        del stripped["Bcc"]
        return stripped
