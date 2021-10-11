from test.helpers import compute_scale_pos


def test_small(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "scale": "10%", "channels": "alpha"}
    )

    assert im_in.width == im.width
    assert im_in.height == im.height

    scale, pos = compute_scale_pos(im)

    assert abs(scale - 0.1) < 1e-3
    assert pos == (im_in.width // 2.0, im_in.height // 2.0)


def test_half(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "scale": "50%", "channels": "alpha"}
    )

    assert im_in.width == im.width
    assert im_in.height == im.height

    scale, pos = compute_scale_pos(im)

    assert abs(scale - 0.5) < 1e-3
    assert pos == (im_in.width // 2.0, im_in.height // 2.0)


def test_full(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "scale": "100%", "channels": "alpha"}
    )

    assert im_in.width == im.width
    assert im_in.height == im.height

    scale, pos = compute_scale_pos(im)

    assert abs(scale - 1.0) < 1e-3
    assert pos == (im_in.width // 2.0, im_in.height // 2.0)
