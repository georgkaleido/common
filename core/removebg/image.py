
import io
import zipfile
import numpy as np

from PIL import Image as ImagePIL

from kaleido.image.imread import read_image
from kaleido.image.icc import rgb2mode
from kaleido.alpha.imops import fill_holes, crop_subject, scale_subject, position_subject, underlay_background


class CouldNotReadImage(Exception):
    """Raised when image could not be read fails"""
    pass


class SmartAlphaImage(object):
    def __init__(self, im_bytes, megapixel_limit=None):
        try:
            im, im_raw, icc, mode, dpi, size_prescale, scale, exif_rot = read_image(im_bytes, megapixel_limit=megapixel_limit)
        except Exception as e:
            raise CouldNotReadImage(str(e)) from None

        # im is rgb and im_raw is in the original colorspace (mode)
        self.im_raw = im_raw

        if im.shape[2] == 3:
            self.im_rgb = im
            self.im_alpha = None
        else:
            # if there is an alpha channel, interpolate with white
            self.im_alpha = im[:, :, 3]

            alpha = self.im_alpha / 255.0
            alpha = np.expand_dims(alpha, 2)
            alpha = np.repeat(alpha, 3, 2)

            self.im_rgb = (im[:, :, :3] * alpha + 255 * (1.0 - alpha)).astype(np.uint8)

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

        # this mask is used later when cmyk colors are restored
        self.pre_background_mask = None

    def _validate_crop(self, crop):
        if len(crop) != 4:
            raise Exception('crop format is invalid! {}'.format(crop))

        x, y, w, h = crop
        if h + y > self.height or w + x > self.width or w == 0 or h == 0 or x < 0 or y < 0:
            raise Exception('crop is invalid! width={}, height={}, crop x={}, y={}, width={}, height={}'.format(self.width, self.height, x, y, w, h))

    def _validate_alpha(self):
        if self.im_alpha is None:
            raise Exception('alpha was not set yet!')

    def get(self, mode='rgb', crop=None):

        if mode == 'rgb':
            im = self.im_rgb
        elif mode == 'bgr':
            im = self.im_rgb[:, :, ::-1]
        elif mode == 'bgra':
            if self.im_alpha is None:
                raise Exception('alpha channel is not available!')
            im = np.dstack((self.im_rgb[:, :, ::-1], self.im_alpha))
        elif mode == 'alpha':
            if self.im_alpha is None:
                raise Exception('alpha channel is not available!')
            im = self.im_alpha
        else:
            raise Exception('mode {} not available'.format(mode))

        # crop

        if crop:
            self._validate_crop(crop)

            x, y, w, h = crop
            im = im[y:y+h, x:x+w]

        return np.ascontiguousarray(im)

    def set(self, im, mode='bgra', limit_alpha=True, crop=None):

        if crop:
            im = self.uncrop(im, crop[0], crop[1])

        if im.shape[0] != self.im_rgb.shape[0] or im.shape[1] != self.im_rgb.shape[1]:
            raise Exception('shape {} does not match original shape {}!'.format(im.shape, self.im_rgb.shape))

        def _limit_alpha(im_alpha):
            # new alpha values can not be larger than old one (enabled by default)

            if self.im_alpha is None or not limit_alpha:
                return im_alpha

            mask = im_alpha > self.im_alpha
            im_alpha[mask] = self.im_alpha[mask]

            return im_alpha

        if mode == 'bgra':
            if im.shape[2] != 4:
                raise Exception('bgra images should have 4 dimensions. only has {}'.format(im.shape[2]))

            self.im_rgb = im[..., :3][..., ::-1]
            self.im_alpha = _limit_alpha(im[..., 3])
        elif mode == 'alpha':
            if len(im.shape) != 2:
                raise Exception('alpha image has {} dimensions but should only have 2'.format(len(im.shape)))

            self.im_alpha = _limit_alpha(im)
        else:
            raise Exception('mode {} not available'.format(mode))

    def uncrop(self, im, x, y):
        self._validate_crop([x, y, im.shape[1], im.shape[0]])

        return np.pad(im, [(y, self.height - (im.shape[0] + y)), (x, self.width - (im.shape[1] + x))] + ([] if len(im.shape) == 2 else [(0, 0)]), 'constant')

    def signal_beacon(self):
        return self.im_rgb[0, 0, 0] >= 254 and self.im_rgb[0, 0, 1] == 0 and self.im_rgb[0, 0, 2] == 0

    def fill_holes(self, fill_value, mode, average, im_rgb_precolorcorr):
        self._validate_alpha()

        im = np.dstack((im_rgb_precolorcorr, self.im_alpha))
        im = fill_holes(im, fill_value, mode=mode, average=average)

        mask = self.im_alpha == im[:, :, 3]
        im[:, :, :3][mask] = self.im_rgb[mask]

        self.im_rgb = im[..., :3]
        self.im_alpha = im[..., 3]

    def postproc_fn(self, name, **kwargs):
        self._validate_alpha()

        if name == 'crop_subject':
            fn = crop_subject
        elif name == 'scale_subject':
            fn = scale_subject
        elif name == 'position_subject':
            fn = position_subject
        else:
            raise Exception('postproc function {} not supported!'.format(name))

        self.im_rgb = fn(self.im_rgb, self.im_alpha, **kwargs)
        self.im_raw = fn(self.im_raw, self.im_alpha, **kwargs)
        self.im_alpha = fn(self.im_alpha, self.im_alpha, **kwargs)

        self.width = self.im_rgb.shape[1]
        self.height = self.im_rgb.shape[0]

    def underlay_background(self, background):
        self._validate_alpha()

        if isinstance(background, list):
            if len(background) != 4:
                raise Exception('background list must have exactly 4 entries!'.format(len(background)))

            # expected mode: RGB

            # completely transparent - return
            if background[3] == 0:
                return

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

    def has_transparency(self):
        return self.im_alpha is not None and (self.im_alpha < 255).any()

    def encode(self, format):

        self._validate_alpha()

        kwargs_jpg = {'format': 'jpeg', 'quality': 90}
        kwargs_png = {'format': 'png', 'compress_level': 3}

        if self.dpi:
            kwargs_jpg['dpi'] = self.dpi
            kwargs_png['dpi'] = self.dpi

        def _restore_cmyk_colors(im):
            # only supported if icc profile is set and mode is cmyk
            if self.icc is None or self.mode_original != 'CMYK':
                return im

            im_np = np.array(im)
            mask = (self.im_alpha == 0) | (self.im_alpha == 255)

            # backgrounds make this step complicated... dont restore areas
            if self.pre_background_mask is not None:
                mask = mask & self.pre_background_mask

            im_np[mask] = self.im_raw[mask]
            return ImagePIL.fromarray(im_np, mode=self.mode_original)

        if format == 'zip':
            # to pil

            im_rgb = ImagePIL.fromarray(self.im_rgb)
            im_alpha = ImagePIL.fromarray(self.im_alpha)

            # convert back to mode

            im, icc_valid = rgb2mode(im_rgb, self.icc, self.mode_original)

            # restore the original colors

            im = _restore_cmyk_colors(im)

            # encode color

            with io.BytesIO() as o:
                im.save(o, icc_profile=self.icc if icc_valid else None, **kwargs_jpg)
                bytes_color = o.getvalue()

            # encode alpha

            with io.BytesIO() as o:
                im_alpha.save(o, **kwargs_png)
                bytes_alpha = o.getvalue()

            # zip it

            with io.BytesIO() as mem_zip:
                with zipfile.ZipFile(mem_zip, mode='w', compression=zipfile.ZIP_STORED) as zf:
                    zf.writestr('color.jpg', bytes_color)
                    zf.writestr('alpha.png', bytes_alpha)

                res = mem_zip.getvalue()

        elif format == 'png':

            # delete colors that are completely transparent to make encoded image smaller

            im = np.dstack((self.im_rgb, self.im_alpha))
            im[:, :, :3][im[:, :, 3] == 0] = 0

            # create pil image

            im_rgba = ImagePIL.fromarray(im)

            with io.BytesIO() as o:
                im_rgba.save(o, icc_profile=self.icc if self.mode_original in ['RGB', 'RGBA'] else None, **kwargs_png)
                res = o.getvalue()

        elif format == 'jpg':

            # create pil image

            im_rgb = ImagePIL.fromarray(self.im_rgb)

            # convert back to mode

            im, icc_valid = rgb2mode(im_rgb, self.icc, self.mode_original)

            # restore original colors

            im = _restore_cmyk_colors(im)

            # if there is an icc profile and its not the alpha mat

            if self.icc and icc_valid:
                kwargs_jpg['icc_profile'] = self.icc

            with io.BytesIO() as o:
                im.save(o, **kwargs_jpg)
                res = o.getvalue()

        elif format == 'jpg_alpha':

            # only alpha

            im_alpha = ImagePIL.fromarray(self.im_alpha)

            with io.BytesIO() as o:
                im_alpha.save(o, **kwargs_jpg)
                res = o.getvalue()

        elif format == 'png_alpha':

            # only alpha

            im_alpha = ImagePIL.fromarray(self.im_alpha)

            with io.BytesIO() as o:
                im_alpha.save(o, **kwargs_png)
                res = o.getvalue()

        elif format == 'jpg_color':

            # only alpha

            im_color = ImagePIL.fromarray(self.im_rgb)

            with io.BytesIO() as o:
                im_color.save(o, **kwargs_png)
                res = o.getvalue()

        else:
            raise Exception('method {} not supported!'.format(format))

        return res
