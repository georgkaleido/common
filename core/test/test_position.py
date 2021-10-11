from test.helpers import compute_scale_pos

import numpy as np


def test_original(req_fn):
    im_ref = req_fn("data/CMYK.jpg", {"format": "png", "size": "full", "channels": "alpha"})[0]
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "position": "original", "channels": "alpha"}
    )

    assert (np.array(im) == np.array(im_ref)).all()


def test_center(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "position": "center", "channels": "alpha"}
    )

    assert im_in.width == im.width
    assert im_in.height == im.height

    # check if its centered
    assert compute_scale_pos(im)[1] == (im_in.width // 2.0, im_in.height // 2.0)


def test_center_vals1(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "position": "50%", "channels": "alpha"}
    )

    assert im_in.width == im.width
    assert im_in.height == im.height

    # check if its centered
    assert compute_scale_pos(im)[1] == (im_in.width // 2.0, im_in.height // 2.0)


def test_center_vals2(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "position": "50% 50%", "channels": "alpha"}
    )

    assert im_in.width == im.width
    assert im_in.height == im.height

    # check if its centered
    assert compute_scale_pos(im)[1] == (im_in.width // 2.0, im_in.height // 2.0)


def test_lt(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "position": "0%", "channels": "alpha"}
    )

    assert im_in.width == im.width
    assert im_in.height == im.height

    assert np.array(im)[0].any()
    assert np.array(im)[:, 0].any()


def test_tr(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "position": "100% 0%", "channels": "alpha"}
    )

    assert im_in.width == im.width
    assert im_in.height == im.height

    assert np.array(im)[0].any()
    assert np.array(im)[:, -1].any()


def test_lb(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "position": "0% 100%", "channels": "alpha"}
    )

    assert im_in.width == im.width
    assert im_in.height == im.height

    assert np.array(im)[-1].any()
    assert np.array(im)[:, 0].any()


def test_br(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "position": "100% 100%", "channels": "alpha"}
    )

    assert im_in.width == im.width
    assert im_in.height == im.height

    assert np.array(im)[-1].any()
    assert np.array(im)[:, -1].any()
