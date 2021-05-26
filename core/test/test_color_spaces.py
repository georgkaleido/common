
# rgb without color profile

def test_rgb_auto(req_fn):
    im, _, headers, status_code = req_fn('data/RGB.png', {'format': 'auto'})

    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_rgb_png(req_fn):
    im, _, headers, status_code = req_fn('data/RGB.png', {'format': 'png'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_rgb_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/RGB.png', {'format': 'jpg'})
    assert headers.get('Content-Type') == 'image/jpeg'
    assert im.mode == 'RGB'
    assert im.info.get('icc_profile') is None

def test_rgb_zip(req_fn):
    im, _, headers, status_code = req_fn('data/RGB.png', {'format': 'zip'})
    assert headers.get('Content-Type') == 'application/zip'
    assert im[0].mode == 'RGB'
    assert im[0].info.get('icc_profile') is None
    assert im[1].mode == 'L'
    assert im[1].info.get('icc_profile') is None


# rgb with color profile

def test_rgb_icc_auto(req_fn):
    im, _, headers, status_code = req_fn('data/RGB_icc.png', {'format': 'auto'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is not None

def test_rgb_icc_png(req_fn):
    im, _, headers, status_code = req_fn('data/RGB_icc.png', {'format': 'png'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is not None

def test_rgb_icc_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/RGB_icc.png', {'format': 'jpg'})
    assert headers.get('Content-Type') == 'image/jpeg'
    assert im.mode == 'RGB'
    assert im.info.get('icc_profile') is not None

def test_rgb_icc_zip(req_fn):
    im, _, headers, status_code = req_fn('data/RGB_icc.png', {'format': 'zip'})
    assert headers.get('Content-Type') == 'application/zip'
    assert im[0].mode == 'RGB'
    assert im[0].info.get('icc_profile') is not None
    assert im[1].mode == 'L'
    assert im[1].info.get('icc_profile') is None


# cmyk without color profile

def test_cmyk_auto(req_fn):
    im, _, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'auto'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_cmyk_png(req_fn):
    im, _, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'png'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_cmyk_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'jpg'})
    assert headers.get('Content-Type') == 'image/jpeg'
    assert im.mode == 'CMYK'
    assert im.info.get('icc_profile') is None

def test_cmyk_zip(req_fn):
    im, _, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'zip'})
    assert headers.get('Content-Type') == 'application/zip'
    assert im[0].mode == 'CMYK'
    assert im[0].info.get('icc_profile') is None
    assert im[1].mode == 'L'
    assert im[1].info.get('icc_profile') is None


# cmyk with color profile

def test_cmyk_icc_auto(req_fn):
    im, _, headers, status_code = req_fn('data/CMYK_icc.jpg', {'format': 'auto'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_cmyk_icc_png(req_fn):
    im, _, headers, status_code = req_fn('data/CMYK_icc.jpg', {'format': 'png'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_cmyk_icc_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/CMYK_icc.jpg', {'format': 'jpg'})
    assert headers.get('Content-Type') == 'image/jpeg'
    assert im.mode == 'CMYK'
    assert im.info.get('icc_profile') is not None

def test_cmyk_icc_zip(req_fn):
    im, _, headers, status_code = req_fn('data/CMYK_icc.jpg', {'format': 'zip'})
    assert headers.get('Content-Type') == 'application/zip'
    assert im[0].mode == 'CMYK'
    assert im[0].info.get('icc_profile') is not None
    assert im[1].mode == 'L'
    assert im[1].info.get('icc_profile') is None


# l without color profile

def test_l_auto(req_fn):
    im, _, headers, status_code = req_fn('data/L.jpg', {'format': 'auto'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_l_png(req_fn):
    im, _, headers, status_code = req_fn('data/L.jpg', {'format': 'png'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_l_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/L.jpg', {'format': 'jpg'})
    assert headers.get('Content-Type') == 'image/jpeg'
    assert im.mode == 'L'
    assert im.info.get('icc_profile') is None

def test_l_zip(req_fn):
    im, _, headers, status_code = req_fn('data/L.jpg', {'format': 'zip'})
    assert headers.get('Content-Type') == 'application/zip'
    assert im[0].mode == 'L'
    assert im[0].info.get('icc_profile') is None
    assert im[1].mode == 'L'
    assert im[1].info.get('icc_profile') is None


# l with color profile

def test_l_icc_auto(req_fn):
    im, _, headers, status_code = req_fn('data/L_icc.jpg', {'format': 'auto'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_l_icc_png(req_fn):
    im, _, headers, status_code = req_fn('data/L_icc.jpg', {'format': 'png'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_l_icc_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/L_icc.jpg', {'format': 'jpg'})
    assert headers.get('Content-Type') == 'image/jpeg'
    assert im.mode == 'L'
    assert im.info.get('icc_profile') is not None

def test_l_icc_zip(req_fn):
    im, _, headers, status_code = req_fn('data/L_icc.jpg', {'format': 'zip'})
    assert headers.get('Content-Type') == 'application/zip'
    assert im[0].mode == 'L'
    assert im[0].info.get('icc_profile') is not None
    assert im[1].mode == 'L'
    assert im[1].info.get('icc_profile') is None


# la without color profile

def test_la_auto(req_fn):
    im, _, headers, status_code = req_fn('data/LA.png', {'format': 'auto'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_la_png(req_fn):
    im, _, headers, status_code = req_fn('data/LA.png', {'format': 'png'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_la_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/LA.png', {'format': 'jpg'})
    assert headers.get('Content-Type') == 'image/jpeg'
    assert im.mode == 'RGB'
    assert im.info.get('icc_profile') is None

def test_la_zip(req_fn):
    im, _, headers, status_code = req_fn('data/LA.png', {'format': 'zip'})
    assert headers.get('Content-Type') == 'application/zip'
    assert im[0].mode == 'RGB'
    assert im[0].info.get('icc_profile') is None
    assert im[1].mode == 'L'
    assert im[1].info.get('icc_profile') is None


# la with color profile

def test_la_icc_auto(req_fn):
    im, _, headers, status_code = req_fn('data/LA_icc.png', {'format': 'auto'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_la_icc_png(req_fn):
    im, _, headers, status_code = req_fn('data/LA_icc.png', {'format': 'png'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_la_icc_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/LA_icc.png', {'format': 'jpg'})
    assert headers.get('Content-Type') == 'image/jpeg'
    assert im.mode == 'RGB'
    assert im.info.get('icc_profile') is None

def test_la_icc_zip(req_fn):
    im, _, headers, status_code = req_fn('data/LA_icc.png', {'format': 'zip'})
    assert headers.get('Content-Type') == 'application/zip'
    assert im[0].mode == 'RGB'
    assert im[0].info.get('icc_profile') is None
    assert im[1].mode == 'L'
    assert im[1].info.get('icc_profile') is None



# p without color profile

def test_p_auto(req_fn):
    im, _, headers, status_code = req_fn('data/P.png', {'format': 'auto'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_p_png(req_fn):
    im, _, headers, status_code = req_fn('data/P.png', {'format': 'png'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_p_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/P.png', {'format': 'jpg'})
    assert headers.get('Content-Type') == 'image/jpeg'
    assert im.mode == 'RGB'
    assert im.info.get('icc_profile') is None

def test_p_zip(req_fn):
    im, _, headers, status_code = req_fn('data/P.png', {'format': 'zip'})
    assert headers.get('Content-Type') == 'application/zip'
    assert im[0].mode == 'RGB'
    assert im[0].info.get('icc_profile') is None
    assert im[1].mode == 'L'
    assert im[1].info.get('icc_profile') is None


# p with color profile

def test_p_icc_auto(req_fn):
    im, _, headers, status_code = req_fn('data/P_icc.png', {'format': 'auto'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_p_icc_png(req_fn):
    im, _, headers, status_code = req_fn('data/P_icc.png', {'format': 'png'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'RGBA'
    assert im.info.get('icc_profile') is None

def test_p_icc_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/P_icc.png', {'format': 'jpg'})
    assert headers.get('Content-Type') == 'image/jpeg'
    assert im.mode == 'RGB'
    assert im.info.get('icc_profile') is None

def test_p_icc_zip(req_fn):
    im, _, headers, status_code = req_fn('data/P_icc.png', {'format': 'zip'})
    assert headers.get('Content-Type') == 'application/zip'
    assert im[0].mode == 'RGB'
    assert im[0].info.get('icc_profile') is None
    assert im[1].mode == 'L'
    assert im[1].info.get('icc_profile') is None
