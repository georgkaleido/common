import numpy as np


def test_png(req_fn):
    im, _, _, _ = req_fn("data/RGB.png", {"format": "png", "size": "preview"})

    im = np.array(im)
    im_rgb = im[..., :3]
    im_alpha = im[..., 3]

    assert (im_rgb[im_alpha == 0] == 0).all()


def test_zip(req_fn):
    im, _, _, _ = req_fn("data/RGB.png", {"format": "zip", "size": "preview"})

    im_rgb = np.array(im[0].convert("L"))

    assert (im_rgb[0] > 0).all()
    assert (im_rgb[-1] > 0).all()
    assert (im_rgb[:, 0] > 0).all()
    assert (im_rgb[:, -1] > 0).all()
