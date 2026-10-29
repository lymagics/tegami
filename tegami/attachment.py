import mimetypes
import re
from abc import ABC, abstractmethod
from email.message import EmailMessage
from pathlib import Path

from plum import dispatch

from tegami.part import Part


class Blob(ABC):
    @abstractmethod
    def bytes(self) -> bytes:
        pass


class Bytes(Blob):
    def __init__(self, content: bytes):
        self.content = content

    def bytes(self) -> bytes:
        return self.content


class File(Blob):
    def __init__(self, path: Path):
        self.path = path

    def bytes(self) -> bytes:
        try:
            return self.path.read_bytes()
        except OSError as e:
            raise Exception(f"Can't read attachment file {self.path}") from e


class Kind(ABC):
    @abstractmethod
    def value(self) -> str:
        pass


class Mime(Kind):
    def __init__(self, name: str):
        self.name = name

    def value(self) -> str:
        kind, _ = mimetypes.guess_type(self.name)
        return kind or "application/octet-stream"


class Declared(Kind):
    def __init__(self, text: str):
        self.text = text

    def value(self) -> str:
        return self.text


class Strict(Kind):
    def __init__(self, origin: Kind):
        self.origin = origin

    def value(self) -> str:
        text = self.origin.value()
        if not re.fullmatch(r"[^/\s]+/[^/\s]+", text):
            raise Exception(f"Invalid content type: {text!r}")
        return text


class Attachment(Part):
    @dispatch
    def __init__(self, name: str, blob: Blob):
        self.__init__(name, blob, Mime(name))

    @dispatch
    def __init__(self, name: str, blob: Blob, kind: str):
        self.__init__(name, blob, Strict(Declared(kind)))

    @dispatch
    def __init__(self, name: str, blob: Blob, kind: Kind):
        self.name = name
        self.blob = blob
        self.kind = kind

    def write(self, message: EmailMessage) -> None:
        maintype, subtype = self.kind.value().split("/", 1)
        message.add_attachment(
            self.blob.bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=self.name,
        )
