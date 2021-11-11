from test.conftest import RemovebgMessage
from test.core.helpers import process_image
from test.helpers import im_absdiff

from tests.utils import read_image


def test_exif1(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/exif_1.jpg")
    im_ref = process_image(core_server_tester, msg)["im"]
    im = process_image(core_server_tester, msg)["im"]
    assert im_ref.width == im.width
    assert im_ref.height == im.height


def _test_exif_rotation(core_server_tester, exif_compare_file_path):
    msg = RemovebgMessage()
    msg.data = read_image("../data/exif_1.jpg")
    im_ref = process_image(core_server_tester, msg)["im"]
    msg.data = read_image(exif_compare_file_path)
    im = process_image(core_server_tester, msg)["im"]

    assert im_ref.width == im.width
    assert im_ref.height == im.height
    assert abs(im_absdiff(im, im_ref, im, only_fg=True) - 0) < 0.025


def test_exif2(core_server_tester):
    _test_exif_rotation(core_server_tester, "../data/exif_2.jpg")


def test_exif3(core_server_tester):
    _test_exif_rotation(core_server_tester, "../data/exif_3.jpg")


def test_exif4(core_server_tester):
    _test_exif_rotation(core_server_tester, "../data/exif_4.jpg")


def test_exif5(core_server_tester):
    _test_exif_rotation(core_server_tester, "../data/exif_5.jpg")


def test_exif6(core_server_tester):
    _test_exif_rotation(core_server_tester, "../data/exif_6.jpg")


def test_exif7(core_server_tester):
    _test_exif_rotation(core_server_tester, "../data/exif_7.jpg")


def test_exif8(core_server_tester):
    _test_exif_rotation(core_server_tester, "../data/exif_2.jpg")


def test_exif_invalid(core_server_tester):
    _test_exif_rotation(core_server_tester, "../data/exif_invalid.jpg")
