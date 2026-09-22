import pytest
from hamcrest import assert_that, equal_to

from tegami.attachment import Mime


@pytest.mark.parametrize(
    "name, kind",
    [
        ("report.PDF", "application/pdf"),
        ("photo.jpeg", "image/jpeg"),
        ("data.json", "application/json"),
        ("archive.tar.gz", "application/x-tar"),
    ],
)
def test_guesses_type_from_name(name: str, kind: str):
    assert_that(
        Mime(name).value(),
        equal_to(kind),
        f"Mime must guess {kind} for {name}",
    )


def test_falls_back_to_octet_stream():
    assert_that(
        Mime("blob.unknownext").value(),
        equal_to("application/octet-stream"),
        "Mime must fall back to octet-stream for unknown names",
    )
