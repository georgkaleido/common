from test.conftest import RemovebgMessage
from test.core.helpers import process_image

import numpy as np
from tests.utils import read_image


def test_car_semitransparency(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/RGB.png")
    msg.megapixels = 0.25
    msg.roi = [0, 0, 639, 358]
    msg.semitransparency = False
    im = process_image(core_server_tester, msg)["im"]
    msg.semitransparency = True
    im_s = process_image(core_server_tester, msg)["im"]

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


def test_carinterior_semitransparency(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/car_interior.jpg")
    msg.megapixels = 0.25
    msg.roi = [0, 0, 670, 446]
    msg.semitransparency = False
    im = process_image(core_server_tester, msg)["im"]
    msg.semitransparency = True
    im_s = process_image(core_server_tester, msg)["im"]

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
