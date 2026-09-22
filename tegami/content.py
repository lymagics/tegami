from email.message import EmailMessage

from tegami.part import Part


class Text(Part):
    def __init__(self, body: str):
        self.body = body

    def write(self, message: EmailMessage) -> None:
        message.set_content(self.body)


class Html(Part):
    def __init__(self, body: str):
        self.body = body

    def write(self, message: EmailMessage) -> None:
        message.set_content(self.body, subtype="html")


class Multipart(Part):
    def __init__(self, *parts: Part):
        self.parts = parts

    def write(self, message: EmailMessage) -> None:
        message.make_alternative()
        for part in self.parts:
            alternative = EmailMessage(policy=message.policy)
            part.write(alternative)
            message.attach(alternative)
