from test.conftest import RemovebgMessage
from test.core.helpers import process_image

from tests.utils import read_image


def test_rgb_auto(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "auto"
    msg.crop = False
    msg.roi = [0, 0, 639, 358]
    msg.data = read_image("../data/RGB.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_rgb_png(core_server_tester):
    msg = RemovebgMessage()
    msg.roi = [0, 0, 639, 358]
    msg.data = read_image("../data/RGB.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_rgb_jpg(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "jpg"
    msg.roi = [0, 0, 639, 358]
    msg.data = read_image("../data/RGB.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "JPEG"
    assert im.mode == "RGB"
    assert im.info.get("icc_profile") is None


# rgb with color profile


def test_rgb_icc_auto(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "auto"
    msg.roi = [0, 0, 639, 358]
    msg.data = read_image("../data/RGB_icc.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is not None


def test_rgb_icc_png(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "png"
    msg.roi = [0, 0, 639, 358]
    msg.data = read_image("../data/RGB_icc.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is not None


def test_rgb_icc_jpg(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "jpg"
    msg.roi = [0, 0, 639, 358]
    msg.data = read_image("../data/RGB_icc.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "JPEG"
    assert im.mode == "RGB"
    assert im.info.get("icc_profile") is not None


def test_rgb_icc_zip(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "zip"
    msg.roi = [0, 0, 639, 358]
    msg.data = read_image("../data/RGB_icc.png")
    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    assert im_color.mode == "RGB"
    assert im_color.info.get("icc_profile") is not None
    assert im_alpha.mode == "L"
    assert im_alpha.info.get("icc_profile") is None


# cmyk without color profile


def test_cmyk_auto(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "auto"
    msg.roi = [0, 0, 396, 639]
    msg.data = read_image("../data/CMYK.jpg")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_cmyk_png(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "png"
    msg.data = read_image("../data/CMYK.jpg")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_cmyk_jpg(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "jpg"
    msg.data = read_image("../data/CMYK.jpg")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "JPEG"
    assert im.mode == "CMYK"
    assert im.info.get("icc_profile") is None


def test_cmyk_zip(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "zip"
    msg.data = read_image("../data/CMYK.jpg")
    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    assert im_color.mode == "CMYK"
    assert im_color.info.get("icc_profile") is None
    assert im_alpha.mode == "L"
    assert im_alpha.info.get("icc_profile") is None


# cmyk with color profile


def test_cmyk_icc_auto(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "auto"
    msg.roi = [0, 0, 396, 639]
    msg.data = read_image("../data/CMYK_icc.jpg")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_cmyk_icc_png(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "png"
    msg.data = read_image("../data/CMYK_icc.jpg")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_cmyk_icc_jpg(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "jpg"
    msg.roi = [0, 0, 396, 639]
    msg.data = read_image("../data/CMYK_icc.jpg")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "JPEG"
    assert im.mode == "CMYK"
    assert im.info.get("icc_profile") is not None


def test_cmyk_icc_zip(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "zip"
    msg.data = read_image("../data/CMYK_icc.jpg")
    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    assert im_color.mode == "CMYK"
    assert im_color.info.get("icc_profile") is not None
    assert im_alpha.mode == "L"
    assert im_alpha.info.get("icc_profile") is None


# l without color profile


def test_l_auto(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "auto"
    msg.data = read_image("../data/L.jpg")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_l_png(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "png"
    msg.data = read_image("../data/L.jpg")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_l_jpg(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "jpg"
    msg.data = read_image("../data/L.jpg")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "JPEG"
    assert im.mode == "L"
    assert im.info.get("icc_profile") is None


def test_l_zip(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "zip"
    msg.data = read_image("../data/L.jpg")
    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    assert im_color.mode == "L"
    assert im_color.info.get("icc_profile") is None
    assert im_alpha.mode == "L"
    assert im_alpha.info.get("icc_profile") is None


# l with color profile


def test_l_icc_auto(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "auto"
    msg.data = read_image("../data/L_icc.jpg")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_l_icc_png(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "png"
    msg.data = read_image("../data/L_icc.jpg")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_l_icc_jpg(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "jpg"
    msg.data = read_image("../data/L_icc.jpg")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "JPEG"
    assert im.mode == "L"
    assert im.info.get("icc_profile") is not None


def test_l_icc_zip(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "zip"
    msg.data = read_image("../data/L_icc.jpg")
    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    assert im_color.mode == "L"
    assert im_color.info.get("icc_profile") is not None
    assert im_alpha.mode == "L"
    assert im_alpha.info.get("icc_profile") is None


# la without color profile


def test_la_auto(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "auto"
    msg.data = read_image("../data/LA.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_la_png(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "png"
    msg.data = read_image("../data/LA.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_la_jpg(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "jpg"
    msg.data = read_image("../data/LA.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "JPEG"
    assert im.mode == "RGB"
    assert im.info.get("icc_profile") is None


def test_la_zip(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "zip"
    msg.data = read_image("../data/LA.png")
    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    assert im_color.mode == "RGB"
    assert im_color.info.get("icc_profile") is None
    assert im_alpha.mode == "L"
    assert im_alpha.info.get("icc_profile") is None


# la with color profile


def test_la_icc_auto(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "auto"
    msg.data = read_image("../data/LA_icc.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_la_icc_png(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "png"
    msg.data = read_image("../data/LA_icc.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_la_icc_jpg(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "jpg"
    msg.data = read_image("../data/LA_icc.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "JPEG"
    assert im.mode == "RGB"
    assert im.info.get("icc_profile") is None


def test_la_icc_zip(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "zip"
    msg.data = read_image("../data/LA_icc.png")
    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    assert im_color.mode == "RGB"
    assert im_color.info.get("icc_profile") is None
    assert im_alpha.mode == "L"
    assert im_alpha.info.get("icc_profile") is None


# p without color profile


def test_p_auto(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "auto"
    msg.data = read_image("../data/P.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_p_png(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "png"
    msg.data = read_image("../data/P.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_p_jpg(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "jpg"
    msg.data = read_image("../data/P.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "JPEG"
    assert im.mode == "RGB"
    assert im.info.get("icc_profile") is None


def test_p_zip(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "zip"
    msg.data = read_image("../data/P.png")
    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    assert im_color.mode == "RGB"
    assert im_color.info.get("icc_profile") is None
    assert im_alpha.mode == "L"
    assert im_alpha.info.get("icc_profile") is None


# p with color profile


def test_p_icc_auto(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "auto"
    msg.data = read_image("../data/P_icc.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_p_icc_png(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "png"
    msg.data = read_image("../data/P_icc.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "PNG"
    assert im.mode == "RGBA"
    assert im.info.get("icc_profile") is None


def test_p_icc_jpg(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "jpg"
    msg.data = read_image("../data/P_icc.png")
    im = process_image(core_server_tester, msg)["im"]
    assert im.format == "JPEG"
    assert im.mode == "RGB"
    assert im.info.get("icc_profile") is None


def test_p_icc_zip(core_server_tester):
    msg = RemovebgMessage()
    msg.format = "zip"
    msg.data = read_image("../data/P_icc.png")
    image_dict = process_image(core_server_tester, msg)
    im_color, im_alpha = image_dict["im_color"], image_dict["im_alpha"]
    assert im_color.mode == "RGB"
    assert im_color.info.get("icc_profile") is None
    assert im_alpha.mode == "L"
    assert im_alpha.info.get("icc_profile") is None
