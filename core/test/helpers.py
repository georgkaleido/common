def pil_to_bytes(im):
    import io

    im_bytes = io.BytesIO()
    im.save(im_bytes, format="jpeg")
    return im_bytes.getvalue()


def im_absdiff(im1, im2, im_alpha=None, only_fg=False, only_bg=False):

    im1 = im1.convert("L")
    im2 = im2.convert("L")

    import numpy as np

    im1 = np.array(im1)
    im2 = np.array(im2)

    if im_alpha is None:
        absdiff = np.abs(im1.mean() - im2.mean())
    else:
        im_alpha = np.array(im_alpha)

        if len(im_alpha.shape) == 3:
            im_alpha = im_alpha[..., -1]

        if only_fg:
            mask = im_alpha == 255
        elif only_bg:
            mask = im_alpha == 0
        else:
            mask = (im_alpha == 0) | (im_alpha == 255)

        absdiff = np.abs(im1[mask].mean() - im2[mask].mean())

    return absdiff


def scaled_im(path, mp):
    import math

    from PIL import Image

    im = Image.open(path)

    scale = math.sqrt(mp * 1000000.0 / (im.width * im.height))
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.BOX)

    return pil_to_bytes(im)


def compute_scale_pos(im):
    import cv2
    import numpy as np

    im = np.array(im)

    x, y, w, h = cv2.boundingRect(im)

    # check if scale was applied correctly
    return max(1.0 * w / im.shape[1], 1.0 * h / im.shape[0]), (x + w // 2.0, y + h // 2.0)
