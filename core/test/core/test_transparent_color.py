from test.conftest import RemovebgMessage
from test.core.helpers import process_image

import numpy as np
from tests.utils import read_image


def test_png(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/RGB.png")
    msg.megapixels = 0.25
    msg.roi = [0, 0, 639, 358]
    im = process_image(core_server_tester, msg)["im"]
    im = np.array(im)
    im_rgb = im[..., :3]
    im_alpha = im[..., 3]

    assert (im_rgb[im_alpha == 0] == 0).all()


def test_zip(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/RGB.png")
    msg.format = "zip"
    msg.megapixels = 0.25
    msg.roi = [0, 0, 639, 358]
    im_color = process_image(core_server_tester, msg)["im_color"]

    im_rgb = np.array(im_color.convert("L"))

    assert (im_rgb[0] > 0).all()
    assert (im_rgb[-1] > 0).all()
    assert (im_rgb[:, 0] > 0).all()
    assert (im_rgb[:, -1] > 0).all()
