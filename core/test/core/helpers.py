import io
import zipfile

from PIL import Image
from tests.utils import convert_to_image


def unzip(im_bytes: bytes):
    with zipfile.ZipFile(io.BytesIO(im_bytes)) as f:
        im_color_bytes = f.open("color.jpg")
        im_alpha_bytes = f.open("alpha.png")

    im_color = Image.open(im_color_bytes)
    im_alpha = Image.open(im_alpha_bytes)
    return im_color, im_alpha


def process_image(core_server_tester, msg, return_result_dict=False):
    result = core_server_tester.request(msg.serialize())
    im_color, im_alpha, im = None, None, None
    if msg.format == "zip":
        im_color, im_alpha = unzip(result[b"data"])
    else:
        im = convert_to_image(result[b"data"])
    output_dict = {"im": im, "im_color": im_color, "im_alpha": im_alpha}
    if return_result_dict:
        output_dict["result"] = result
    return output_dict
