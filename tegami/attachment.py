import mimetypes
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


class Mime:
    def __init__(self, name: str):
        self.name = name

    def value(self) -> str:
        kind, _ = mimetypes.guess_type(self.name)
        return kind or "application/octet-stream"


class Attachment(Part):
    @dispatch
    def __init__(self, name: str, blob: Blob):
        self.__init__(name, blob, Mime(name).value())

    @dispatch
    def __init__(self, name: str, blob: Blob, kind: str):
        self.name = name
        self.blob = blob
        self.kind = kind

    def write(self, message: EmailMessage) -> None:
        maintype, subtype = self.kind.split("/", 1)
        message.add_attachment(
            self.blob.bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=self.name,
        )
