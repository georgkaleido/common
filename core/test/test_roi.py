
def test_default(req_fn):
    im, im_in, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'png', 'size': 'full', 'roi': '0% 0% 100% 100%'})

    assert im_in.width == im.width
    assert im_in.height == im.height

    import numpy as np
    im = np.array(im)

    # this image must have alpha values in last row
    assert (im[-1, :] > 0).any()

def test_relative(req_fn):
    im, im_in, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'png', 'size': 'full', 'roi': '20% 10% 80% 90%', 'channels': 'alpha'})

    assert im_in.width == im.width
    assert im_in.height == im.height

    w, h = im.width, im.height
    import numpy as np
    im = np.array(im)

    assert (im[:int(h * 0.1)] == 0).all()
    assert (im[-int(h * 0.1):] == 0).all()

    assert (im[:, :int(w * 0.2)] == 0).all()
    assert (im[:, -int(w * 0.2):] == 0).all()

def test_relative_exceed(req_fn):
    im, im_in, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'png', 'size': 'full', 'roi': '0% 0% 101% 100%', 'channels': 'alpha'})

    assert status_code == 400

def test_relative_order(req_fn):
    im, im_in, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'png', 'size': 'full', 'roi': '70% 0% 30% 100%', 'channels': 'alpha'})

    assert status_code == 200

def test_absolute(req_fn):
    im, im_in, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'png', 'size': 'full', 'roi': '50px 75px 255px 300px', 'channels': 'alpha'})

    assert im_in.width == im.width
    assert im_in.height == im.height

    import numpy as np
    im = np.array(im)

    assert (im[:75] == 0).all()
    assert (im[301:] == 0).all()

    assert (im[:, :50] == 0).all()
    assert (im[:, 256:] == 0).all()

def test_absolute_exceed(req_fn):
    im, im_in, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'png', 'size': 'full', 'roi': '0px 0px 1000px 100px', 'channels': 'alpha'})

    assert status_code == 400

def test_relative_zero(req_fn):
    im, im_in, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'png', 'size': 'full', 'roi': '100% 100% 100% 100%', 'channels': 'alpha'})

    assert status_code == 400

def test_absolute_zero(req_fn):
    im, im_in, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'png', 'size': 'full', 'roi': '100px 100px 100px 100px', 'channels': 'alpha'})

    assert status_code == 400