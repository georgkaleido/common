
# cmyk

def test_cmyk_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'jpg'})
    assert im.info.get('dpi') == (300, 300)

def test_cmyk_png(req_fn):
    im, _, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'png'})
    assert im.info.get('dpi') == (300, 300)

def test_cmyk_zip(req_fn):
    im, _, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'zip'})
    assert im[0].info.get('dpi') == (300, 300)
    assert im[1].info.get('dpi') == (300, 300)

# rgb

def test_rgb_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/RGB.png', {'format': 'jpg'})
    assert im.info.get('dpi') == (300, 300)

def test_rgb_png(req_fn):
    im, _, headers, status_code = req_fn('data/RGB.png', {'format': 'png'})
    assert im.info.get('dpi') == (300, 300)

def test_rgb_zip(req_fn):
    im, _, headers, status_code = req_fn('data/RGB.png', {'format': 'zip'})
    assert im[0].info.get('dpi') == (300, 300)
    assert im[1].info.get('dpi') == (300, 300)

# rgba

def test_rgba_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/RGBA.png', {'format': 'jpg'})
    assert im.info.get('dpi') == (300, 300)

def test_rgba_png(req_fn):
    im, _, headers, status_code = req_fn('data/RGBA.png', {'format': 'png'})
    assert im.info.get('dpi') == (300, 300)

def test_rgba_zip(req_fn):
    im, _, headers, status_code = req_fn('data/RGBA.png', {'format': 'zip'})
    assert im[0].info.get('dpi') == (300, 300)
    assert im[1].info.get('dpi') == (300, 300)

# l

def test_l_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/L.jpg', {'format': 'jpg'})
    assert im.info.get('dpi') == (300, 300)

def test_l_png(req_fn):
    im, _, headers, status_code = req_fn('data/L.jpg', {'format': 'png'})
    assert im.info.get('dpi') == (300, 300)

def test_l_zip(req_fn):
    im, _, headers, status_code = req_fn('data/L.jpg', {'format': 'zip'})
    assert im[0].info.get('dpi') == (300, 300)
    assert im[1].info.get('dpi') == (300, 300)

# la

def test_la_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/LA.png', {'format': 'jpg'})
    assert im.info.get('dpi') == (300, 300)

def test_la_png(req_fn):
    im, _, headers, status_code = req_fn('data/LA.png', {'format': 'png'})
    assert im.info.get('dpi') == (300, 300)

def test_la_zip(req_fn):
    im, _, headers, status_code = req_fn('data/LA.png', {'format': 'zip'})
    assert im[0].info.get('dpi') == (300, 300)
    assert im[1].info.get('dpi') == (300, 300)

# p

def test_p_jpg(req_fn):
    im, _, headers, status_code = req_fn('data/P.png', {'format': 'jpg'})
    assert im.info.get('dpi') == (300, 300)

def test_p_png(req_fn):
    im, _, headers, status_code = req_fn('data/P.png', {'format': 'png'})
    assert im.info.get('dpi') == (300, 300)

def test_p_zip(req_fn):
    im, _, headers, status_code = req_fn('data/P.png', {'format': 'zip'})
    assert im[0].info.get('dpi') == (300, 300)
    assert im[1].info.get('dpi') == (300, 300)