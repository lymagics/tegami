import pytest
from hamcrest import assert_that, calling, equal_to, has_entry, has_key, is_not, raises

from tegami.address import Address
from tegami.content import Text
from tegami.email import Email
from tegami.headers import Bcc, Cc, From, ReplyTo, Subject, To
from tegami.sendgrid import Payload


def test_maps_recipients_into_personalization():
    payload = Payload(
        Email(
            From(Address("from@payload.example")),
            To(Address("to@payload.example", "Target")),
            Bcc(Address("bcc@payload.example")),
            Text("mapped"),
        ).mime()
    ).json()
    assert_that(
        payload["personalizations"],
        equal_to(
            [
                {
                    "to": [{"email": "to@payload.example", "name": "Target"}],
                    "bcc": [{"email": "bcc@payload.example"}],
                }
            ]
        ),
        "Payload must map To and Bcc into the first personalization",
    )


def test_maps_sender():
    payload = Payload(
        Email(
            From(Address("boss@payload.example", "The Boss")),
            To(Address("staff@payload.example")),
            Text("sender"),
        ).mime()
    ).json()
    assert_that(
        payload,
        has_entry("from", {"email": "boss@payload.example", "name": "The Boss"}),
        "Payload must map the From header to the sender object",
    )


def test_maps_reply_to_list():
    payload = Payload(
        Email(
            From(Address("noreply@payload.example")),
            To(Address("someone@payload.example")),
            ReplyTo(Address("answers@payload.example")),
            Text("reply"),
        ).mime()
    ).json()
    assert_that(
        payload,
        has_entry("reply_to_list", [{"email": "answers@payload.example"}]),
        "Payload must map Reply-To into reply_to_list",
    )


def test_maps_subject():
    payload = Payload(
        Email(
            From(Address("s@payload.example")),
            To(Address("t@payload.example")),
            Subject("Payload subject ✓"),
            Text("subject"),
        ).mime()
    ).json()
    assert_that(
        payload,
        has_entry("subject", "Payload subject ✓"),
        "Payload must copy the Subject header",
    )


def test_fails_clearly_without_from_header():
    payload = Payload(
        Email(
            To(Address("orphan@payload.example")),
            Text("nobody sent this"),
        ).mime()
    )
    assert_that(
        calling(payload.json),
        raises(Exception, "From"),
        "Payload must raise a clear error when the email has no From header",
    )


def test_omits_subject_when_email_has_none():
    payload = Payload(
        Email(
            From(Address("quiet@payload.example")),
            To(Address("mute@payload.example")),
            Text("no subject line"),
        ).mime()
    ).json()
    assert_that(
        payload,
        is_not(has_key("subject")),
        "Payload must not invent a subject when the Subject header is absent",
    )


def test_omits_empty_sections():
    payload = Payload(
        Email(
            From(Address("lean@payload.example")),
            To(Address("mean@payload.example")),
            Text("no extras"),
        ).mime()
    ).json()
    assert_that(
        payload,
        is_not(has_key("attachments")),
        "Payload must leave out sections that have nothing in them",
    )


# TODO: Bug: Payload repeats a recipient https://github.com/lymagics/tegami/pull/59
@pytest.mark.skip(
    reason="Bug: Payload repeats a recipient "
    "https://github.com/lymagics/tegami/pull/59"
)
def test_lists_recipient_repeated_in_to_and_cc_once():
    personalization = Payload(
        Email(
            From(Address("dup-from@payload.example")),
            To(Address("twice-7@payload.example")),
            Cc(Address("twice-7@payload.example")),
            Text("repeated across fields"),
        ).mime()
    ).json()["personalizations"][0]
    assert_that(
        personalization,
        equal_to({"to": [{"email": "twice-7@payload.example"}]}),
        "Payload must list a recipient repeated in to and cc once",
    )
