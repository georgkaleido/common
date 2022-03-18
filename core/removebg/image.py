import io
import math
import zipfile
from typing import Any, Optional, Tuple, Union

import numpy
import numpy as np
import PIL
from kaleido.alpha.imops import bbox, crop_subject, fill_holes, position_subject, scale_subject, underlay_background
from kaleido.image import ALPHA, BGR, BGRA, RGB, RGBA, CouldNotReadImage, encode_image
from kaleido.image.exif import handle_exif_rotation
from kaleido.image.icc import mode2rgb, rgb2mode

# from kaleido.image.imread import read_image
from PIL import Image as ImagePIL

TRIMAP_OPTI = "TRIMAP_OPTI"


def read_image_custom(
    data: Union[str, bytes], megapixel_limit: float, megapixel_limit_trimap: float
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, bytes, str, Tuple[int, int], Tuple[int, int], float, float, Any]:
    if isinstance(data, str):
        im_raw = ImagePIL.open(data)
    else:
        im_bytes = np.frombuffer(data, np.uint8)
        im_raw = ImagePIL.open(io.BytesIO(im_bytes))

    # copy image without overwriting. this will throw an exception if image is truncated
    im_raw.copy()

    icc = im_raw.info.get("icc_profile")
    dpi = im_raw.info.get("dpi")
    mode = im_raw.mode

    im_raw, exif_rot = handle_exif_rotation(im_raw)

    # scale
    width_prescale = im_raw.width
    height_prescale = im_raw.height

    def downscale(image, mp_limit, interpolation_method=None, reducing_gap=None):
        scale_factor = min(1.0, math.sqrt(mp_limit * 1000000.0 / (image.width * image.height))) if mp_limit else 1.0
        if scale_factor < 1.0:
            if interpolation_method is None:
                interpolation_method = ImagePIL.BICUBIC if scale_factor > 0.5 and mp_limit < 1.0 else ImagePIL.BOX
            ds_width, ds_height = (int(image.width * scale_factor), int(image.height * scale_factor))
            image = image.resize((ds_width, ds_height), resample=interpolation_method, reducing_gap=reducing_gap)
        return image, scale_factor

    im, scale = downscale(im_raw, megapixel_limit, interpolation_method=None, reducing_gap=3.0)

    # to rgb
    im_rgb = mode2rgb(im, icc)

    # to numpy
    im_np = np.ascontiguousarray(np.array(im))
    im_rgb_np = np.ascontiguousarray(np.array(im_rgb))

    # Same process for image optimized for trimap
    has_im_for_trimap = megapixel_limit_trimap is not None
    if has_im_for_trimap:
        im_for_trimap, scale_trimap = downscale(
            im_raw, megapixel_limit_trimap, interpolation_method=ImagePIL.BOX, reducing_gap=1.0
        )
        im_for_trimap = mode2rgb(im_for_trimap, icc)
        im_for_trimap_np = np.ascontiguousarray(np.array(im_for_trimap))
    else:
        im_for_trimap_np = None
        scale_trimap = None

    return im_rgb_np, im_np, im_for_trimap_np, icc, mode, dpi, (width_prescale, height_prescale), scale, scale_trimap, exif_rot


class SmartAlphaImage:
    def __init__(self, im_bytes: bytes, megapixel_limit: Optional[float] = None, megapixel_limit_trimap: Optional[float] = None):
        try:
            im, im_raw, im_for_trimap, icc, mode, dpi, size_prescale, scale, scale_trimap, exif_rot = read_image_custom(
                im_bytes, megapixel_limit=megapixel_limit, megapixel_limit_trimap=megapixel_limit_trimap
            )
        except OSError as e:
            raise CouldNotReadImage("corrupted image (truncated)") from e
        except Exception as e:
            raise CouldNotReadImage("unknown error occurred") from e

        # im is rgb and im_raw is in the original colorspace (mode)
        self.im_raw = im_raw

        if im.shape[2] == 3:
            self.im_rgb = im
            self.im_for_trimap = im_for_trimap
            self.im_alpha = None
        else:
            # if there is an alpha channel, interpolate with white

            def interpolate_with_white(image_rgb, image_alpha):
                alpha = image_alpha / 255.0
                alpha = np.expand_dims(alpha, 2)
                alpha = np.repeat(alpha, 3, 2)
                return (image_rgb * alpha + 255 * (1.0 - alpha)).astype(np.uint8)

            self.im_alpha = im[:, :, 3]
            self.im_rgb = interpolate_with_white(im[:, :, :3], self.im_alpha)
            if im_for_trimap is not None:
                self.im_for_trimap = interpolate_with_white(im_for_trimap[:, :, :3], im_for_trimap[:, :, 3])
            else:
                self.im_for_trimap = None

        self.icc = icc
        self.mode_original = mode
        self.dpi = dpi
        self.exif_rot = exif_rot

        self.width = im.shape[1]
        self.height = im.shape[0]

        self.width_original = self.width
        self.height_original = self.height

        self.width_pre_mplimit = size_prescale[0]
        self.height_pre_mplimit = size_prescale[1]
        self.scale_pre_mplimit = scale
        self.scale_trimap = scale_trimap

        # this mask is used later when cmyk colors are restored
        self.pre_background_mask = None
        self.foreground_bounding_box = None

    def _validate_crop(self, crop_roi: Tuple[int, int, int, int]) -> None:
        assert len(crop_roi) == 4, f"crop format is invalid! {crop_roi}"
        x, y, w, h = crop_roi
        assert h + y <= self.height, f"crop invalid, {h + x} out of height {self.height} bound"
        assert w + x <= self.width, f"crop invalid, {w + x} out of width {self.width} bound"
        assert w != 0 and h != 0 and x >= 0 and y >= 0, f"crop invalid zero value in width={w}, height={h}, x={x} y={y}"

    def get(
        self,
        mode: str = RGB,
        crop: Tuple[int, int, int, int] = tuple(),
        ascontiguousarray: bool = True,
    ) -> Optional[np.ndarray]:
        mode = mode.upper()
        assert mode in {RGB, BGR, BGRA, ALPHA, TRIMAP_OPTI}, f"Mode '{mode}' is not supported"
        im = None
        if mode == RGB:
            im = self.im_rgb
        elif mode == TRIMAP_OPTI:
            assert self.im_for_trimap is not None, "im_for_trimap was not set"
            im = self.im_for_trimap
        elif mode == BGR:
            im = self.im_rgb[:, :, ::-1]
        elif mode == BGRA:
            assert self.im_alpha is not None, "alpha was not set yet!"
            im = np.dstack((self.im_rgb[:, :, ::-1], self.im_alpha))
        elif mode == ALPHA:
            assert self.im_alpha is not None, "alpha was not set yet!"
            im = self.im_alpha

        if crop:
            im = self._crop(im, crop)

        if ascontiguousarray:
            return np.ascontiguousarray(im)
        return im

    def _crop(self, image: np.ndarray, crop_roi: Tuple[int, int, int, int]) -> np.ndarray:
        self._validate_crop(crop_roi)
        x, y, w, h = crop_roi
        return image[y : y + h, x : x + w]

    def set(
        self,
        im: np.ndarray,
        mode: str = BGRA,
        limit_alpha: bool = True,
        crop: Optional[Tuple[int, int, int, int]] = None,
    ) -> None:
        mode = mode.upper()
        assert mode in {BGRA, ALPHA}, f"mode {mode} not available"

        if crop:
            im = self._uncrop(im, crop[0], crop[1])

        assert (
            im.shape[0] == self.im_rgb.shape[0] or im.shape[1] == self.im_rgb.shape[1]
        ), f"shape {im.shape} does not match original shape {self.im_rgb.shape}!"

        def _limit_alpha(im_alpha):
            # new alpha values can not be larger than old one (enabled by default)
            if self.im_alpha is None or not limit_alpha:
                return im_alpha
            mask = im_alpha > self.im_alpha
            im_alpha[mask] = self.im_alpha[mask]
            return im_alpha

        if mode == BGRA:
            assert im.shape[2] == 4, f"bgra images should have 4 dimensions. only has {im.shape[2]}"
            self.im_rgb = im[..., :3][..., ::-1]
            self.im_alpha = _limit_alpha(im[..., 3])
        elif mode == ALPHA:
            assert len(im.shape) == 2, f"alpha image has {len(im.shape)} dimensions but should only have 2"
            self.im_alpha = _limit_alpha(im)

    def _uncrop(self, im: np.ndarray, x: int, y: int) -> np.ndarray:
        self._validate_crop((x, y, im.shape[1], im.shape[0]))
        return np.pad(
            im,
            [(y, self.height - (im.shape[0] + y)), (x, self.width - (im.shape[1] + x))]
            + ([] if len(im.shape) == 2 else [(0, 0)]),
            "constant",
        )

    @property
    def signal_beacon(self) -> bool:
        return self.im_rgb[0, 0, 0] >= 254 and self.im_rgb[0, 0, 1] == 0 and self.im_rgb[0, 0, 2] == 0

    def fill_holes(
        self,
        fill_value: Any,
        mode: str,
        average: bool,
        im_rgb_precolorcorr: numpy.ndarray,
    ) -> None:
        assert self.im_alpha is not None, "alpha was not set yet!"

        im = np.dstack((im_rgb_precolorcorr, self.im_alpha))
        im = fill_holes(im, fill_value, mode=mode, average=average)

        mask = self.im_alpha == im[:, :, 3]
        im[:, :, :3][mask] = self.im_rgb[mask]

        self.im_rgb = im[..., :3]
        self.im_alpha = im[..., 3]

    def compute_foreground_bounding_box(self) -> None:
        self.foreground_bounding_box = bbox(self.im_alpha)

    def postproc_fn(self, name: str, **kwargs: Any) -> None:
        assert self.im_alpha is not None, "alpha was not set yet!"

        if name == "crop_subject":
            fn = crop_subject
            kwargs["precomputed_bbox"] = self.foreground_bounding_box
        elif name == "scale_subject":
            fn = scale_subject
        elif name == "position_subject":
            fn = position_subject
        else:
            raise ValueError(f"postproc function {name} not supported!")

        self.im_rgb = fn(self.im_rgb, self.im_alpha, **kwargs)
        self.im_raw = fn(self.im_raw, self.im_alpha, **kwargs)
        self.im_alpha = fn(self.im_alpha, self.im_alpha, **kwargs)

        self.width = self.im_rgb.shape[1]
        self.height = self.im_rgb.shape[0]

    def underlay_background(self, background: Union[list, "SmartAlphaImage"]) -> None:
        assert self.im_alpha is not None, "alpha was not set yet!"

        if isinstance(background, list):
            assert len(background) == 4, f"background list must have exactly 4 entries! has {len(background)}"
            # expected mode: RGB
            # completely transparent - return
            if background[3] == 0:
                return None
            background_ = background
        elif isinstance(background, SmartAlphaImage):
            if background.im_alpha is None:
                background_ = background.im_rgb
            else:
                background_ = np.dstack((background.im_rgb, background.im_alpha))
        else:
            background_ = background

        im = np.dstack((self.im_rgb, self.im_alpha))
        im = underlay_background(im, background_)

        # take a snapshot
        self.pre_background_mask = self.im_alpha == 255

        self.im_rgb = im[..., :3]
        self.im_alpha = im[..., 3]

    @property
    def has_transparency(self):
        return self.im_alpha is not None and (self.im_alpha < 255).any()

    def _restore_cmyk_colors(self, im: Union[np.ndarray, ImagePIL.Image]) -> Union[np.ndarray, ImagePIL.Image]:
        # only supported if icc profile is set and mode is cmyk
        if self.icc is None or self.mode_original != "CMYK":
            return im

        im_np = np.array(im)
        mask = (self.im_alpha == 0) | (self.im_alpha == 255)

        # backgrounds make this step complicated... dont restore areas
        if self.pre_background_mask is not None:
            mask = mask & self.pre_background_mask

        im_np[mask] = self.im_raw[mask]
        return ImagePIL.fromarray(im_np, mode=self.mode_original)

    def encode(self, im_format: str = "png", **encoding_kwargs: Any) -> bytes:
        """Encodes an image to the specified image format.

        Args:
            im_format: Format to encode image to e.g. png, jpeg, jpeg_alpha, jpeg_color
            png_alpha.
            **encoding_kwargs: Additional PIL encoding args.

        Returns:
            Encoded image in bytes.
        """
        if self.dpi:
            encoding_kwargs["dpi"] = self.dpi

        im_format = im_format.lower()
        # PIL only support jpeg not jpg as format to encode
        if "jpg" in im_format:
            im_format = im_format.replace("jpg", "jpeg")
        assert im_format in {
            "png",
            "jpeg",
            "jpeg_alpha",
            "jpeg_color",
            "png_alpha",
        }, f"Image format: '{im_format}' not supported to encode."

        if im_format == "jpeg":
            # create pil image
            im_rgb = PIL.Image.fromarray(self.im_rgb)
            # convert back to mode
            im, icc_valid = rgb2mode(im_rgb, self.icc, self.mode_original)

            # restore original colors
            im = self._restore_cmyk_colors(im)

            # if there is an icc profile and its not the alpha mat
            if self.icc and icc_valid:
                encoding_kwargs["icc_profile"] = self.icc

            return encode_image(im, im_format, **encoding_kwargs)
        elif im_format == "jpeg_alpha":
            im_alpha = PIL.Image.fromarray(self.im_alpha)
            return encode_image(im_alpha, im_format="jpeg", **encoding_kwargs)
        elif im_format == "jpeg_color":
            im_color = PIL.Image.fromarray(self.im_rgb)
            return encode_image(im_color, im_format="jpeg", **encoding_kwargs)
        elif im_format == "png_alpha":
            im_alpha = PIL.Image.fromarray(self.im_alpha)
            return encode_image(im_alpha, **encoding_kwargs)

        # delete colors that are completely transparent to make encoded image smaller
        im = np.dstack((self.im_rgb, self.im_alpha))
        im[:, :, :3][im[:, :, 3] == 0] = 0
        # create pil image
        im_rgba = PIL.Image.fromarray(im)
        return encode_image(
            im_rgba,
            icc_profile=self.icc if self.mode_original.upper() in {RGB, RGBA} else None,
            **encoding_kwargs,
        )

    def zip(self) -> bytes:
        """Returns images alpha.png and color.jpg zipped."""
        encoding_kwargs = {}
        if self.dpi:
            encoding_kwargs["dpi"] = self.dpi
        # to pil
        im_rgb = PIL.Image.fromarray(self.im_rgb)
        im_alpha = PIL.Image.fromarray(self.im_alpha)
        # convert back to mode
        im, icc_valid = rgb2mode(im_rgb, self.icc, self.mode_original)
        # restore the original colors
        im = self._restore_cmyk_colors(im)

        # encode color
        bytes_color = encode_image(im, "jpeg", icc_profile=self.icc if icc_valid else None, **encoding_kwargs)
        # encode alpha
        bytes_alpha = encode_image(im_alpha, **encoding_kwargs)

        # zip it
        with io.BytesIO() as mem_zip:
            with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_STORED) as zf:
                zf.writestr("color.jpg", bytes_color)
                zf.writestr("alpha.png", bytes_alpha)
            return mem_zip.getvalue()
