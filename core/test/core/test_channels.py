from test.conftest import RemovebgMessage
from test.core.helpers import unzip

from tests.utils import convert_to_image, read_image


def _test_alpha(core_server_tester, im_format):
    msg = RemovebgMessage()
    msg.channels = "alpha"
    msg.format = im_format
    msg.data = read_image("../data/CMYK_icc.jpg")
    result = core_server_tester.request(msg.serialize())
    im_alpha = convert_to_image(result[b"data"])
    assert im_alpha.mode == "L"
    assert im_alpha.info.get("icc_profile") is None


def test_jpg_alpha(core_server_tester):
    _test_alpha(core_server_tester, "jpg")


def test_png_alpha(core_server_tester):
    _test_alpha(core_server_tester, "png")


def test_zip_alpha(core_server_tester):
    msg = RemovebgMessage()
    msg.channels = "alpha"
    msg.format = "zip"
    msg.data = read_image("../data/CMYK_icc.jpg")
    result = core_server_tester.request(msg.serialize())
    im_color, im_alpha = unzip(result[b"data"])
    assert im_color.mode == "CMYK"
    assert im_color.info.get("icc_profile") is not None
    assert im_alpha.mode == "L"
    assert im_alpha.info.get("icc_profile") is None


def test_noformat_alpha(core_server_tester):
    msg = RemovebgMessage()
    msg.channels = "alpha"
    msg.format = "auto"
    msg.data = read_image("../data/CMYK_icc.jpg")
    result = core_server_tester.request(msg.serialize())
    im = convert_to_image(result[b"data"])
    assert im.mode == "L"
    assert im.info.get("icc_profile") is None
