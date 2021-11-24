from test.conftest import RemovebgMessage
from test.core.helpers import process_image
from test.helpers import scaled_im

import numpy as np
from tests.utils import convert_to_image, read_image


def test_tight(core_server_tester):
    msg = RemovebgMessage()
    msg.crop = True
    msg.channels = "alpha"
    msg.roi = [0, 0, 396, 639]
    im_in_bytes = read_image("../data/CMYK.jpg")
    im_in = convert_to_image(im_in_bytes)
    msg.data = im_in_bytes
    im = process_image(core_server_tester, msg)["im"]
    assert im_in.width > im.width
    assert im_in.height > im.height

    im = np.array(im)
    assert (im[0] > 0).any()
    assert (im[-1] > 0).any()
    assert (im[:, 0] > 0).any()
    assert (im[:-1] > 0).any()


def test_tight_mp_png(core_server_tester):
    msg = RemovebgMessage()
    msg.data = scaled_im("../data/CMYK.jpg", 12)
    msg.crop = True
    msg.channels = "alpha"
    im = process_image(core_server_tester, msg)["im"]
    # megapixels should be capped with uncropped dimensions,
    # so here it should not be 10 mp
    assert im.width * im.height < 9500000


def test_tight_mp_jpg(core_server_tester):
    msg = RemovebgMessage()
    msg.data = scaled_im("../data/CMYK.jpg", 27)
    msg.crop = True
    msg.format = "jpg"
    msg.channels = "alpha"
    msg.roi = [0, 0, 4091, 6596]
    im = process_image(core_server_tester, msg)["im"]
    # megapixels should be capped with uncropped dimensions,
    # so here it should not be 10 mp
    assert im.width * im.height < 9500000


def test_tight_mp_zip(core_server_tester):
    msg = RemovebgMessage()
    msg.data = scaled_im("../data/CMYK.jpg", 27)
    msg.crop = True
    msg.channels = "alpha"
    msg.format = "zip"
    msg.roi = [0, 0, 4091, 6596]
    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    # megapixels should be capped with uncropped dimensions,
    # so here it should not be 10 mp
    assert im_color.width * im_color.height < 24000000
    assert im_alpha.width * im_alpha.height < 24000000


def test_margin_abs1(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/CMYK.jpg")
    msg.crop = True
    msg.roi = [0, 0, 396, 639]
    im_ref = process_image(core_server_tester, msg)["im"]

    msg.crop_margin = {
        "top": 50,
        "top_relative": False,
        "right": 50,
        "right_relative": False,
        "bottom": 50,
        "bottom_relative": False,
        "left": 50,
        "left_relative": False,
    }

    im = process_image(core_server_tester, msg)["im"]

    assert im.width == im_ref.width + 100
    assert im.height == im_ref.height + 100

    im = np.array(im)
    assert (im[:50] == 0).all()
    assert (im[-50:] == 0).all()
    assert (im[:, :50] == 0).all()
    assert (im[:, -50:] == 0).all()


def test_margin_rel1(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/CMYK.jpg")
    msg.crop = True
    msg.roi = [0, 0, 396, 639]
    im_ref = process_image(core_server_tester, msg)["im"]

    msg.crop_margin = {
        "top": 10,
        "top_relative": True,
        "right": 10,
        "right_relative": True,
        "bottom": 10,
        "bottom_relative": True,
        "left": 10,
        "left_relative": True,
    }

    im = process_image(core_server_tester, msg)["im"]

    assert im.width == int(im_ref.width * 1.2 + 0.5)
    assert im.height == int(im_ref.height * 1.2 + 0.5)


def test_margin_abs2(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/CMYK.jpg")
    msg.crop = True
    msg.roi = [0, 0, 396, 639]
    im_ref = process_image(core_server_tester, msg)["im"]

    msg.crop_margin = {
        "top": 50,
        "top_relative": False,
        "right": 25,
        "right_relative": False,
        "bottom": 50,
        "bottom_relative": False,
        "left": 25,
        "left_relative": False,
    }

    im = process_image(core_server_tester, msg)["im"]

    assert im.width == im_ref.width + 50
    assert im.height == im_ref.height + 100

    im = np.array(im)
    assert (im[:50] == 0).all()
    assert (im[-50:] == 0).all()
    assert (im[:, :25] == 0).all()
    assert (im[:, -25:] == 0).all()


def test_margin_rel2(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/CMYK.jpg")
    msg.crop = True
    msg.roi = [0, 0, 396, 639]
    im_ref = process_image(core_server_tester, msg)["im"]

    msg.crop_margin = {
        "top": 10,
        "top_relative": True,
        "right": 5,
        "right_relative": True,
        "bottom": 10,
        "bottom_relative": True,
        "left": 5,
        "left_relative": True,
    }
    im = process_image(core_server_tester, msg)["im"]

    assert im.width == int(im_ref.width * 1.1 + 0.5)
    assert im.height == int(im_ref.height * 1.2 + 0.5)


def test_margin_abs4(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/CMYK.jpg")
    msg.crop = True
    msg.roi = [0, 0, 396, 639]
    im_ref = process_image(core_server_tester, msg)["im"]

    msg.crop_margin = {
        "top": 10,
        "top_relative": False,
        "right": 20,
        "right_relative": False,
        "bottom": 30,
        "bottom_relative": False,
        "left": 40,
        "left_relative": False,
    }

    im = process_image(core_server_tester, msg)["im"]

    assert im.width == im_ref.width + 60
    assert im.height == im_ref.height + 40

    im = np.array(im)
    assert (im[:10] == 0).all()
    assert (im[-30:] == 0).all()
    assert (im[:, -20:] == 0).all()
    assert (im[:, :40] == 0).all()


def test_margin_rel4(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/CMYK.jpg")
    msg.crop = True
    msg.roi = [0, 0, 396, 639]
    im_ref = process_image(core_server_tester, msg)["im"]

    msg.crop_margin = {
        "top": 1,
        "top_relative": True,
        "right": 2,
        "right_relative": True,
        "bottom": 3,
        "bottom_relative": True,
        "left": 4,
        "left_relative": True,
    }
    im = process_image(core_server_tester, msg)["im"]

    assert im.width == int(im_ref.width * 1.06 + 0.5)
    assert im.height == int(im_ref.height * 1.04 + 0.5)


def test_margin_rel_clamp_valid(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/CMYK.jpg")
    msg.crop = True
    msg.roi = [0, 0, 396, 639]
    msg.channels = "alpha"
    msg.crop_margin = {
        "top": 50,
        "top_relative": True,
        "right": 50,
        "right_relative": True,
        "bottom": 50,
        "bottom_relative": True,
        "left": 50,
        "left_relative": True,
    }
    result = core_server_tester.request(msg.serialize())
    assert result[b"status"] == b"ok"


def test_margin_abs_clamp_valid(core_server_tester):
    msg = RemovebgMessage()
    msg.data = read_image("../data/CMYK.jpg")
    msg.crop = True
    msg.roi = [0, 0, 396, 639]
    msg.channels = "alpha"
    msg.crop_margin = {
        "top": 500,
        "top_relative": False,
        "right": 500,
        "right_relative": False,
        "bottom": 500,
        "bottom_relative": False,
        "left": 500,
        "left_relative": False,
    }
    result = core_server_tester.request(msg.serialize())
    assert result[b"status"] == b"ok"


def test_margin_rel_huge(core_server_tester):
    msg = RemovebgMessage()
    msg.data = scaled_im("../data/CMYK.jpg", 25)
    msg.crop = True
    msg.roi = [0, 0, 3936, 6347]
    msg.channels = "alpha"
    msg.format = "jpg"
    msg.megapixels = 25
    msg.crop_margin = {
        "top": 50,
        "top_relative": True,
        "right": 50,
        "right_relative": True,
        "bottom": 50,
        "bottom_relative": True,
        "left": 50,
        "left_relative": True,
    }
    im = process_image(core_server_tester, msg)["im"]
    assert im.width * im.height > 25000000


def test_margin_abs_huge(core_server_tester):
    msg = RemovebgMessage()
    msg.data = scaled_im("../data/CMYK.jpg", 25)
    msg.crop = True
    msg.roi = [0, 0, 3936, 6347]
    msg.channels = "alpha"
    msg.format = "jpg"
    msg.megapixels = 25
    msg.crop_margin = {
        "top": 500,
        "top_relative": False,
        "right": 500,
        "right_relative": False,
        "bottom": 500,
        "bottom_relative": False,
        "left": 500,
        "left_relative": False,
    }
    im = process_image(core_server_tester, msg)["im"]
    assert im.width * im.height > 25000000


def test_margin_rel_huge_png(core_server_tester):
    msg = RemovebgMessage()
    msg.data = scaled_im("../data/CMYK.jpg", 10)
    msg.crop = True
    msg.roi = [0, 0, 2489, 4014]
    msg.channels = "alpha"
    msg.crop_margin = {
        "top": 50,
        "top_relative": True,
        "right": 50,
        "right_relative": True,
        "bottom": 50,
        "bottom_relative": True,
        "left": 50,
        "left_relative": True,
    }
    im = process_image(core_server_tester, msg)["im"]
    assert im.width * im.height > 10000000


def test_margin_abs_huge_png(core_server_tester):
    msg = RemovebgMessage()
    msg.data = scaled_im("../data/CMYK.jpg", 10)
    msg.crop = True
    msg.roi = [0, 0, 2489, 4014]
    msg.channels = "alpha"
    msg.crop_margin = {
        "top": 500,
        "top_relative": False,
        "right": 500,
        "right_relative": False,
        "bottom": 500,
        "bottom_relative": False,
        "left": 500,
        "left_relative": False,
    }
    im = process_image(core_server_tester, msg)["im"]
    assert im.width * im.height > 10000000


def test_foreground_anchors(core_server_tester):
    msg = RemovebgMessage()
    msg.crop = True
    msg.channels = "alpha"
    im_in_bytes = read_image("../data/RGB.png")
    im_in = convert_to_image(im_in_bytes)
    msg.data = im_in_bytes
    result = process_image(core_server_tester, msg, return_result_dict=True)
    im = result["im"]

    input_foreground_left = result["result"][b"input_foreground_left"]
    input_foreground_top = result["result"][b"input_foreground_top"]
    input_foreground_width = result["result"][b"input_foreground_width"]
    input_foreground_height = result["result"][b"input_foreground_height"]

    assert 0 < input_foreground_left < im_in.width
    assert 0 < input_foreground_top < im_in.height
    assert 0 < input_foreground_width
    assert 0 < input_foreground_height
    assert input_foreground_left + input_foreground_width <= im_in.width
    assert input_foreground_top + input_foreground_height <= im_in.height
    assert im.width == input_foreground_width
    assert im.height == input_foreground_height
    assert im_in.width > im.width
    assert im_in.height > im.height


def test_foreground_anchors_no_crop(core_server_tester):
    msg = RemovebgMessage()
    msg.crop = False
    msg.channels = "alpha"
    im_in_bytes = read_image("../data/RGB.png")
    im_in = convert_to_image(im_in_bytes)
    msg.data = im_in_bytes
    result = process_image(core_server_tester, msg, return_result_dict=True)
    im = result["im"]

    input_foreground_left = result["result"][b"input_foreground_left"]
    input_foreground_top = result["result"][b"input_foreground_top"]
    input_foreground_width = result["result"][b"input_foreground_width"]
    input_foreground_height = result["result"][b"input_foreground_height"]

    assert 0 < input_foreground_left < im_in.width
    assert 0 < input_foreground_top < im_in.height
    assert 0 < input_foreground_width
    assert 0 < input_foreground_height
    assert input_foreground_left + input_foreground_width <= im_in.width
    assert input_foreground_top + input_foreground_height <= im_in.height
    assert im.width > input_foreground_width
    assert im.height > input_foreground_height
    assert im_in.width == im.width
    assert im_in.height == im.height

