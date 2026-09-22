from abc import ABC, abstractmethod
from email.message import EmailMessage


class Part(ABC):
    @abstractmethod
    def write(self, message: EmailMessage) -> None:
        pass
