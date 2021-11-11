from test.helpers import scaled_im


def check_sizes(im_in, im_out, mp_target, headers=None):
    mp_in = im_in.width * im_in.height
    mp_out = im_out.width * im_out.height
    if headers:
        mp_res_max = int(headers.get("X-Max-Width")) * int(headers.get("X-Max-Height"))

        assert headers.get("X-Width") == str(im_out.width)
        assert headers.get("X-Height") == str(im_out.height)

        if mp_in > 25000000:
            # should be capped at the limit
            assert 0 < 25000000 - mp_res_max < mp_res_max * 0.005
        else:
            # must match with the original mp
            assert mp_in == mp_res_max

    assert 0 < mp_target * 1000000 - mp_out < mp_out * 0.005


# test small (0 - 0.25mp)


def test_small(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 0.5), {"format": "jpg", "size": "small"}
    )
    check_sizes(im_in, im, 0.25, headers)


def test_preview(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 0.5), {"format": "jpg", "size": "preview"}
    )
    check_sizes(im_in, im, 0.25, headers)


def test_regular(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 0.5), {"format": "jpg", "size": "regular"}
    )
    check_sizes(im_in, im, 0.25, headers)


def test_preview_lower(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 0.2), {"format": "jpg", "size": "preview"}
    )
    check_sizes(im_in, im, 0.2, headers)


# test medium (0.25 - 1.5mp)


def test_medium_lower(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 0.2), {"format": "jpg", "size": "medium"}
    )
    check_sizes(im_in, im, 0.2, headers)


def test_medium(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 1.1), {"format": "jpg", "size": "medium"}
    )
    check_sizes(im_in, im, 1.1, headers)


def test_medium_upper(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 2.0), {"format": "jpg", "size": "medium"}
    )
    check_sizes(im_in, im, 1.5, headers)


# test hd (1.0 - 4.0mp)


def test_hd_lower(req_fn):
    im, im_in, headers, status_code = req_fn(scaled_im("data/CMYK.jpg", 0.8), {"format": "jpg", "size": "hd"})
    check_sizes(im_in, im, 0.8, headers)


def test_hd(req_fn):
    im, im_in, headers, status_code = req_fn(scaled_im("data/CMYK.jpg", 2.1), {"format": "jpg", "size": "hd"})
    check_sizes(im_in, im, 2.1, headers)


def test_hd_upper(req_fn):
    im, im_in, headers, status_code = req_fn(scaled_im("data/CMYK.jpg", 5.0), {"format": "jpg", "size": "hd"})
    check_sizes(im_in, im, 4.0, headers)


# test full (- 25mp)


def test_full_lower(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 3.5), {"format": "jpg", "size": "full"}
    )
    check_sizes(im_in, im, 3.5, headers)


def test_full(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 5.0), {"format": "jpg", "size": "full"}
    )
    check_sizes(im_in, im, 5.0, headers)


def test_4k(req_fn):
    im, im_in, headers, status_code = req_fn(scaled_im("data/CMYK.jpg", 5.0), {"format": "jpg", "size": "4k"})
    check_sizes(im_in, im, 5.0, headers)


def test_full_upper(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 27.0), {"format": "jpg", "size": "full"}
    )
    check_sizes(im_in, im, 25, headers)


# test auto


def test_auto_small(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 0.2), {"format": "jpg", "size": "full"}
    )
    check_sizes(im_in, im, 0.2, headers)


def test_auto_medium(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 0.5), {"format": "jpg", "size": "full"}
    )
    check_sizes(im_in, im, 0.5, headers)


def test_auto_hd(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 2.0), {"format": "jpg", "size": "full"}
    )
    check_sizes(im_in, im, 2.0, headers)


def test_auto_full(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 5.0), {"format": "jpg", "size": "full"}
    )
    check_sizes(im_in, im, 5.0, headers)


# test zip and png


def test_full_png(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 27.0), {"format": "png", "size": "full"}
    )
    check_sizes(im_in, im, 10, headers)


def test_full_zip(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 27.0), {"format": "zip", "size": "full"}
    )
    check_sizes(im_in, im[0], 25, headers)
    check_sizes(im_in, im[1], 25, headers)


# image too large


def test_image_too_large(req_fn):
    im, im_in, headers, status_code = req_fn(
        scaled_im("data/CMYK.jpg", 51.0), {"format": "jpg", "size": "full"}
    )
    assert status_code == 400
