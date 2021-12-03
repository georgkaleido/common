from test.helpers import scaled_im

import numpy as np


def test_tight(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "crop": "true", "channels": "alpha"}
    )

    assert im_in.width > im.width
    assert im_in.height > im.height
    assert headers.get("X-Width") == str(im.width)
    assert headers.get("X-Height") == str(im.height)
    assert headers.get("X-Max-Width") == str(im_in.width)
    assert headers.get("X-Max-Height") == str(im_in.height)

    im = np.array(im)
    assert (im[0] > 0).any()
    assert (im[-1] > 0).any()
    assert (im[:, 0] > 0).any()
    assert (im[:-1] > 0).any()


def test_tight_mp_png(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 12), {"format": "png", "size": "full", "crop": "true", "channels": "alpha"}
    )

    # megapixels should be capped with uncropped dimensions, so here it should not be 10 mp
    assert im.width * im.height < 9500000


def test_tight_mp_jpg(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 27), {"format": "jpg", "size": "full", "crop": "true", "channels": "alpha"}
    )

    # megapixels should be capped with uncropped dimensions, so here it should not be 25 mp
    assert im.width * im.height < 24000000


def test_tight_mp_zip(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 27), {"format": "zip", "size": "full", "crop": "true"}
    )

    # megapixels should be capped with uncropped dimensions, so here it should not be 25 mp
    assert im[0].width * im[0].height < 24000000
    assert im[1].width * im[1].height < 24000000


def test_margin_abs1(req_fn):
    im_ref, _, _, _ = req_fn("data/CMYK.jpg", {"format": "png", "size": "full", "crop": "true"})
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg",
        {"format": "png", "size": "full", "crop": "true", "crop_margin": "50px", "channels": "alpha"},
    )

    assert im.width == im_ref.width + 100
    assert im.height == im_ref.height + 100

    im = np.array(im)
    assert (im[:50] == 0).all()
    assert (im[-50:] == 0).all()
    assert (im[:, :50] == 0).all()
    assert (im[:, -50:] == 0).all()


def test_margin_rel1(req_fn):
    im_ref, _, _, _ = req_fn("data/CMYK.jpg", {"format": "png", "size": "full", "crop": "true"})
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg",
        {"format": "png", "size": "full", "crop": "true", "crop_margin": "10%", "channels": "alpha"},
    )

    assert im.width == int(im_ref.width * 1.2 + 0.5)
    assert im.height == int(im_ref.height * 1.2 + 0.5)


def test_margin_abs2(req_fn):
    im_ref, _, _, _ = req_fn("data/CMYK.jpg", {"format": "png", "size": "full", "crop": "true"})
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg", {"format": "png", "size": "full", "crop": "true", "crop_margin": "50px 25px"}
    )

    assert im.width == im_ref.width + 50
    assert im.height == im_ref.height + 100

    im = np.array(im)
    assert (im[:50] == 0).all()
    assert (im[-50:] == 0).all()
    assert (im[:, :25] == 0).all()
    assert (im[:, -25:] == 0).all()


def test_margin_rel2(req_fn):
    im_ref, _, _, _ = req_fn("data/CMYK.jpg", {"format": "png", "size": "full", "crop": "true"})
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg",
        {"format": "png", "size": "full", "crop": "true", "crop_margin": "10% 5%", "channels": "alpha"},
    )

    assert im.width == int(im_ref.width * 1.1 + 0.5)
    assert im.height == int(im_ref.height * 1.2 + 0.5)


def test_margin_abs4(req_fn):
    im_ref, _, _, _ = req_fn("data/CMYK.jpg", {"format": "png", "size": "full", "crop": "true"})
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg",
        {"format": "png", "size": "full", "crop": "true", "crop_margin": "10px 20px 30px 40px"},
    )

    assert im.width == im_ref.width + 60
    assert im.height == im_ref.height + 40

    im = np.array(im)
    assert (im[:10] == 0).all()
    assert (im[-30:] == 0).all()
    assert (im[:, -20:] == 0).all()
    assert (im[:, :40] == 0).all()


def test_margin_rel4(req_fn):
    im_ref, _, _, _ = req_fn("data/CMYK.jpg", {"format": "png", "size": "full", "crop": "true"})
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg",
        {"format": "png", "size": "full", "crop": "true", "crop_margin": "1% 2% 3% 4%", "channels": "alpha"},
    )

    assert im.width == int(im_ref.width * 1.06 + 0.5)
    assert im.height == int(im_ref.height * 1.04 + 0.5)


def test_margin_rel_clamp_valid(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg",
        {"format": "png", "size": "full", "crop": "true", "crop_margin": "50%", "channels": "alpha"},
    )

    assert status_code == 200


def test_margin_rel_clamp_invalid(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg",
        {"format": "png", "size": "full", "crop": "true", "crop_margin": "51%", "channels": "alpha"},
    )

    assert status_code == 400


def test_margin_abs_clamp_valid(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg",
        {"format": "png", "size": "full", "crop": "true", "crop_margin": "500", "channels": "alpha"},
    )

    assert status_code == 200


def test_margin_abs_clamp_invalid(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/CMYK.jpg",
        {"format": "png", "size": "full", "crop": "true", "crop_margin": "501", "channels": "alpha"},
    )

    assert status_code == 400


def test_margin_rel_huge(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 25),
        {"format": "jpg", "size": "full", "crop": "true", "crop_margin": "50%", "channels": "alpha"},
    )

    assert status_code == 200
    assert im.width * im.height > 25000000


def test_margin_abs_huge(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 25),
        {"format": "jpg", "size": "full", "crop": "true", "crop_margin": "500px", "channels": "alpha"},
    )

    assert status_code == 200
    assert im.width * im.height > 25000000


def test_margin_rel_huge_png(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 10),
        {"format": "png", "size": "full", "crop": "true", "crop_margin": "50%", "channels": "alpha"},
    )

    assert status_code == 200
    assert im.width * im.height > 10000000


def test_margin_abs_huge_png(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 10),
        {"format": "png", "size": "full", "crop": "true", "crop_margin": "500px", "channels": "alpha"},
    )

    assert status_code == 200
    assert im.width * im.height > 10000000


def test_foreground_anchors(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/RGB.png", {"format": "png", "size": "full", "crop": "true", "channels": "alpha"}
    )

    input_foreground_left = int(headers.get("X-Foreground-Top"))
    input_foreground_top = int(headers.get("X-Foreground-Left"))
    input_foreground_width = int(headers.get("X-Foreground-Width"))
    input_foreground_height = int(headers.get("X-Foreground-Height"))

    assert 0 < input_foreground_left < im_in.width
    assert 0 < input_foreground_top < im_in.height
    assert 0 < input_foreground_width
    assert 0 < input_foreground_height
    assert input_foreground_left + input_foreground_width <= im_in.width
    assert input_foreground_top + input_foreground_height <= im_in.height
    assert im.width == input_foreground_width
    assert im.height == input_foreground_height
    assert im_in.width > im.width
    assert im_in.height > im.height


def test_foreground_anchors_no_crop(req_fn):
    im, im_in, headers, status_code = req_fn(
        "data/RGB.png", {"format": "png", "size": "full", "crop": "false", "channels": "alpha"}
    )

    input_foreground_left = int(headers.get("X-Foreground-Top"))
    input_foreground_top = int(headers.get("X-Foreground-Left"))
    input_foreground_width = int(headers.get("X-Foreground-Width"))
    input_foreground_height = int(headers.get("X-Foreground-Height"))

    assert 0 < input_foreground_left < im_in.width
    assert 0 < input_foreground_top < im_in.height
    assert 0 < input_foreground_width
    assert 0 < input_foreground_height
    assert input_foreground_left + input_foreground_width <= im_in.width
    assert input_foreground_top + input_foreground_height <= im_in.height
    assert im.width > input_foreground_width
    assert im.height > input_foreground_height
    assert im_in.width == im.width
    assert im_in.height == im.height

