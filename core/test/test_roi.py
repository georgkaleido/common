from test.helpers import pil_to_bytes
from tests.utils import convert_to_image, read_image


def test_default(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "roi": "0% 0% 100% 100%"}
    )

    assert im_in.width == im.width
    assert im_in.height == im.height

    import numpy as np

    im = np.array(im)

    # this image must have alpha values in last row
    assert (im[-1, :] > 0).any()


def test_relative(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "roi": "20% 10% 80% 90%", "channels": "alpha"}
    )

    assert im_in.width == im.width
    assert im_in.height == im.height

    w, h = im.width, im.height
    import numpy as np

    im = np.array(im)

    assert (im[: int(h * 0.1)] == 0).all()
    assert (im[-int(h * 0.1) :] == 0).all()

    assert (im[:, : int(w * 0.2)] == 0).all()
    assert (im[:, -int(w * 0.2) :] == 0).all()


def test_relative_exceed(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "roi": "0% 0% 101% 100%", "channels": "alpha"}
    )

    assert status_code == 400


def test_relative_order(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "roi": "70% 0% 30% 100%", "channels": "alpha"}
    )

    assert status_code == 200


def test_absolute(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg",
        {"format": "png", "size": "full", "roi": "50px 75px 255px 300px", "channels": "alpha"},
    )

    assert im_in.width == im.width
    assert im_in.height == im.height

    import numpy as np

    im = np.array(im)

    assert (im[:75] == 0).all()
    assert (im[301:] == 0).all()

    assert (im[:, :50] == 0).all()
    assert (im[:, 256:] == 0).all()


def test_fullres(req_fn):

    # In this test, we compare the results of the two following use case:
    # - processing the input in full resolution (>0.25mp) with an roi parameter,
    # - cropping manually the same input image with the same roi and processing it without roi parameters
    im_in_bytes = read_image("data/RGB.png")
    im_in = convert_to_image(im_in_bytes)
    im_in = im_in.resize(size=(im_in.size[0]*2, im_in.size[1]*2))
    im_in_bytes = pil_to_bytes(im_in)

    roi = [100, 75, 1220, 675]

    im_in_cropped = im_in.crop(roi)
    im_in_cropped_bytes = pil_to_bytes(im_in_cropped)

    im, _, headers, status_code = req_fn(
        im_in_bytes,
        {"format": "png", "size": "full", "roi": f"{roi[0]}px {roi[1]}px {roi[2]}px {roi[3]}px", "channels": "alpha"},
    )

    im_cropped_then_processed, _, headers2, status_code2 = req_fn(
        im_in_cropped_bytes,
        {"format": "png", "size": "full", "channels": "alpha"},
    )

    im_processed_then_cropped = im.crop(roi)

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


def test_absolute_exceed(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "roi": "0px 0px 1000px 100px", "channels": "alpha"}
    )

    assert status_code == 400


def test_relative_zero(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "roi": "100% 100% 100% 100%", "channels": "alpha"}
    )

    assert status_code == 400


def test_absolute_zero(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg",
        {"format": "png", "size": "full", "roi": "100px 100px 100px 100px", "channels": "alpha"},
    )

    assert status_code == 400
