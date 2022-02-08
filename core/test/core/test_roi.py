from test.conftest import RemovebgMessage
from test.core.helpers import process_image
from test.helpers import pil_to_bytes

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


def test_fullres(core_server_tester):
    msg = RemovebgMessage()
    im_in_bytes = read_image("../data/RGB.png")
    im_in = convert_to_image(im_in_bytes)
    im_in = im_in.resize(size=(im_in.size[0]*2, im_in.size[1]*2))
    im_in_bytes = pil_to_bytes(im_in)

    msg.data = im_in_bytes
    roi = [100, 75, 1220, 675]
    msg.roi = roi
    im = process_image(core_server_tester, msg)["im"]

    msg = RemovebgMessage()
    im_in_cropped = im_in.crop(roi)
    im_in_cropped_bytes = pil_to_bytes(im_in_cropped)
    msg.data = im_in_cropped_bytes
    im_cropped_then_processed = process_image(core_server_tester, msg)["im"]

    im_processed_then_cropped = im.crop(roi)

    assert im_cropped_then_processed.width == im_processed_then_cropped.width
    assert im_cropped_then_processed.height == im_processed_then_cropped.height

    import numpy as np

    im_cropped_then_processed = np.array(im_cropped_then_processed)
    im_processed_then_cropped = np.array(im_processed_then_cropped)

    # convert to boolean numpy array
    im_cropped_then_processed = im_cropped_then_processed > 0
    im_processed_then_cropped = im_processed_then_cropped > 0

    # Compute IoU
    overlap = im_cropped_then_processed * im_processed_then_cropped
    union = im_cropped_then_processed + im_processed_then_cropped
    iou = overlap.sum() / float(union.sum())

    # With a different version of the model, it is possible that the IoU is below 0.99
    # Let's think of something if this happens
    assert 0.99 < iou
