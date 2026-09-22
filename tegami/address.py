import re
from abc import ABC, abstractmethod
from email.utils import formataddr, parseaddr

from plum import dispatch


class Mailbox(ABC):
    @abstractmethod
    def value(self) -> str:
        pass


class Address(Mailbox):
    @dispatch
    def __init__(self, email: str):
        self.__init__(email, "")

    @dispatch
    def __init__(self, email: str, name: str):
        self.email = email
        self.name = name

    def value(self) -> str:
        return formataddr((self.name, self.email))


class Valid(Mailbox):
    def __init__(self, origin: Mailbox):
        self.origin = origin

    def value(self) -> str:
        text = self.origin.value()
        _, spec = parseaddr(text)
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", spec):
            raise Exception(f"Invalid email address: {text}")
        return text
