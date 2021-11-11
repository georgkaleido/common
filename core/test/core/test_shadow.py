from test.conftest import RemovebgMessage
from test.core.helpers import process_image

import numpy as np
from tests.utils import read_image


def test_car_shadow(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/RGB.png")
    msg.megapixels = 0.25
    msg.shadow = False
    msg.scale = None
    msg.roi = [0, 0, 639, 358]
    tmp = dict(msg.serialize())
    del tmp[b"data"]
    print(tmp)
    im = process_image(core_server_tester, msg)["im"]
    msg.shadow = True
    tmp = dict(msg.serialize())
    del tmp[b"data"]
    print(tmp)
    im_s = process_image(core_server_tester, msg)["im"]

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


def test_person_shadow(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/CMYK.jpg")
    msg.megapixels = 0.25
    msg.shadow = False
    msg.roi = [0, 0, 396, 639]
    im = process_image(core_server_tester, msg)["im"]
    msg.shadow = True
    im_s = process_image(core_server_tester, msg)["im"]

    im = np.array(im)
    im_s = np.array(im_s)

    assert (im == im_s).all()
