from plum import dispatch
from tenacity import AsyncRetrying, stop_after_attempt, wait_fixed

from tegami.delivery import Delivery
from tegami.email import Email
from tegami.receipt import Receipt


class Retry(Delivery):
    @dispatch
    def __init__(self, origin: Delivery, attempts: int):
        self.__init__(origin, attempts, 1.0)

    @dispatch
    def __init__(self, origin: Delivery, attempts: int, delay: float):
        self.origin = origin
        self.attempts = attempts
        self.delay = delay

    async def send(self, email: Email) -> Receipt:
        retrying = AsyncRetrying(
            stop=stop_after_attempt(self.attempts),
            wait=wait_fixed(self.delay),
            reraise=True,
        )
        return await retrying(self.origin.send, email)
