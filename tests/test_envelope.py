from email.message import EmailMessage

import pytest
from hamcrest import assert_that, contains_exactly, equal_to, none

from tegami.envelope import Envelope


def test_collects_recipients_from_all_headers():
    message = EmailMessage()
    message["To"] = "Primary <p@env.example>"
    message["Cc"] = "c1@env.example, c2@env.example"
    message["Bcc"] = "hidden@env.example"
    assert_that(
        Envelope(message).recipients(),
        contains_exactly(
            "p@env.example", "c1@env.example", "c2@env.example", "hidden@env.example"
        ),
        "Envelope must gather To, Cc and Bcc recipients in order",
    )


def test_strips_bcc_from_content():
    message = EmailMessage()
    message["To"] = "visible@env.example"
    message["Bcc"] = "invisible@env.example"
    assert_that(
        Envelope(message).content()["Bcc"],
        none(),
        "Envelope content must not carry a Bcc header",
    )


def test_keeps_original_message_intact():
    message = EmailMessage()
    message["Bcc"] = "still@env.example"
    Envelope(message).content()
    assert_that(
        str(message["Bcc"]),
        equal_to("still@env.example"),
        "Envelope must not mutate the original message",
    )


# TODO: Bug: Envelope lists an address twice when it is in To and Cc, https://github.com/lymagics/tegami/pull/26
@pytest.mark.skip(
    reason="Bug: Envelope lists an address twice when it is in To and Cc, "
    "https://github.com/lymagics/tegami/pull/26"
)
def test_lists_a_repeated_recipient_once():
    message = EmailMessage()
    message["To"] = "twin@dup.example, other@dup.example"
    message["Cc"] = "twin@dup.example"
    assert_that(
        Envelope(message).recipients(),
        contains_exactly("twin@dup.example", "other@dup.example"),
        "Envelope must list an address once even if it is in To and Cc",
    )
