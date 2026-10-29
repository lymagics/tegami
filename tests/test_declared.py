from hamcrest import assert_that, equal_to

from tegami.attachment import Declared


def test_keeps_given_content_type():
    assert_that(
        Declared("model/vnd.gltf+json").value(),
        equal_to("model/vnd.gltf+json"),
        "Declared must return the content type it was given",
    )
