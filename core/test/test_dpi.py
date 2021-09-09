
def convert_dpi_as_int(dpi):
    dpi = (int(round(dpi[0])), int(round(dpi[1])))
    return dpi, dpi

# cmyk

def test_cmyk_jpg(req_fn):
    im, im_in, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'jpg'})
    dpi = convert_dpi_as_int(im.info.get('dpi'))
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    assert dpi == dpi_in

def test_cmyk_png(req_fn):
    im, im_in, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'png'})
    dpi = convert_dpi_as_int(im.info.get('dpi'))
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    assert dpi == dpi_in

def test_cmyk_zip(req_fn):
    im, im_in, headers, status_code = req_fn('data/CMYK.jpg', {'format': 'zip'})
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    for i in range(2):
        dpi = convert_dpi_as_int(im[i].info.get('dpi'))
        assert dpi == dpi_in

# rgb

def test_rgb_jpg(req_fn):
    im, im_in, headers, status_code = req_fn('data/RGB.png', {'format': 'jpg'})
    dpi = convert_dpi_as_int(im.info.get('dpi'))
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    assert dpi == dpi_in

def test_rgb_png(req_fn):
    im, im_in, headers, status_code = req_fn('data/RGB.png', {'format': 'png'})
    dpi = convert_dpi_as_int(im.info.get('dpi'))
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    assert dpi == dpi_in

def test_rgb_zip(req_fn):
    im, im_in, headers, status_code = req_fn('data/RGB.png', {'format': 'zip'})
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    for i in range(2):
        dpi = convert_dpi_as_int(im[i].info.get('dpi'))
        assert dpi == dpi_in

# rgba

def test_rgba_jpg(req_fn):
    im, im_in, headers, status_code = req_fn('data/RGBA.png', {'format': 'jpg'})
    dpi = convert_dpi_as_int(im.info.get('dpi'))
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    assert dpi == dpi_in

def test_rgba_png(req_fn):
    im, im_in, headers, status_code = req_fn('data/RGBA.png', {'format': 'png'})
    dpi = convert_dpi_as_int(im.info.get('dpi'))
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    assert dpi == dpi_in

def test_rgba_zip(req_fn):
    im, im_in, headers, status_code = req_fn('data/RGBA.png', {'format': 'zip'})
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    for i in range(2):
        dpi = convert_dpi_as_int(im[i].info.get('dpi'))
        assert dpi == dpi_in

# l

def test_l_jpg(req_fn):
    im, im_in, headers, status_code = req_fn('data/L.jpg', {'format': 'jpg'})
    dpi = convert_dpi_as_int(im.info.get('dpi'))
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    assert dpi == dpi_in

def test_l_png(req_fn):
    im, im_in, headers, status_code = req_fn('data/L.jpg', {'format': 'png'})
    dpi = convert_dpi_as_int(im.info.get('dpi'))
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    assert dpi == dpi_in

def test_l_zip(req_fn):
    im, im_in, headers, status_code = req_fn('data/L.jpg', {'format': 'zip'})
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    for i in range(2):
        dpi = convert_dpi_as_int(im[i].info.get('dpi'))
        assert dpi == dpi_in

# la

def test_la_jpg(req_fn):
    im, im_in, headers, status_code = req_fn('data/LA.png', {'format': 'jpg'})
    dpi = convert_dpi_as_int(im.info.get('dpi'))
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    assert dpi == dpi_in

def test_la_png(req_fn):
    im, im_in, headers, status_code = req_fn('data/LA.png', {'format': 'png'})
    dpi = convert_dpi_as_int(im.info.get('dpi'))
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    assert dpi == dpi_in

def test_la_zip(req_fn):
    im, im_in, headers, status_code = req_fn('data/LA.png', {'format': 'zip'})
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    for i in range(2):
        dpi = convert_dpi_as_int(im[i].info.get('dpi'))
        assert dpi == dpi_in

# p

def test_p_jpg(req_fn):
    im, im_in, headers, status_code = req_fn('data/P.png', {'format': 'jpg'})
    dpi = convert_dpi_as_int(im.info.get('dpi'))
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    assert dpi == dpi_in

def test_p_png(req_fn):
    im, im_in, headers, status_code = req_fn('data/P.png', {'format': 'png'})
    dpi = convert_dpi_as_int(im.info.get('dpi'))
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    assert dpi == dpi_in

def test_p_zip(req_fn):
    im, im_in, headers, status_code = req_fn('data/P.png', {'format': 'zip'})
    dpi_in = convert_dpi_as_int(im_in.info.get('dpi'))
    for i in range(2):
        dpi = convert_dpi_as_int(im[i].info.get('dpi'))
        assert dpi == dpi_in
