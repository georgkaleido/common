from test.conftest import RemovebgMessage

from tests.utils import read_image


def test_no_foreground(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "jpg"
    msg.data = read_image("../data/white.jpg")
    result = core_server_tester.request(msg.serialize())
    assert result[b"status"] == b"error"


def test_truncated(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "jpg"
    msg.data = read_image("../data/truncated.jpg")
    result = core_server_tester.request(msg.serialize())
    assert result[b"status"] == b"error"
