from test.helpers import im_absdiff


def test_exif1(req_fn):
    im_ref = req_fn("data/exif_1.jpg", {"format": "png", "size": "full"})[0]
    im, im_in, headers, status_code = req_fn("data/exif_1.jpg", {"format": "png", "size": "full"})

    assert im_ref.width == im.width
    assert im_ref.height == im.height


def test_exif2(req_fn):
    im_ref = req_fn("data/exif_1.jpg", {"format": "png", "size": "full"})[0]
    im, im_in, headers, status_code = req_fn("data/exif_2.jpg", {"format": "png", "size": "full"})

    assert im_ref.width == im.width
    assert im_ref.height == im.height

    assert abs(im_absdiff(im, im_ref, im, only_fg=True) - 0) < 0.025


def test_exif3(req_fn):
    im_ref = req_fn("data/exif_1.jpg", {"format": "png", "size": "full"})[0]
    im, im_in, headers, status_code = req_fn("data/exif_3.jpg", {"format": "png", "size": "full"})

    assert im_ref.width == im.width
    assert im_ref.height == im.height

    assert abs(im_absdiff(im, im_ref, im, only_fg=True) - 0) < 0.025


def test_exif4(req_fn):
    im_ref = req_fn("data/exif_1.jpg", {"format": "png", "size": "full"})[0]
    im, im_in, headers, status_code = req_fn("data/exif_4.jpg", {"format": "png", "size": "full"})

    assert im_ref.width == im.width
    assert im_ref.height == im.height

    assert abs(im_absdiff(im, im_ref, im, only_fg=True) - 0) < 0.025


def test_exif5(req_fn):
    im_ref = req_fn("data/exif_1.jpg", {"format": "png", "size": "full"})[0]
    im, im_in, headers, status_code = req_fn("data/exif_5.jpg", {"format": "png", "size": "full"})

    assert im_ref.width == im.width
    assert im_ref.height == im.height

    assert abs(im_absdiff(im, im_ref, im, only_fg=True) - 0) < 0.025


def test_exif6(req_fn):
    im_ref = req_fn("data/exif_1.jpg", {"format": "png", "size": "full"})[0]
    im, im_in, headers, status_code = req_fn("data/exif_6.jpg", {"format": "png", "size": "full"})

    assert im_ref.width == im.width
    assert im_ref.height == im.height

    assert abs(im_absdiff(im, im_ref, im, only_fg=True) - 0) < 0.025


def test_exif7(req_fn):
    im_ref = req_fn("data/exif_1.jpg", {"format": "png", "size": "full"})[0]
    im, im_in, headers, status_code = req_fn("data/exif_7.jpg", {"format": "png", "size": "full"})

    assert im_ref.width == im.width
    assert im_ref.height == im.height

    assert abs(im_absdiff(im, im_ref, im, only_fg=True) - 0) < 0.025


def test_exif8(req_fn):
    im_ref = req_fn("data/exif_1.jpg", {"format": "png", "size": "full"})[0]
    im, im_in, headers, status_code = req_fn("data/exif_8.jpg", {"format": "png", "size": "full"})

    assert im_ref.width == im.width
    assert im_ref.height == im.height

    assert abs(im_absdiff(im, im_ref, im, only_fg=True) - 0) < 0.025


def test_exif_invalid(req_fn):
    im_ref = req_fn("data/exif_1.jpg", {"format": "png", "size": "full"})[0]
    im, im_in, headers, status_code = req_fn("data/exif_invalid.jpg", {"format": "png", "size": "full"})

    assert im_ref.width == im.width
    assert im_ref.height == im.height

    assert abs(im_absdiff(im, im_ref, im, only_fg=True) - 0) < 0.025
