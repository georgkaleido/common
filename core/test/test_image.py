import os
import tempfile
from unittest.mock import patch, ANY

import cv2
from kaleido.image import RGB, BGR, BGRA, ALPHA

from removebg.image import SmartAlphaImage
import numpy as np


def check_encode(image, im_format: str):
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_img_path = os.path.join(tmp_dir, f"test_image.{im_format}")
        with open(os.path.join(tmp_dir, f"test_image.{im_format}"), "wb") as file:
            file.write(image.encode(im_format=im_format))
        img = cv2.imread(tmp_img_path)
        assert img is not None


class TestSmartAlphaImage:
    def test_read_image(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        assert image.im_raw.shape[2] == 4
        assert image.im_alpha is not None
        assert image.has_transparency

    def test_get_rgb(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        compare_image = SmartAlphaImage(test_image_alpha_bytes)
        rgb_image = image.get(mode=RGB)
        assert (rgb_image == compare_image.get()).all()
        assert rgb_image.shape[2] == 3

    def test_get_bgr(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        compare_image = SmartAlphaImage(test_image_alpha_bytes)
        bgr_image = image.get(mode=BGR)
        assert (compare_image.get(mode=BGR) == bgr_image).all()
        assert bgr_image.shape[2] == 3

    def test_get_rgba(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        assert (image.im_rgb == image.get()).all()

    def test_get_bgra(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        RGBA_image = np.dstack((image.im_rgb[..., :3][:, :, ::-1], image.im_alpha))
        assert (image.get(mode=BGRA) == RGBA_image).all()

    def test_get_alpha(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        assert (image.im_raw[..., 3] == image.im_alpha).all()

    def test_set_image_bgra(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        image_two = SmartAlphaImage(test_image_alpha_bytes)
        bgra_image = image_two.get(mode=BGRA)
        image_two.set(bgra_image, BGRA)
        assert (image.get(mode=BGRA) == bgra_image).all()

    def test_set_image_alpha(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        fake_alpha = image.get()[:, :, 0]
        print(fake_alpha.shape)
        image.set(fake_alpha, ALPHA)
        assert (fake_alpha == image.im_alpha).all()

    def test_encode_png(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        check_encode(image, "png")

    def test_encode_png_dpi(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        image.dpi = (72, 72)
        with patch("removebg.image.encode_image") as mocked_encode:
            image.encode()
            mocked_encode.assert_called_with(ANY, icc_profile=None, dpi=(72, 72))

    def test_encode_jpeg_dpi(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        image.dpi = (72, 72)
        with patch("removebg.image.encode_image") as mocked_encode:
            image.encode(im_format="jpeg")
            mocked_encode.assert_called_with(ANY, "jpeg", dpi=(72, 72))

    def test_encode_jpg(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        check_encode(image, "jpg")

    def test_encode_jpg_alpha(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        check_encode(image, "jpg")

    def test_encode_jpg_color(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        check_encode(image, "jpg")

    def test_encode_jpeg(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        check_encode(image, "jpeg")

    def test_encode_jpeg_alpha(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        check_encode(image, "jpeg_alpha")

    def test_encode_jpeg_color(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        check_encode(image, "jpeg_color")

    def test_zip(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        with tempfile.TemporaryDirectory() as tmp_dir:
            with open(os.path.join(tmp_dir, "my.zip"), "wb") as file:
                file.write(image.zip())
            assert os.path.exists(os.path.join(tmp_dir, "my.zip"))

    def test_zip_dpi(self, test_image_alpha_bytes):
        image = SmartAlphaImage(test_image_alpha_bytes)
        image.dpi = (72, 72)
        with patch("removebg.image.encode_image") as mocked_encode:
            image.encode(im_format="jpeg")
            mocked_encode.assert_called_with(ANY, "jpeg", dpi=(72, 72))
