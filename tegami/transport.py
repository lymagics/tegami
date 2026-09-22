from abc import ABC, abstractmethod
from email.message import EmailMessage

from tegami.receipt import Receipt


class Transport(ABC):
    @abstractmethod
    async def deliver(self, message: EmailMessage) -> Receipt:
        pass
