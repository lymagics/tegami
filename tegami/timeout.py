import asyncio

from tegami.delivery import Delivery
from tegami.email import Email
from tegami.receipt import Receipt


class Timeout(Delivery):
    def __init__(self, origin: Delivery, seconds: float):
        self.origin = origin
        self.seconds = seconds

    async def send(self, email: Email) -> Receipt:
        try:
            return await asyncio.wait_for(self.origin.send(email), self.seconds)
        except TimeoutError as e:
            raise Exception(f"Can't send email within {self.seconds} seconds") from e
