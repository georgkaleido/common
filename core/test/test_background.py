from PIL import Image

from test.helpers import im_absdiff, pil_to_bytes

ABSDIFF_THRESH = .8

def test_bg_im_png(req_fn):
    im_alpha, _, _, _, = req_fn('data/CMYK.jpg', {'format': 'png', 'size': 'full', 'channels': 'alpha'})

    im_bg = Image.open('data/RGB.png')
    im_bg = im_bg.resize((im_alpha.width, im_alpha.height))

    im_color, im_in, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'png', 'size': 'full', 'bg_image_file': pil_to_bytes(im_bg)})

    assert im_absdiff(im_bg, im_color, im_alpha, only_bg=True) < ABSDIFF_THRESH

def test_bg_im_jpg(req_fn):
    im_alpha, _, _, _, = req_fn('data/CMYK.jpg', {'format': 'png', 'size': 'full', 'channels': 'alpha'})

    im_bg = Image.open('data/RGB.png')
    im_bg = im_bg.resize((im_alpha.width, im_alpha.height))

    im_color, im_in, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'jpg', 'size': 'full', 'bg_image_file': pil_to_bytes(im_bg)})

    assert im_absdiff(im_bg, im_color, im_alpha, only_bg=True) < ABSDIFF_THRESH

def test_bg_im_zip(req_fn):
    im_alpha, _, _, _, = req_fn('data/CMYK.jpg', {'format': 'png', 'size': 'full', 'channels': 'alpha'})

    im_bg = Image.open('data/RGB.png')
    im_bg = im_bg.resize((im_alpha.width, im_alpha.height))

    im, im_in, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'zip', 'size': 'full', 'bg_image_file': pil_to_bytes(im_bg)})

    assert im_absdiff(im_bg, im[0], im_alpha, only_bg=True) < ABSDIFF_THRESH

def test_bg_color_jpg(req_fn):
    im_color, im_in, headers, status_code = req_fn('data/RGB.png', {'format': 'jpg', 'size': 'full', 'bg_color': 'ffaa33'})

    import numpy as np
    im_color = np.array(im_color)
    assert im_color[0, 0, 0] == 255
    assert im_color[0, 0, 1] == 170
    assert im_color[0, 0, 2] == 51

def test_bg_color_zip(req_fn):
    im, im_in, headers, status_code = req_fn('data/RGB.png', {'format': 'zip', 'size': 'full', 'bg_color': 'ffaa33'})
    im_color, im_alpha = im

    import numpy as np

    im_color = np.array(im_color)
    im_alpha = np.array(im_alpha)

    assert im_color[0, 0, 0] == 255
    assert im_color[0, 0, 1] == 170
    assert im_color[0, 0, 2] == 51
    assert (im_alpha == 255).all()

def test_bg_color_transparent_zip(req_fn):
    im, im_in, headers, status_code = req_fn('data/RGB.png', {'format': 'zip', 'size': 'full', 'bg_color': 'ffaa3311'})
    im_color, im_alpha = im

    import numpy as np

    im_color = np.array(im_color)
    im_alpha = np.array(im_alpha)

    assert im_color[0, 0, 0] == 255
    assert im_color[0, 0, 1] == 170
    assert im_color[0, 0, 2] == 51
    assert im_alpha[0, 0] == 17

