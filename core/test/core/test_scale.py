from test.conftest import RemovebgMessage
from test.core.helpers import process_image
from test.helpers import compute_scale_pos

from tests.utils import convert_to_image, read_image


def _test_scale(core_server_tester, scale_factor):
    msg = RemovebgMessage()
    im_in_bytes = read_image("../data/CMYK.jpg")
    im_in = convert_to_image(im_in_bytes)
    msg.channels = "alpha"
    msg.data = im_in_bytes
    msg.scale = scale_factor
    msg.roi = [0, 0, 396, 639]
    im = process_image(core_server_tester, msg)["im"]

    assert im_in.width == im.width
    assert im_in.height == im.height

    scale, pos = compute_scale_pos(im)

    assert abs(scale - scale_factor / 100) < 1e-3
    assert pos == (im_in.width // 2.0, im_in.height // 2.0)


def test_small(core_server_tester):
    _test_scale(core_server_tester, 10)


def test_half(core_server_tester):
    _test_scale(core_server_tester, 50)


def test_full(core_server_tester):
    _test_scale(core_server_tester, 100)
