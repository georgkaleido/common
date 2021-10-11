def test_no_foreground(req_fn):
    im, _, headers, status_code = req_fn("data/white.jpg", {"format": "jpg"})
    assert status_code == 400


def test_truncated(req_fn):
    im, _, headers, status_code = req_fn("data/truncated.jpg", {"format": "jpg"})
    assert status_code == 400
