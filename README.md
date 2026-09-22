# Tegami

[![EO principles respected here](https://www.elegantobjects.org/badge.svg)](https://www.elegantobjects.org)

<img src="tegami.png" width=125 height=125 alt="Tegami" />

**Tegami** (手紙, "letter" in Japanese) is a small, object-oriented Python library for sending email.

You build an email from small objects. You build a way to send it from small objects. Then you put them together.

```python
from tegami import Address, Courier, Email, From, Html, Login, Smtp, Subject, To

courier = Courier(
    Smtp(
        "smtp.example.com",
        587,
        Login("alice", "secret"),
    ),
)

receipt = await courier.send(
    Email(
        From(Address("alice@example.com", "Alice")),
        To(
            Address("bob@example.com"),
            Address("charlie@example.com"),
        ),
        Subject("Hello"),
        Html("<h1>Hello!</h1>"),
    ),
)

print(receipt.id())
```

- **Async first.** Every call that touches the network is `await`-able.
- **Two transports out of the box.** SMTP and SendGrid.
- **Composable.** Add retries, timeouts, logging or anything else by wrapping.
- **No surprises.** Immutable objects, no global config, one exception type.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Building an Email](#building-an-email)
   - [Addresses](#addresses)
   - [Recipients](#recipients)
   - [Subject](#subject)
   - [Plain Text and HTML](#plain-text-and-html)
   - [Text and HTML Together](#text-and-html-together)
   - [Attachments](#attachments)
4. [Sending](#sending)
   - [SMTP](#smtp)
   - [SendGrid](#sendgrid)
   - [Receipts](#receipts)
5. [Adding Behavior](#adding-behavior)
   - [Retry](#retry)
   - [Timeout](#timeout)
   - [Stacking Decorators](#stacking-decorators)
   - [Writing Your Own Decorator](#writing-your-own-decorator)
6. [Error Handling](#error-handling)
7. [Extending Tegami](#extending-tegami)
   - [Your Own Attachment Source](#your-own-attachment-source)
   - [Your Own Transport](#your-own-transport)
8. [Testing Your Code](#testing-your-code)
9. [Development](#development)
10. [License](#license)

---

## Installation

Tegami requires Python 3.11 or newer.

```bash
pip install tegami
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add tegami
```

---

## Quick Start

```python
import asyncio

from tegami import Address, Courier, Email, From, Login, Smtp, Subject, Text, To


async def main() -> None:
    courier = Courier(
        Smtp(
            "smtp.example.com",
            587,
            Login("alice", "secret"),
        ),
    )
    receipt = await courier.send(
        Email(
            From(Address("alice@example.com")),
            To(Address("bob@example.com")),
            Subject("Lunch?"),
            Text("Are you free at noon?"),
        ),
    )
    print(f"Sent as {receipt.id()} to {receipt.recipients()}")


asyncio.run(main())
```

That is the whole library in one picture:

```
Email  ──►  Courier  ──►  Transport  ──►  the world
(what)      (how)         (where)
```

---

## Building an Email

An `Email` is a list of parts. Every header, body and attachment is a part.
Pass them in the order you want them written.

```python
from tegami import Email

email = Email(
    From(...),
    To(...),
    Subject(...),
    Text(...),
    Attachment(...),
)
```

> **Tip:** put content (`Text`, `Html`, `Multipart`) before attachments.

Emails are immutable. To change one, build a new one.

### Addresses

An `Address` is an email with an optional display name.

```python
from tegami import Address

Address("bob@example.com")                # bob@example.com
Address("bob@example.com", "Bob Smith")   # Bob Smith <bob@example.com>
```

`Address` does not validate. When you take addresses from user input, wrap them in `Valid`.
It raises a clear error the moment the address is used.

```python
from tegami import Address, To, Valid

To(Valid(Address(user_input)))
```

### Recipients

| Class     | Header     | Takes                 |
|-----------|------------|-----------------------|
| `From`    | `From`     | exactly one address   |
| `To`      | `To`       | one or more addresses |
| `Cc`      | `Cc`       | one or more addresses |
| `Bcc`     | `Bcc`      | one or more addresses |
| `ReplyTo` | `Reply-To` | one or more addresses |

```python
from tegami import Address, Bcc, Cc, Email, From, ReplyTo, To

Email(
    From(Address("news@example.com", "Example News")),
    To(
        Address("bob@example.com"),
        Address("charlie@example.com"),
    ),
    Cc(
        Address("manager@example.com"),
    ),
    Bcc(
        Address("archive@example.com"),
    ),
    ReplyTo(
        Address("support@example.com"),
    ),
    ...
)
```

`Bcc` recipients receive the email, but the `Bcc` header is stripped before sending.
Nobody else sees them.

### Subject

```python
from tegami import Subject

Subject("Your invoice for September")
```

Unicode is fine.

### Plain Text and HTML

```python
from tegami import Html, Text

Text("Hello, Bob!")
Html("<h1>Hello, Bob!</h1>")
```

Use one of them as the body of your email.

### Text and HTML Together

`Multipart` sends both. The mail client shows the best one it can render.
Put the plain text first. It is the fallback.

```python
from tegami import Html, Multipart, Text

Multipart(
    Text("Hello, Bob!"),
    Html("<h1>Hello, Bob!</h1>"),
)
```

### Attachments

An `Attachment` has a file name and a source of bytes.

```python
from pathlib import Path

from tegami import Attachment, Bytes, File

Attachment("invoice.pdf", File(Path("./invoice.pdf")))
Attachment("report.csv", Bytes(b"date,amount\n2024-09-01,42.00\n"))
```

- `File` reads the path only when the email is sent, not when you create it.
- The MIME type is guessed from the file name.
- Give it explicitly as a third argument when the guess is not enough:

```python
Attachment("data.bin", Bytes(payload), "application/x-custom")
```

A complete email with everything:

```python
from pathlib import Path

from tegami import (
    Address,
    Attachment,
    Bcc,
    Email,
    File,
    From,
    Html,
    Multipart,
    ReplyTo,
    Subject,
    Text,
    To,
)

email = Email(
    From(Address("billing@example.com", "Example Billing")),
    To(
        Address("bob@example.com", "Bob Smith"),
    ),
    Bcc(
        Address("archive@example.com"),
    ),
    ReplyTo(
        Address("support@example.com"),
    ),
    Subject("Your invoice for September"),
    Multipart(
        Text("Hi Bob, your invoice is attached."),
        Html("<p>Hi Bob, your invoice is <b>attached</b>.</p>"),
    ),
    Attachment("invoice.pdf", File(Path("invoices/september.pdf"))),
)
```

---

## Sending

A `Courier` sends an `Email` through a transport and gives you a receipt.

```python
from tegami import Courier

courier = Courier(transport)
receipt = await courier.send(email)
```

### SMTP

```python
from tegami import Anonymous, Login, Smtp

Smtp(
    "smtp.example.com",
    587,
    Login("alice", "secret"),
)

Smtp(
    "localhost",
    1025,
    Anonymous(),
)
```

Use `Login` for servers that need a user name and password, and `Anonymous` for those that do not.

TLS is picked by port:

| Port  | Mode          |
|-------|---------------|
| 465   | implicit TLS  |
| 587   | STARTTLS      |
| other | plain         |

Each send opens a connection, sends, and closes it. Simple and safe.

### SendGrid

```python
from tegami import SendGrid

SendGrid("SG.your-api-key")
```

SendGrid talks HTTP, so your `Email` is converted to the JSON the
[SendGrid v3 Mail Send API](https://docs.sendgrid.com/api-reference/mail-send/mail-send) expects.
Headers, bodies and attachments all map across. You do not need to do anything different.

### Receipts

`send` returns a `Receipt`, the proof that the provider accepted your email.

```python
receipt = await courier.send(email)

receipt.id()          # message id known to the provider
receipt.recipients()  # addresses the provider accepted
receipt.metadata()    # extra provider data, e.g. the raw SMTP reply
```

Receipts are immutable and safe to log.

---

## Adding Behavior

`Courier` implements the `Delivery` interface. So do `Retry` and `Timeout`.
Anything that implements `Delivery` can wrap anything else that does.

```python
from tegami import Courier, Delivery, Smtp

delivery: Delivery = Courier(Smtp(...))
```

### Retry

Try up to N times before giving up. The last error is raised if every attempt fails.

```python
from tegami import Courier, Retry, Smtp

Retry(
    Courier(Smtp(...)),
    3,
)

Retry(
    Courier(Smtp(...)),
    5,
    0.2,
)
```

The first one makes three attempts one second apart. The second makes five attempts
with a pause of 0.2 seconds between them.

### Timeout

Give up after a number of seconds.

```python
from tegami import Courier, Smtp, Timeout

Timeout(
    Courier(Smtp(...)),
    10,
)
```

### Stacking Decorators

Wrap in any order. Read it inside out.

```python
from tegami import Courier, Login, Retry, Smtp, Timeout

delivery = Timeout(
    Retry(
        Courier(
            Smtp(
                "smtp.example.com",
                587,
                Login("alice", "secret"),
            ),
        ),
        3,
    ),
    30,
)

receipt = await delivery.send(email)
```

This one retries three times, and the whole thing must finish within thirty seconds.

### Writing Your Own Decorator

Implement `Delivery`, hold another `Delivery`, and do your thing around it.

```python
import logging

from tegami import Courier, Delivery, Email, Receipt, Retry, Smtp


class Logged(Delivery):
    def __init__(self, origin: Delivery, log: logging.Logger):
        self.origin = origin
        self.log = log

    async def send(self, email: Email) -> Receipt:
        receipt = await self.origin.send(email)
        self.log.info("Sent %s to %s", receipt.id(), receipt.recipients())
        return receipt


delivery = Logged(
    Retry(
        Courier(Smtp(...)),
        3,
    ),
    logging.getLogger("mail"),
)
```

Good candidates: logging, rate limits, dry runs, metrics.

---

## Error Handling

Tegami raises only one type: the built-in `Exception`.

Every vendor error is caught and re-raised with a clear message. The original error
is attached as the cause, so nothing is lost.

```python
try:
    receipt = await delivery.send(email)
except Exception as error:
    print(error)            # Can't deliver email <...> through smtp.example.com:587
    print(error.__cause__)  # the original aiosmtplib or httpx error
```

Catch it once, at the top of your application.

---

## Extending Tegami

### Your Own Attachment Source

Implement `Blob` to load attachment bytes from anywhere.

```python
from tegami import Attachment, Blob


class S3Object(Blob):
    def __init__(self, bucket: str, key: str):
        self.bucket = bucket
        self.key = key

    def bytes(self) -> bytes:
        body = boto3.client("s3").get_object(Bucket=self.bucket, Key=self.key)["Body"]
        return body.read()


Attachment("report.pdf", S3Object("reports", "2024/september.pdf"))
```

### Your Own Transport

Implement `Transport` to send through a new provider. You receive a standard
`email.message.EmailMessage` and return a `Receipt`.

```python
from email.message import EmailMessage

from tegami import Confirmation, Courier, Receipt, Transport


class Postmark(Transport):
    def __init__(self, token: str):
        self.token = token

    async def deliver(self, message: EmailMessage) -> Receipt:
        ...  # call the provider
        return Confirmation(
            provider_id,
            recipients,
            {"status": "queued"},
        )


courier = Courier(Postmark("your-token"))
```

Everything else, including `Retry` and `Timeout`, works with it unchanged.

---

## Testing Your Code

Because everything is an interface, you never need to mock. Write a fake.

```python
from email.message import EmailMessage

from tegami import Confirmation, Courier, Receipt, Transport


class FakeTransport(Transport):
    def __init__(self):
        self.messages: list[EmailMessage] = []

    async def deliver(self, message: EmailMessage) -> Receipt:
        self.messages.append(message)
        return Confirmation("fake-id", ("bob@example.com",), {})


transport = FakeTransport()
await Courier(transport).send(email)

assert transport.messages[0]["Subject"] == "Lunch?"
```

---

## Development

```bash
make sync     # install dependencies with uv
make unit     # run tests with coverage
make lint     # black, flake8 and ruff
make help     # list all commands
```

Tests run against a local SMTP server and a fake SendGrid API. No internet needed.

---

## License

MIT. See [LICENSE](LICENSE).
