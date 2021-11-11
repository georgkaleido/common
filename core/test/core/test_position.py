from test.conftest import RemovebgMessage
from test.core.helpers import process_image
from test.helpers import compute_scale_pos

import numpy as np
from tests.utils import convert_to_image, read_image


def test_original(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/CMYK.jpg")
    msg.channels = "alpha"
    im_ref = process_image(core_server_tester, msg)["im"]
    im = process_image(core_server_tester, msg)["im"]
    assert (np.array(im) == np.array(im_ref)).all()


def _test_position(core_server_tester, position):
    msg = RemovebgMessage()
    im_in_bytes = read_image("../data/CMYK.jpg")
    im_in = convert_to_image(im_in_bytes)
    msg.data = im_in_bytes
    msg.channels = "alpha"
    msg.position = position
    im = process_image(core_server_tester, msg)["im"]
    return im_in, im


def test_center(core_server_tester):
    im_in, im = _test_position(core_server_tester, {"x": 50, "y": 50})
    assert im_in.width == im.width
    assert im_in.height == im.height
    # check if its centered
    assert compute_scale_pos(im)[1] == (im_in.width // 2.0, im_in.height // 2.0)


def test_lt(core_server_tester):
    im_in, im = _test_position(core_server_tester, {"x": 0, "y": 0})
    assert im_in.width == im.width
    assert im_in.height == im.height
    assert np.array(im)[0].any()
    assert np.array(im)[:, 0].any()


def test_tr(core_server_tester):
    im_in, im = _test_position(core_server_tester, {"x": 100, "y": 0})
    assert im_in.width == im.width
    assert im_in.height == im.height
    assert np.array(im)[0].any()
    assert np.array(im)[:, -1].any()


def test_lb(core_server_tester):
    im_in, im = _test_position(core_server_tester, {"x": 0, "y": 100})
    assert im_in.width == im.width
    assert im_in.height == im.height
    assert np.array(im)[-1].any()
    assert np.array(im)[:, 0].any()


def test_br(core_server_tester):
    im_in, im = _test_position(core_server_tester, {"x": 100, "y": 100})
    assert im_in.width == im.width
    assert im_in.height == im.height
    assert np.array(im)[-1].any()
    assert np.array(im)[:, -1].any()
