from tegami.delivery import Delivery
from tegami.email import Email
from tegami.receipt import Receipt
from tegami.transport import Transport


class Courier(Delivery):
    def __init__(self, transport: Transport):
        self.transport = transport

    async def send(self, email: Email) -> Receipt:
        return await self.transport.deliver(email.mime())
