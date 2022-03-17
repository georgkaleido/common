import dataclasses
import io
import os
import zipfile
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
import pytest
import requests
from PIL import Image
from tests.conftest import core_server_tester  # noqa: F401


def pytest_addoption(parser):
    parser.addini("url", "url of the endpoint")
    parser.addini("port", "port of the endpoint")
    parser.addini("api_key", "api key to use")


@pytest.fixture(scope="module")
def req_fn(request):
    def _fn(path, args):

        if isinstance(path, bytes):
            im_bytes = path
        else:
            if not os.path.exists(path):
                raise Exception("data must be bytes or valid path!")

            with open(path, "rb") as f:
                im_bytes = f.read()

        im_in = Image.open(io.BytesIO(im_bytes))

        files = {"image_file": im_bytes}

        if "bg_image_file" in args:
            files["bg_image_file"] = args["bg_image_file"]
            del args["bg_image_file"]

        response = requests.post(
            "https://{}:{}/v1.0/removebg".format(request.config.getini("url"), request.config.getini("port")),
            files=files,
            data=args,
            headers={"X-Api-Key": request.config.getini("api_key")},
            verify=False,
        )

        im = None
        if response.status_code == 200:
            if response.headers.get("Content-Type") == "application/zip":
                im_bytes = np.fromstring(response.content, np.uint8)

                with zipfile.ZipFile(io.BytesIO(im_bytes)) as f:
                    im_color_bytes = f.open("color.jpg")
                    im_alpha_bytes = f.open("alpha.png")

                im_color = Image.open(im_color_bytes)
                im_alpha = Image.open(im_alpha_bytes)

                im = (im_color, im_alpha)

            else:
                im_bytes = np.fromstring(response.content, np.uint8)
                im = Image.open(io.BytesIO(im_bytes))

        return im, im_in, response.headers, response.status_code

    return _fn


@pytest.fixture(scope="session")
def test_image_alpha_bytes() -> bytes:
    with open("./data/lena_alpha.png", "rb") as image_file:
        yield image_file.read()


RUN_CORE_TESTER = os.environ.get("RUN_TESTER")


@dataclass
class RemovebgMessage:
    version: str = "1.0"
    command: str = "removebg"
    megapixels: float = 10
    channels: str = "rgba"
    format: str = "png"
    bg_color: List[int] = None
    type: str = "auto"
    crop: bool = False
    crop_margin: Dict[str, Any] = None
    roi: List[int] = None
    semitransparency: bool = True
    semitransparency_experimental: bool = False
    shadow: bool = False
    bg_image: Any = None
    data: Any = None
    position: Dict[str, int] = None
    scale: Optional[int] = None

    def serialize(self):
        """Serialize to dict with byte encoded keys."""

        if self.crop_margin is None:
            self.crop_margin = {
                "top": 0,
                "top_relative": False,
                "right": 0,
                "right_relative": False,
                "bottom": 0,
                "bottom_relative": False,
                "left": 0,
                "left_relative": False,
            }
        if self.bg_color is None:
            self.bg_color = [255, 255, 255, 0]
        return {str.encode(key): value for key, value in dataclasses.asdict(self).items()}
