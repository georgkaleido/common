from test.conftest import RemovebgMessage
from test.core.helpers import process_image
from test.helpers import im_absdiff, pil_to_bytes
from test.test_background import ABSDIFF_THRESH

import numpy as np
from PIL import Image
from tests.utils import read_image


def _test_bg_im(core_server_tester, im_format: str):
    msg = RemovebgMessage()
    msg.channels = "alpha"
    msg.data = read_image("../data/CMYK.jpg")

    im_alpha = process_image(core_server_tester, msg)["im"]

    im_bg = Image.open("../data/RGB.png")
    im_bg = im_bg.resize((im_alpha.width, im_alpha.height))

    msg = RemovebgMessage()
    msg.format = im_format
    msg.bg_image = pil_to_bytes(im_bg)
    msg.data = read_image("../data/CMYK.jpg")

    im_color = process_image(core_server_tester, msg)["im"]

    assert im_absdiff(im_bg, im_color, im_alpha, only_bg=True) < ABSDIFF_THRESH


def test_bg_im_png(core_server_tester):
    _test_bg_im(core_server_tester, im_format="png")


def test_bg_im_jpg(core_server_tester):
    _test_bg_im(core_server_tester, im_format="jpg")


def test_bg_im_zip(core_server_tester):
    msg = RemovebgMessage()
    msg.channels = "alpha"
    msg.data = read_image("../data/CMYK.jpg")

    im_alpha = process_image(core_server_tester, msg)["im"]

    im_bg = Image.open("../data/RGB.png")
    im_bg = im_bg.resize((im_alpha.width, im_alpha.height))

    msg = RemovebgMessage()
    msg.format = "zip"
    msg.bg_image = pil_to_bytes(im_bg)
    msg.data = read_image("../data/CMYK.jpg")

    im_color = process_image(core_server_tester, msg)["im_color"]
    assert im_absdiff(im_bg, im_color, im_alpha, only_bg=True) < ABSDIFF_THRESH


def test_bg_color_jpg(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "jpg"
    msg.megapixels = 25
    msg.roi = [0, 0, 639, 358]
    msg.data = read_image("../data/RGB.png")
    msg.bg_color = [255, 170, 51, 255]
    im_color = process_image(core_server_tester, msg)["im"]
    im_color = np.array(im_color)
    assert im_color[0, 0, 0] == 255
    assert im_color[0, 0, 1] == 170
    assert im_color[0, 0, 2] == 51


def _test_bg_color_zip(core_server_tester, bg_color):
    msg = RemovebgMessage()
    msg.format = "zip"
    msg.megapixels = 25
    msg.roi = [0, 0, 639, 358]
    msg.data = read_image("../data/RGB.png")
    msg.bg_color = bg_color

    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]

    im_color = np.array(im_color)
    im_alpha = np.array(im_alpha)

    assert im_color[0, 0, 0] == bg_color[0]
    assert im_color[0, 0, 1] == bg_color[1]
    assert im_color[0, 0, 2] == bg_color[2]
    return im_alpha


def test_bg_color_zip(core_server_tester):
    bg_color = [255, 170, 51, 255]
    im_alpha = _test_bg_color_zip(core_server_tester, bg_color)
    assert (im_alpha == bg_color[3]).all()


def test_bg_color_transparent_zip(core_server_tester):
    im_alpha = _test_bg_color_zip(core_server_tester, [255, 170, 51, 17])
    assert im_alpha[0, 0] == 17
