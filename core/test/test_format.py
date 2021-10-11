def test_png(req_fn):
    im, im_in, headers, status_code = req_fn("data/RGB.png", {"format": "png"})
    assert headers.get("Content-Type") == "image/png"


def test_jpg(req_fn):
    im, im_in, headers, status_code = req_fn("data/RGB.png", {"format": "jpg"})
    assert headers.get("Content-Type") == "image/jpeg"


def test_zip(req_fn):
    im, im_in, headers, status_code = req_fn("data/RGB.png", {"format": "zip"})
    assert headers.get("Content-Type") == "application/zip"
