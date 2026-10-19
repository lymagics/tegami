from email.message import EmailMessage

import pytest
from hamcrest import assert_that, calling, equal_to, raises

from tegami.headers import Subject


def test_writes_unicode_subject():
    message = EmailMessage()
    Subject("Héllo wörld — 日本語").write(message)
    assert_that(
        str(message["Subject"]),
        equal_to("Héllo wörld — 日本語"),
        "Subject must keep unicode text intact",
    )


# TODO: Bug: line break raises ValueError https://github.com/lymagics/tegami/pull/37
@pytest.mark.skip(
    reason="Bug: Subject line break raises ValueError "
    "https://github.com/lymagics/tegami/pull/37"
)
def test_rejects_subject_with_line_break_using_plain_exception():
    assert_that(
        calling(Subject("Invoice\r\nBcc: x@y.zz").write).with_args(EmailMessage()),
        raises(Exception, "Can't write subject"),
        "Subject must reject a subject with a line break using a plain exception",
    )
