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
    msg.semitransparency_experimental = True
    im = process_image(core_server_tester, msg)["im"]

    msg.semitransparency = False
    msg.semitransparency_experimental = False
    im2 = process_image(core_server_tester, msg)["im"]

    msg.semitransparency = True
    msg.semitransparency_experimental = False
    im_s = process_image(core_server_tester, msg)["im"]

    msg.semitransparency = True
    msg.semitransparency_experimental = True
    im_new = process_image(core_server_tester, msg)["im"]

    im = np.array(im)
    im2 = np.array(im2)
    im_s = np.array(im_s)
    im_new = np.array(im_new)

    alpha = im[..., 3]
    alpha2 = im2[..., 3]
    alpha_s = im_s[..., 3]
    alpha_new = im_new[..., 3]

    mask = (0 < alpha) & (alpha < 255)
    mask_s = (0 < alpha_s) & (alpha_s < 255)
    mask_new = (0 < alpha_new) & (alpha_new < 255)

    # only use new semitransparency model when both flags are true.
    assert alpha2.sum() == alpha.sum()

    # there must be significantelly more in between regions for semi transparency
    assert mask_s.sum() > mask.sum() * 2
    assert mask_new.sum() > mask.sum() * 2

    # zeros should stay the same
    assert (alpha == 0).sum() == (alpha_s == 0).sum()
    assert (alpha == 0).sum() == (alpha_new == 0).sum()

    # color std must be smaller when semi transparency is on due to window averaging
    assert im[..., :3][mask].std() > im_s[..., :3][mask_s].std() * 1.2


def test_carinterior_semitransparency(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/car_interior.jpg")
    msg.megapixels = 0.25
    msg.roi = [0, 0, 670, 446]

    # new experimental flag default is False
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
