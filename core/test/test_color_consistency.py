from test.helpers import im_absdiff

ABSDIFF_THRESH = .8

# CMYK

def test_cmyk(req_fn):

    im, im_in, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'zip', 'size': 'full'})
    im_color, im_alpha = im

    assert im_color.mode == 'CMYK'
    assert im_color.info.get('icc_profile') is None

    assert im_absdiff(im_in, im_color, im_alpha) < ABSDIFF_THRESH

def test_cmyk_icc(req_fn):

    im, im_in, headers, status_code = req_fn('data/CMYK_icc.jpg', {'format': 'zip', 'size': 'full'})
    im_color, im_alpha = im

    assert im_color.mode == 'CMYK'
    assert im_color.info.get('icc_profile') is not None

    assert im_absdiff(im_in, im_color, im_alpha) < ABSDIFF_THRESH

def test_cmyk_icc_bg(req_fn):

    im_alpha, _, _, _,              = req_fn('data/CMYK_icc.jpg', {'format': 'png', 'size': 'full', 'channels': 'alpha'})
    im, im_in, headers, status_code = req_fn('data/CMYK_icc.jpg', {'format': 'zip', 'size': 'full', 'bg_color': 'ffffffff'})
    im_color = im[0]

    assert im_color.mode == 'CMYK'
    assert im_color.info.get('icc_profile') is not None

    assert im_absdiff(im_in, im_color, im_alpha, only_fg=True) < ABSDIFF_THRESH

def test_cmyk_icc_bg_im(req_fn):

    with open('data/RGB_icc.png', 'rb') as f:
        bg_image_file = f.read()

    im_alpha, _, _, _,              = req_fn('data/CMYK_icc.jpg', {'format': 'png', 'size': 'full', 'channels': 'alpha'})
    im, im_in, headers, status_code = req_fn('data/CMYK_icc.jpg', {'format': 'zip', 'size': 'full', 'bg_image_file': bg_image_file})
    im_color = im[0]

    assert im_color.mode == 'CMYK'
    assert im_color.info.get('icc_profile') is not None

    assert im_absdiff(im_in, im_color, im_alpha, only_fg=True) < ABSDIFF_THRESH

# RGB

def test_rgb(req_fn):

    im, im_in, headers, status_code = req_fn('data/RGB.png', {'format': 'zip', 'size': 'full', 'semitransparency': 'false', 'shadow': 'false'})
    im_color, im_alpha = im

    assert im_color.mode == 'RGB'
    assert im_color.info.get('icc_profile') is None

    assert im_absdiff(im_in, im_color, im_alpha) < ABSDIFF_THRESH

def test_rgb_png(req_fn):

    im, im_in, headers, status_code = req_fn('data/RGB.png', {'format': 'png', 'size': 'full', 'semitransparency': 'false', 'shadow': 'false'})

    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

    assert im_absdiff(im_in, im, im, only_fg=True) < 0.06

def test_rgb_icc(req_fn):

    im, im_in, headers, status_code = req_fn('data/RGB_icc.png', {'format': 'zip', 'size': 'full', 'semitransparency': 'false', 'shadow': 'false'})
    im_color, im_alpha = im

    assert im_color.mode == 'RGB'
    assert im_color.info.get('icc_profile') is not None

    assert im_absdiff(im_in, im_color, im_alpha) < ABSDIFF_THRESH

def test_rgb_icc_png(req_fn):

    im, im_in, headers, status_code = req_fn('data/RGB_icc.png', {'format': 'png', 'size': 'full', 'semitransparency': 'false', 'shadow': 'false'})

    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is not None

    assert im_absdiff(im_in, im, im, only_fg=True) < 0.06

def test_rgb_icc_bg(req_fn):

    im_alpha, _, _, _,              = req_fn('data/RGB_icc.png', {'format': 'png', 'size': 'full', 'channels': 'alpha'})
    im, im_in, headers, status_code = req_fn('data/RGB_icc.png', {'format': 'zip', 'size': 'full', 'bg_color': 'ffffffff', 'semitransparency': 'false', 'shadow': 'false'})
    im_color = im[0]

    assert im_color.mode == 'RGB'
    assert im_color.info.get('icc_profile') is not None

    assert im_absdiff(im_in, im_color, im_alpha, only_fg=True) < ABSDIFF_THRESH

def test_rgb_icc_bg_png(req_fn):

    im_alpha, _, _, _,              = req_fn('data/RGB_icc.png', {'format': 'png', 'size': 'full', 'channels': 'alpha'})
    im, im_in, headers, status_code = req_fn('data/RGB_icc.png', {'format': 'png', 'size': 'full', 'bg_color': 'ffffffff', 'semitransparency': 'false', 'shadow': 'false'})

    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is not None

    assert im_absdiff(im_in, im, im_alpha, only_fg=True) < 0.06

def test_rgb_icc_bg_im(req_fn):

    with open('data/CMYK_icc.jpg', 'rb') as f:
        bg_image_file = f.read()

    im_alpha, _, _, _,              = req_fn('data/RGB_icc.png', {'format': 'png', 'size': 'full', 'channels': 'alpha'})
    im, im_in, headers, status_code = req_fn('data/RGB_icc.png', {'format': 'zip', 'size': 'full', 'bg_image_file': bg_image_file, 'semitransparency': 'false', 'shadow': 'false'})
    im_color = im[0]

    assert im_color.mode == 'RGB'
    assert im_color.info.get('icc_profile') is not None

    assert im_absdiff(im_in, im_color, im_alpha, only_fg=True) < ABSDIFF_THRESH

# L

def test_l(req_fn):

    im, im_in, headers, status_code = req_fn('data/L.jpg', {'format': 'zip', 'size': 'full'})
    im_color, im_alpha = im

    assert im_color.mode == 'L'
    assert im_color.info.get('icc_profile') is None

    assert im_absdiff(im_in, im_color, im_alpha) < ABSDIFF_THRESH

def test_l_icc(req_fn):

    im, im_in, headers, status_code = req_fn('data/L_icc.jpg', {'format': 'zip', 'size': 'full'})
    im_color, im_alpha = im

    assert im_color.mode == 'L'
    assert im_color.info.get('icc_profile') is not None

    assert im_absdiff(im_in, im_color, im_alpha) < ABSDIFF_THRESH

def test_l_icc_bg(req_fn):

    im_alpha, _, _, _,              = req_fn('data/L_icc.jpg', {'format': 'png', 'size': 'full', 'channels': 'alpha'})
    im, im_in, headers, status_code = req_fn('data/L_icc.jpg', {'format': 'zip', 'size': 'full', 'bg_color': 'ffffffff'})
    im_color = im[0]

    assert im_color.mode == 'L'
    assert im_color.info.get('icc_profile') is not None

    assert im_absdiff(im_in, im_color, im_alpha, only_fg=True) < ABSDIFF_THRESH

def test_l_icc_bg_im(req_fn):

    with open('data/CMYK_icc.jpg', 'rb') as f:
        bg_image_file = f.read()

    im_alpha, _, _, _,              = req_fn('data/L_icc.jpg', {'format': 'png', 'size': 'full', 'channels': 'alpha'})
    im, im_in, headers, status_code = req_fn('data/L_icc.jpg', {'format': 'zip', 'size': 'full', 'bg_image_file': bg_image_file})
    im_color = im[0]

    assert im_color.mode == 'L'
    assert im_color.info.get('icc_profile') is not None

    assert im_absdiff(im_in, im_color, im_alpha, only_fg=True) < ABSDIFF_THRESH
