import shutil
from pathlib import Path

from hamcrest import assert_that, calling, equal_to, raises

from tegami.attachment import File


def test_reads_bytes_from_disk():
    folder = Path(__file__).parent.parent / "tmp" / "file_reads_bytes"
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    (folder / "note.bin").write_bytes(b"\x00\x01\xfe\xff")
    assert_that(
        File(folder / "note.bin").bytes(),
        equal_to(b"\x00\x01\xfe\xff"),
        "File must read the bytes stored on disk",
    )


def test_fails_on_missing_file():
    folder = Path(__file__).parent.parent / "tmp" / "file_missing"
    shutil.rmtree(folder, ignore_errors=True)
    assert_that(
        calling(File(folder / "ghost.pdf").bytes),
        raises(Exception, "Can't read attachment file"),
        "File must fail clearly when the path does not exist",
    )
