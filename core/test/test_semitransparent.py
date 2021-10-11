def test_car_semitransparency(req_fn):
    im, _, _, _ = req_fn("data/RGB.png", {"format": "png", "size": "preview", "semitransparency": "false"})
    im_s, _, _, _ = req_fn("data/RGB.png", {"format": "png", "size": "preview", "semitransparency": "true"})

    import numpy as np

    im = np.array(im)
    im_s = np.array(im_s)

    alpha = im[..., 3]
    alpha_s = im_s[..., 3]

    mask = (0 < alpha) & (alpha < 255)
    mask_s = (0 < alpha_s) & (alpha_s < 255)

    # there must be significantelly more in between regions for semi transparency
    assert mask_s.sum() > mask.sum() * 2

    # zeros should stay the same
    assert (alpha == 0).sum() == (alpha_s == 0).sum()

    # color std must be smaller when semi transparency is on due to window averaging
    assert im[..., :3][mask].std() > im_s[..., :3][mask_s].std() * 1.2


def test_carinterior_semitransparency(req_fn):
    im, _, _, _ = req_fn(
        "data/car_interior.jpg", {"format": "png", "size": "preview", "semitransparency": "false"}
    )
    im_s, _, _, _ = req_fn(
        "data/car_interior.jpg", {"format": "png", "size": "preview", "semitransparency": "true"}
    )

    import numpy as np

    im = np.array(im)
    im_s = np.array(im_s)

    alpha = im[..., 3]
    alpha_s = im_s[..., 3]

    mask = (0 < alpha) & (alpha < 255)
    mask_s = (0 < alpha_s) & (alpha_s < 255)

    # there must be significantelly more in between regions for semi transparency
    assert mask_s.sum() > mask.sum() * 2

    # ones should stay the same
    assert (alpha == 255).sum() == (alpha_s == 255).sum()

    # color std must be smaller when semi transparency is on due to window averaging
    assert im[..., :3][mask].std() > im_s[..., :3][mask_s].std() * 1.2
