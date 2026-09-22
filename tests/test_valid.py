import pytest
from hamcrest import assert_that, calling, equal_to, raises

from tegami.address import Address, Valid


def test_passes_correct_address_through():
    assert_that(
        Valid(Address("ann@mail.example.net", "Ann")).value(),
        equal_to("Ann <ann@mail.example.net>"),
        "Valid must render a correct address unchanged",
    )


@pytest.mark.parametrize(
    "email",
    ["nobody", "", "user@localhost", "@missing.local", "two words@x.io", "cut@"],
)
def test_rejects_malformed_address(email: str):
    assert_that(
        calling(Valid(Address(email)).value),
        raises(Exception, "Invalid email address"),
        f"Valid must reject {email!r}",
    )
