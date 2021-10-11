from test.helpers import compute_scale_pos


def test_crop_scale_pos1(req_fn):
    im_ref = req_fn("data/CMYK.jpg", {"format": "png", "size": "full", "crop": "true", "channels": "alpha"})[
        0
    ]
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg",
        {
            "format": "png",
            "size": "full",
            "crop": "true",
            "crop_margin": "100px",
            "scale": "50%",
            "position": "50%",
            "channels": "alpha",
        },
    )

    assert im.width == im_ref.width + 200
    assert im.height == im_ref.height + 200

    scale, pos = compute_scale_pos(im)

    assert abs(scale - 0.5) < 1e-3
    assert pos == (im.width // 2.0, im.height // 2.0)


def test_crop_scale_pos2(req_fn):
    im_ref = req_fn("data/CMYK.jpg", {"format": "png", "size": "full", "crop": "true", "channels": "alpha"})[
        0
    ]
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg",
        {
            "format": "png",
            "size": "full",
            "crop": "true",
            "crop_margin": "7px",
            "scale": "20%",
            "position": "100%",
            "channels": "alpha",
        },
    )

    assert im.width == im_ref.width + 14
    assert im.height == im_ref.height + 14

    scale, pos = compute_scale_pos(im)

    assert abs(scale - 0.2) < 1e-3

    import numpy as np

    assert (np.array(im)[-1] > 0).any()
    assert (np.array(im)[:, -1] > 0).any()


def test_crop_scale_pos_bg(req_fn):

    im_ref = req_fn("data/CMYK.jpg", {"format": "png", "size": "full", "crop": "true", "channels": "alpha"})[
        0
    ]
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg",
        {
            "format": "png",
            "size": "full",
            "crop": "true",
            "crop_margin": "100px",
            "scale": "50%",
            "position": "50%",
            "channels": "alpha",
            "bg_color": "bbbbbb",
        },
    )

    assert im.width == im_ref.width + 200
    assert im.height == im_ref.height + 200

    import numpy as np

    assert (np.array(im) == 255).all()
