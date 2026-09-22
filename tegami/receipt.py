from abc import ABC, abstractmethod
from collections.abc import Mapping


class Receipt(ABC):
    @abstractmethod
    def id(self) -> str:
        pass

    @abstractmethod
    def recipients(self) -> tuple[str, ...]:
        pass

    @abstractmethod
    def metadata(self) -> Mapping[str, str]:
        pass


class Confirmation(Receipt):
    def __init__(
        self,
        label: str,
        addresses: tuple[str, ...],
        details: Mapping[str, str],
    ):
        self.label = label
        self.addresses = addresses
        self.details = details

    def id(self) -> str:
        return self.label

    def recipients(self) -> tuple[str, ...]:
        return self.addresses

    def metadata(self) -> Mapping[str, str]:
        return self.details
