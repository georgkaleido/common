from test.conftest import RemovebgMessage
from test.core.helpers import process_image

from tests.utils import convert_to_image, read_image


def test_default(core_server_tester):
    msg = RemovebgMessage()
    im_in_bytes = read_image("../data/CMYK.jpg")
    im_in = convert_to_image(im_in_bytes)
    msg.data = im_in_bytes
    msg.roi = [0, 0, 396, 639]
    im = process_image(core_server_tester, msg)["im"]

    assert im_in.width == im.width
    assert im_in.height == im.height

    import numpy as np

    im = np.array(im)

    # this image must have alpha values in last row
    assert (im[-1, :] > 0).any()


def test_relative(core_server_tester):
    msg = RemovebgMessage()
    im_in_bytes = read_image("../data/CMYK.jpg")
    im_in = convert_to_image(im_in_bytes)
    msg.data = im_in_bytes
    msg.roi = [79, 64, 317, 575]
    im = process_image(core_server_tester, msg)["im"]

    assert im_in.width == im.width
    assert im_in.height == im.height

    w, h = im.width, im.height
    import numpy as np

    im = np.array(im)

    assert (im[: int(h * 0.1)] == 0).all()
    assert (im[-int(h * 0.1) :] == 0).all()

    assert (im[:, : int(w * 0.2)] == 0).all()
    assert (im[:, -int(w * 0.2) :] == 0).all()


def test_relative_exceed(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/CMYK.jpg")
    msg.roi = [79, 64, 317, 10000]
    result = core_server_tester.request(msg.serialize())
    assert result[b"status"] == b"error"


def test_relative_order(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/CMYK.jpg")
    msg.roi = [277, 0, 119, 639]
    result = core_server_tester.request(msg.serialize())
    assert result[b"status"] == b"ok"


def test_absolute(core_server_tester):
    msg = RemovebgMessage()
    im_in_bytes = read_image("../data/CMYK.jpg")
    im_in = convert_to_image(im_in_bytes)
    msg.data = im_in_bytes
    msg.roi = [50, 75, 255, 300]
    im = process_image(core_server_tester, msg)["im"]
    assert im_in.width == im.width
    assert im_in.height == im.height

    import numpy as np

    im = np.array(im)

    assert (im[:75] == 0).all()
    assert (im[301:] == 0).all()

    assert (im[:, :50] == 0).all()
    assert (im[:, 256:] == 0).all()
