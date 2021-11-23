from test.conftest import RemovebgMessage

from tests.utils import read_image


def _test_type(core_server_tester, im_file, out_type, in_type="auto"):
    msg = RemovebgMessage()
    msg.data = read_image(im_file)
    msg.type = in_type
    msg.format = "jpg"
    result = core_server_tester.request(msg.serialize())
    assert result[b"type"] == str.encode(out_type)


def test_car_manual(core_server_tester):
    _test_type(core_server_tester, "../data/CMYK.jpg", out_type="car", in_type="car")


def test_person_manual(core_server_tester):
    _test_type(core_server_tester, "../data/CMYK.jpg", out_type="person", in_type="person")


def test_product_manual(core_server_tester):
    _test_type(core_server_tester, "../data/CMYK.jpg", out_type="product", in_type="product")


def test_product_animal(core_server_tester):
    _test_type(core_server_tester, "../data/CMYK.jpg", out_type="animal", in_type="animal")


def test_person(core_server_tester):
    _test_type(core_server_tester, "../data/CMYK.jpg", out_type="person")


def test_animal(core_server_tester):
    _test_type(core_server_tester, "../data/L.jpg", out_type="animal")


def test_car(core_server_tester):
    _test_type(core_server_tester, "../data/RGB.png", out_type="car")
