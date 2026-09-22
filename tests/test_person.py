from hamcrest import assert_that, equal_to

from tegami.sendgrid import Person


def test_includes_name_when_present():
    assert_that(
        Person("Ada Lovelace", "ada@person.example").json(),
        equal_to({"email": "ada@person.example", "name": "Ada Lovelace"}),
        "Person must include a non-empty name",
    )


def test_omits_empty_name():
    assert_that(
        Person("", "nameless@person.example").json(),
        equal_to({"email": "nameless@person.example"}),
        "Person must omit an empty name",
    )
