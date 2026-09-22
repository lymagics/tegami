from abc import ABC, abstractmethod

from tegami.email import Email
from tegami.receipt import Receipt


class Delivery(ABC):
    @abstractmethod
    async def send(self, email: Email) -> Receipt:
        pass
