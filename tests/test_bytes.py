from hamcrest import assert_that, equal_to
from hypothesis import given
from hypothesis import strategies as st

from tegami.attachment import Bytes


@given(st.binary())
def test_returns_given_bytes(data: bytes):
    assert_that(
        Bytes(data).bytes(),
        equal_to(data),
        "Bytes must return exactly the bytes it holds",
    )
