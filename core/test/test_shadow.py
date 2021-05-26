def test_car_shadow(req_fn):
    im, _, _, _ = req_fn('data/RGB.png', {'format': 'png', 'size': 'preview', 'add_shadow': 'false'})
    im_s,  _, _, _ = req_fn('data/RGB.png', {'format': 'png', 'size': 'preview', 'add_shadow': 'true'})

    import numpy as np
    im = np.array(im)
    im_s = np.array(im_s)

    alpha = im[..., 3]
    alpha_s = im_s[..., 3]

    mask = (0 < alpha) & (alpha < 255)
    mask_s = (0 < alpha_s) & (alpha_s < 255)

    # there must be significantelly more in between regions when shadow is enabled
    assert mask_s.sum() > mask.sum() * 2

    # ones should stay the same
    assert (alpha == 255).sum() == (alpha_s == 255).sum()

    # color mean must be smaller for shadows due to zeros
    assert im[..., :3][mask].mean() > im_s[..., :3][mask_s].mean() * 1.2

    # the shadow should be completely black
    assert im_s[..., :3][alpha == 0].mean() < 1e-3


def test_person_shadow(req_fn):
    im, _, _, _ = req_fn('data/CMYK.jpg', {'format': 'png', 'size': 'preview', 'add_shadow': 'false'})
    im_s,  _, _, _ = req_fn('data/CMYK.jpg', {'format': 'png', 'size': 'preview', 'add_shadow': 'true'})

    import numpy as np
    im = np.array(im)
    im_s = np.array(im_s)

    assert (im == im_s).all()
