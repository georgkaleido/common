from test.conftest import RemovebgMessage
from test.core.helpers import process_image
from test.helpers import im_absdiff
from test.test_color_consistency import ABSDIFF_THRESH

from tests.utils import convert_to_image, read_image


def test_cmyk(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "zip"
    im_in_bytes = read_image("../data/CMYK.jpg")
    im_in = convert_to_image(im_in_bytes)
    msg.data = im_in_bytes
    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    assert im_color.mode == "CMYK"
    assert im_color.info.get("icc_profile") is None
    assert im_absdiff(im_in, im_color, im_alpha) < ABSDIFF_THRESH


def test_cmyk_icc(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "zip"
    im_in_bytes = read_image("../data/CMYK_icc.jpg")
    im_in = convert_to_image(im_in_bytes)
    msg.data = im_in_bytes
    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    assert im_color.mode == "CMYK"
    assert im_color.info.get("icc_profile") is not None
    assert im_absdiff(im_in, im_color, im_alpha) < ABSDIFF_THRESH


def test_cmyk_icc_bg(core_server_tester):
    msg = RemovebgMessage()
    msg.channels = "alpha"
    im_in_bytes = read_image("../data/CMYK_icc.jpg")
    im_in = convert_to_image(im_in_bytes)
    msg.data = im_in_bytes
    msg.roi = [0, 0, 396, 639]

    im_alpha = process_image(core_server_tester, msg)["im"]
    msg.format = "zip"
    msg.channels = "rgba"
    msg.bg_color = [255, 255, 255, 255]
    msg.roi = [0, 0, 396, 639]
    im_color = process_image(core_server_tester, msg)["im_color"]

    assert im_color.mode == "CMYK"
    assert im_color.info.get("icc_profile") is not None
    assert im_absdiff(im_in, im_color, im_alpha, only_fg=True) < ABSDIFF_THRESH


def test_cmyk_icc_bg_im(core_server_tester):
    bg_image = read_image("../data/RGB_icc.png")

    msg = RemovebgMessage()
    msg.channels = "alpha"
    msg.data = read_image("../data/CMYK_icc.jpg")
    msg.roi = [0, 0, 396, 639]
    im_alpha = process_image(core_server_tester, msg)["im"]

    msg.format = "zip"
    im_in_bytes = read_image("../data/CMYK_icc.jpg")
    im_in = convert_to_image(im_in_bytes)
    msg.data = im_in_bytes
    msg.bg_image = bg_image
    msg.roi = [0, 0, 396, 639]

    im_color = process_image(core_server_tester, msg)["im_color"]

    assert im_color.mode == "CMYK"
    assert im_color.info.get("icc_profile") is not None
    assert im_absdiff(im_in, im_color, im_alpha, only_fg=True) < ABSDIFF_THRESH


def test_rgb(core_server_tester):
    msg = RemovebgMessage()
    msg.semitransparency = False
    msg.format = "zip"
    msg.roi = [0, 0, 639, 358]
    im_in_bytes = read_image("../data/RGB.png")
    im_in = convert_to_image(im_in_bytes)
    msg.data = im_in_bytes
    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    assert im_color.mode == "RGB"
    assert im_color.info.get("icc_profile") is None
    assert im_absdiff(im_in, im_color, im_alpha) < ABSDIFF_THRESH


def test_rgb_png(core_server_tester):
    msg = RemovebgMessage()
    msg.semitransparency = False
    msg.roi = [0, 0, 639, 358]
    im_in_bytes = read_image("../data/RGB.png")
    im_in = convert_to_image(im_in_bytes)
    msg.data = im_in_bytes
    im = process_image(core_server_tester, msg)["im"]
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None
    assert im_absdiff(im_in, im, im, only_fg=True) < 0.06


def test_rgb_icc(core_server_tester):
    msg = RemovebgMessage()
    msg.semitransparency = False
    msg.roi = [0, 0, 639, 358]
    msg.format = "zip"
    im_in_bytes = read_image("../data/RGB_icc.png")
    im_in = convert_to_image(im_in_bytes)
    msg.data = im_in_bytes
    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    assert im_color.mode == "RGB"
    assert im_color.info.get("icc_profile") is not None

    assert im_absdiff(im_in, im_color, im_alpha) < ABSDIFF_THRESH


def test_rgb_icc_png(core_server_tester):
    msg = RemovebgMessage()
    msg.semitransparency = False
    msg.roi = [0, 0, 639, 358]
    im_in_bytes = read_image("../data/RGB_icc.png")
    im_in = convert_to_image(im_in_bytes)
    msg.data = im_in_bytes
    im = process_image(core_server_tester, msg)["im"]
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is not None
    assert im_absdiff(im_in, im, im, only_fg=True) < 0.06


def test_rgb_icc_bg(core_server_tester):
    im_in_bytes = read_image("../data/RGB_icc.png")
    im_in = convert_to_image(im_in_bytes)
    msg = RemovebgMessage()
    msg.channels = "alpha"
    msg.data = im_in_bytes
    msg.roi = [0, 0, 639, 358]
    im_alpha = process_image(core_server_tester, msg)["im"]

    msg.bg_color = [255, 255, 255, 255]
    msg.format = "zip"
    msg.semitransparency = False
    msg.bg_image = read_image("../data/CMYK_icc.jpg")
    im_color = process_image(core_server_tester, msg)["im_color"]

    assert im_color.mode == "RGB"
    assert im_color.info.get("icc_profile") is not None
    assert im_absdiff(im_in, im_color, im_alpha, only_fg=True) < ABSDIFF_THRESH


def test_rgb_icc_bg_im(core_server_tester):
    im_in_bytes = read_image("../data/RGB_icc.png")
    im_in = convert_to_image(im_in_bytes)
    msg = RemovebgMessage()
    msg.channels = "alpha"
    msg.data = im_in_bytes
    msg.roi = [0, 0, 639, 358]
    im_alpha = process_image(core_server_tester, msg)["im"]

    msg.format = "zip"
    msg.semitransparency = False
    msg.bg_image = read_image("../data/CMYK_icc.jpg")
    im_color = process_image(core_server_tester, msg)["im_color"]
    assert im_color.mode == "RGB"
    assert im_color.info.get("icc_profile") is not None
    assert im_absdiff(im_in, im_color, im_alpha, only_fg=True) < ABSDIFF_THRESH


# L


def test_l(core_server_tester):
    im_in_bytes = read_image("../data/L.jpg")
    im_in = convert_to_image(im_in_bytes)
    msg = RemovebgMessage()
    msg.format = "zip"
    msg.roi = [0, 0, 511, 639]
    msg.data = im_in_bytes
    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    assert im_color.mode == "L"
    assert im_color.info.get("icc_profile") is None
    assert im_absdiff(im_in, im_color, im_alpha) < ABSDIFF_THRESH


def test_l_icc_bg(core_server_tester):
    im_in_bytes = read_image("../data/L_icc.jpg")
    im_in = convert_to_image(im_in_bytes)
    msg = RemovebgMessage()
    msg.data = im_in_bytes
    im_alpha = process_image(core_server_tester, msg)["im"]

    msg.format = "zip"
    msg.bg_color = [255, 255, 255, 255]
    im_color = process_image(core_server_tester, msg)["im_color"]

    assert im_color.mode == "L"
    assert im_color.info.get("icc_profile") is not None

    assert im_absdiff(im_in, im_color, im_alpha, only_fg=True) < ABSDIFF_THRESH


def test_l_icc_bg_im(core_server_tester):
    bg_image = read_image("../data/CMYK_icc.jpg")
    im_in_bytes = read_image("../data/L_icc.jpg")
    im_in = convert_to_image(im_in_bytes)

    msg = RemovebgMessage()
    msg.data = im_in_bytes
    msg.channels = "alpha"
    im_alpha = process_image(core_server_tester, msg)["im"]

    msg.format = "zip"
    msg.bg_image = bg_image
    im_color = process_image(core_server_tester, msg)["im_color"]

    assert im_color.mode == "L"
    assert im_color.info.get("icc_profile") is not None

    assert im_absdiff(im_in, im_color, im_alpha, only_fg=True) < ABSDIFF_THRESH
