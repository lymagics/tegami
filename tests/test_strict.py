import pytest
from hamcrest import assert_that, calling, equal_to, raises

from tegami.attachment import Declared, Strict


def test_passes_wellformed_content_type_through():
    assert_that(
        Strict(Declared("application/vnd.ms-excel")).value(),
        equal_to("application/vnd.ms-excel"),
        "Strict must return a well-formed content type unchanged",
    )


@pytest.mark.parametrize(
    "kind",
    ["", "/", "plain", "image/", "/png", "text/x/y", "audio/ ogg", " video/mp4"],
)
def test_rejects_malformed_content_type(kind: str):
    assert_that(
        calling(Strict(Declared(kind)).value),
        raises(Exception, "Invalid content type"),
        f"Strict must reject {kind!r}",
    )
