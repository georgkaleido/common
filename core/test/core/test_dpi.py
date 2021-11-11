from test.conftest import RemovebgMessage
from test.core.helpers import process_image
from test.test_dpi import convert_dpi_as_int

from tests.utils import convert_to_image, read_image

# cmyk


def _test_dpi(core_server_tester, im_file, im_format, roi=None):
    if im_format == "zip":
        _test_dpi_zip(core_server_tester, im_file, roi)
        return None
    msg = RemovebgMessage()
    msg.format = im_format
    if roi:
        msg.roi = roi
    im_in_bytes = read_image(im_file)
    msg.data = im_in_bytes
    im_in = convert_to_image(im_in_bytes)
    im = process_image(core_server_tester, msg)["im"]
    dpi = convert_dpi_as_int(im.info.get("dpi"))
    dpi_in = convert_dpi_as_int(im_in.info.get("dpi"))
    assert dpi == dpi_in
    return None


def test_cmyk_png(core_server_tester):
    _test_dpi(core_server_tester, "../data/CMYK.jpg", "png")


def test_cmyk_jpg(core_server_tester):
    _test_dpi(core_server_tester, "../data/CMYK.jpg", "jpg")


def _test_dpi_zip(core_server_tester, im_file, roi=None):
    msg = RemovebgMessage()
    msg.format = "zip"
    im_in_bytes = read_image(im_file)
    msg.data = im_in_bytes
    if roi:
        msg.roi = roi
    im_in = convert_to_image(im_in_bytes)
    image_dict = process_image(core_server_tester, msg)
    dpi_in = convert_dpi_as_int(im_in.info.get("dpi"))
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    for im in [im_color, im_alpha]:
        dpi = convert_dpi_as_int(im.info.get("dpi"))
        assert dpi == dpi_in


def test_cmyk_zip(core_server_tester):
    _test_dpi(core_server_tester, "../data/CMYK.jpg", "zip")


# rgb


def test_rgb_jpg(core_server_tester):
    _test_dpi(core_server_tester, "../data/RGB.png", "jpg", [0, 0, 639, 358])


def test_rgb_png(core_server_tester):
    _test_dpi(core_server_tester, "../data/RGB.png", "png", [0, 0, 639, 358])


def test_rgb_zip(core_server_tester):
    _test_dpi(core_server_tester, "../data/RGB.png", "zip", [0, 0, 639, 358])


# rgba


def test_rgba_jpg(core_server_tester):
    _test_dpi(core_server_tester, "../data/RGBA.png", "jpg", [0, 0, 639, 358])


def test_rgba_png(core_server_tester):
    _test_dpi(core_server_tester, "../data/RGBA.png", "png", [0, 0, 639, 358])


def test_rgba_zip(core_server_tester):
    _test_dpi(core_server_tester, "../data/RGBA.png", "zip", [0, 0, 639, 358])


# l


def test_l_jpg(core_server_tester):
    _test_dpi(core_server_tester, "../data/L.jpg", "jpg")


def test_l_png(core_server_tester):
    _test_dpi(core_server_tester, "../data/L.jpg", "png")


def test_l_zip(core_server_tester):
    _test_dpi(core_server_tester, "../data/L.jpg", "zip")


# la


def test_la_jpg(core_server_tester):
    _test_dpi(core_server_tester, "../data/LA.png", "jpg")


def test_la_png(core_server_tester):
    _test_dpi(core_server_tester, "../data/LA.png", "png")


def test_la_zip(core_server_tester):
    _test_dpi(core_server_tester, "../data/LA.png", "zip")


# p


def test_p_jpg(core_server_tester):
    _test_dpi(core_server_tester, "../data/P.png", "jpg")


def test_p_png(core_server_tester):
    _test_dpi(core_server_tester, "../data/P.png", "png")


def test_p_zip(core_server_tester):
    _test_dpi(core_server_tester, "../data/P.png", "zip")
