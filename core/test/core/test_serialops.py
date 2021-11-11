from test.conftest import RemovebgMessage
from test.core.helpers import process_image
from test.helpers import compute_scale_pos

import numpy as np
from tests.utils import read_image


def _test_crop_scale_pos(core_server_tester, roi, scale, position, crop_margin, bg_color=None):
    msg = RemovebgMessage()
    msg.data = read_image("../data/CMYK.jpg")
    msg.crop = True
    msg.channels = "alpha"
    msg.roi = roi
    im_ref = process_image(core_server_tester, msg)["im"]

    msg.crop_margin = crop_margin
    msg.scale = scale
    msg.position = position
    if bg_color:
        msg.bg_color = bg_color
    im = process_image(core_server_tester, msg)["im"]
    return im_ref, im


def test_crop_scale_pos1(core_server_tester):
    im_ref, im = _test_crop_scale_pos(
        core_server_tester,
        [0, 0, 396, 639],
        50,
        {"x": 50, "y": 50},
        {
            "top": 100,
            "top_relative": False,
            "right": 100,
            "right_relative": False,
            "bottom": 100,
            "bottom_relative": False,
            "left": 100,
            "left_relative": False,
        },
    )

    assert im.width == im_ref.width + 200
    assert im.height == im_ref.height + 200

    scale, pos = compute_scale_pos(im)

    assert abs(scale - 0.5) < 1e-3
    assert pos == (im.width // 2.0, im.height // 2.0)


def test_crop_scale_pos2(core_server_tester):
    im_ref, im = _test_crop_scale_pos(
        core_server_tester,
        [0, 0, 396, 639],
        20,
        {"x": 100, "y": 100},
        {
            "top": 7,
            "top_relative": False,
            "right": 7,
            "right_relative": False,
            "bottom": 7,
            "bottom_relative": False,
            "left": 7,
            "left_relative": False,
        },
    )
    assert im.width == im_ref.width + 14
    assert im.height == im_ref.height + 14

    scale, pos = compute_scale_pos(im)

    assert abs(scale - 0.2) < 1e-3

    assert (np.array(im)[-1] > 0).any()
    assert (np.array(im)[:, -1] > 0).any()


def test_crop_scale_pos_bg(core_server_tester):
    im_ref, im = _test_crop_scale_pos(
        core_server_tester,
        [0, 0, 396, 639],
        50,
        {"x": 50, "y": 50},
        {
            "top": 100,
            "top_relative": False,
            "right": 100,
            "right_relative": False,
            "bottom": 100,
            "bottom_relative": False,
            "left": 100,
            "left_relative": False,
        },
        [187, 187, 187, 255],
    )
    assert im.width == im_ref.width + 200
    assert im.height == im_ref.height + 200

    assert (np.array(im) == 255).all()
