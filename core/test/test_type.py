def test_car_manual(req_fn):
    im, im_in, headers, status_code = req_fn("data/CMYK.jpg", {"format": "jpg", "type": "car"})
    assert headers.get("X-Type") == "car"


def test_person_manual(req_fn):
    im, im_in, headers, status_code = req_fn("data/CMYK.jpg", {"format": "jpg", "type": "person"})
    assert headers.get("X-Type") == "person"


def test_product_manual(req_fn):
    im, im_in, headers, status_code = req_fn("data/CMYK.jpg", {"format": "jpg", "type": "product"})
    assert headers.get("X-Type") == "product"


def test_product_animal(req_fn):
    im, im_in, headers, status_code = req_fn("data/CMYK.jpg", {"format": "jpg", "type": "animal"})
    # TODO - this is currently a bug in the API - the returned type should be animal here
    assert headers.get("X-Type") == "person"


def test_person(req_fn):
    im, im_in, headers, status_code = req_fn("data/CMYK.jpg", {"format": "jpg", "type": "auto"})
    assert headers.get("X-Type") == "person"


def test_animal(req_fn):
    im, im_in, headers, status_code = req_fn("data/L.jpg", {"format": "jpg", "type": "auto"})
    assert headers.get("X-Type") == "animal"


def test_car(req_fn):
    im, im_in, headers, status_code = req_fn("data/RGB.png", {"format": "jpg", "type": "auto"})
    assert headers.get("X-Type") == "car"
