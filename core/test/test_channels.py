def test_jpg_alpha(req_fn):
    im, _, headers, status_code = req_fn('data/CMYK_icc.jpg', {'format': 'jpg', 'channels': 'alpha'})
    assert headers.get('Content-Type') == 'image/jpeg'
    assert im.mode == 'L'
    assert im.info.get('icc_profile') is None

def test_png_alpha(req_fn):
    im, _, headers, status_code = req_fn('data/CMYK_icc.jpg', {'format': 'png', 'channels': 'alpha'})
    assert headers.get('Content-Type') == 'image/png'
    assert im.mode == 'L'
    assert im.info.get('icc_profile') is None

def test_zip_alpha(req_fn):
    im, _, headers, status_code = req_fn('data/CMYK_icc.jpg', {'format': 'zip', 'channels': 'alpha'})
    assert headers.get('Content-Type') == 'application/zip'
    assert im[0].mode == 'CMYK'
    assert im[1].mode == 'L'
    assert im[0].info.get('icc_profile') is not None
    assert im[1].info.get('icc_profile') is None

def test_noformat_alpha(req_fn):
    im, _, headers, status_code = req_fn('data/CMYK_icc.jpg', {'channels': 'alpha'})
    assert headers.get('Content-Type') == 'image/jpeg'
    assert im.mode == 'L'
    assert im.info.get('icc_profile') is None