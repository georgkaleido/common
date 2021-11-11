from test.conftest import RemovebgMessage
from test.core.helpers import process_image

from tests.utils import read_image


def _test_processing(core_server_tester, im_format):
    msg = RemovebgMessage()
    msg.data = read_image("../data/RGB.png")
    msg.format = im_format
    msg.roi = [0, 0, 639, 358]
    if im_format != "zip":
        im = process_image(core_server_tester, msg)["im"]

        assert im.format == im_format.upper()
    else:
        assert process_image(core_server_tester, msg)["im_alpha"]


def test_png(core_server_tester):
    _test_processing(core_server_tester, "png")


def test_jpg(core_server_tester):
    _test_processing(core_server_tester, "jpeg")


def test_zip(core_server_tester):
    _test_processing(core_server_tester, "zip")
