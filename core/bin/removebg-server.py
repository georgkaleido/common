#!/usr/bin/env python
import math
import multiprocessing
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

import numpy as np
from kaleido.server import ImageServer, Worker, read_rabbitmq_env_variables
from kaleido.server.messages import ERROR_STATUS, ImageProcessingData, ImageResult
from kaleido.tensor.utils import to_numpy, to_tensor
from removebg.image import CouldNotReadImage, SmartAlphaImage
from removebg.removebg import UnknownForegroundException

UNKNOWN_ERROR = "unknown_error"
UNKNOWN_FOREGROUND = "unknown_foreground"


@dataclass
class RemovebgResult(ImageResult):
    maxwidth: int = 0
    maxheight: int = 0
    width_hd: int = 0
    height_hd: int = 0
    width_medium: int = 0
    height_medium: int = 0
    width_uncropped: int = 0
    height_uncropped: int = 0
    input_foreground_left: int = 0
    input_foreground_top: int = 0
    input_foreground_width: int = 0
    input_foreground_height: int = 0
    type: str = "auto"


class RemovebgWorker(Worker):
    def _preprocess(self, processing_data: ImageProcessingData, message: Dict[bytes, Any]) -> None:
        correlation_extra = {"correlation_id": processing_data.correlation_id}

        result: RemovebgResult = RemovebgResult()
        processing_data.result = result

        # continue with removebg
        im_bytes = message[b"data"]
        megapixels = message[b"megapixels"]
        only_alpha = message.get(b"channels", b"rgba") == b"alpha"
        api_type = message.get(b"type", b"auto")
        file_format = message.get(b"format", b"auto").decode()
        bg_color = message.get(b"bg_color", [255, 255, 255, 0])
        im_bytes_bg = message.get(b"bg_image", None)
        scale_param = message.get(b"scale", None)
        position_param = message.get(b"position", None)
        crop = message.get(b"crop", False)
        crop_margin = message.get(b"crop_margin", None)
        roi = message.get(b"roi", None)
        shadow = message.get(b"shadow", False)
        semitransparency = message.get(b"semitransparency", True)
        image_bg = None

        times = []
        t = time.time()

        try:
            image = SmartAlphaImage(im_bytes, megapixel_limit=megapixels)

            if im_bytes_bg is not None:
                image_bg = SmartAlphaImage(im_bytes_bg, megapixel_limit=megapixels)
        except CouldNotReadImage:
            self.logger.exception("error: could not read image", extra=correlation_extra)
            result.status = ERROR_STATUS
            result.description = "failed_to_read_image"
            # error happened, we exit
            return None

        if image.signal_beacon:
            self.logger.info("SIGNAL BEACON DETECTED", extra=correlation_extra)

        times.append(time.time() - t)
        has_image_icc: str = "yes" if image.icc else "no"
        has_alpha: str = "yes" if image.im_alpha is not None is not None else "no"
        has_exif_rot: str = "none" if image.exif_rot is None else image.exif_rot
        self.logger.info(
            f"[{processing_data.correlation_id}] decoding ({times[-1]:.2f}s) | megapixels: {megapixels},"
            f" mode: {image.mode_original}, dpi: {image.dpi}, icc: {has_image_icc},"
            f" has alpha: {has_alpha}, exif: {has_exif_rot}",
        )
        t = time.time()

        # crop to roi
        crop_roi = None

        if roi:
            x0 = min(roi[0], roi[2])
            x1 = max(roi[0], roi[2])
            y0 = min(roi[1], roi[3])
            y1 = max(roi[1], roi[3])

            w = int((x1 - x0 + 1) * image.scale_pre_mplimit)
            h = int((y1 - y0 + 1) * image.scale_pre_mplimit)
            x0 = int(x0 * image.scale_pre_mplimit)
            y0 = int(y0 * image.scale_pre_mplimit)

            crop_roi = (x0, y0, w, h)

        im_cv = image.get("bgr", crop=crop_roi)

        # check min size
        s = 224.0 / max(im_cv.shape[0], im_cv.shape[1])
        if s * im_cv.shape[0] < 5 or s * im_cv.shape[1] < 5:
            self.logger.exception(
                "error: could not identify foreground",
                extra={
                    "detail": f"image size too small: {im_cv.shape}",
                    **correlation_extra,
                },
            )
            result.status = ERROR_STATUS
            result.description = UNKNOWN_FOREGROUND
            return None

        times.append(time.time() - t)
        self.logger.info(
            f"[{processing_data.correlation_id}] preproc ({times[-1]:.2f}s) | "
            f"{image.width}x{image.height} -> {im_cv.shape[1]}x{im_cv.shape[0]} (crop: {crop})",
        )

        # pass all data which is needed for postprocessing
        processing_data.data = {
            "times": times,
            "api": api_type.decode(),
            "image": image,
            "im_cv": im_cv,
            "image_bg": image_bg,
            "shadow": shadow,
            "only_alpha": only_alpha,
            "file_format": file_format,
            "bg_color": bg_color,
            "scale_param": scale_param,
            "position_param": position_param,
            "crop": crop,
            "crop_margin": crop_margin,
            "crop_roi": crop_roi,
            "semitransparency": semitransparency,
        }

    def _post_process(self, processing_data: ImageProcessingData) -> None:

        result = processing_data.result
        data = processing_data.data

        # load data from preprocessing
        im_res = data["data"]
        times = data["times"]
        image = data["image"]
        semitransparency = data["semitransparency"]
        crop_margin = data["crop_margin"]
        scale_param = data["scale_param"]
        position_param = data["position_param"]
        bg_color = data["bg_color"]
        image_bg = data["image_bg"]
        shadow = data["shadow"]
        only_alpha = data["only_alpha"]
        file_format = data["file_format"]

        times.append(data["time"])
        self.logger.info(
            f"[{processing_data.correlation_id}] processing " f"({times[-1]:.2f}s) | class: {data['api']}",
        )
        t = time.time()

        # uncrop and set result
        im_rgb_precolorcorr = image.get("rgb")
        image.set(im_res, "bgra", limit_alpha=True, crop=data["crop_roi"])

        # car windows
        if data["api"] == "car":
            image.fill_holes(
                200 if semitransparency else 255,
                mode="car",
                average=semitransparency,
                im_rgb_precolorcorr=im_rgb_precolorcorr,
            )
        elif data["api"] == "car_interior":
            image.fill_holes(
                200 if semitransparency else 0,
                mode="all",
                average=True,
                im_rgb_precolorcorr=im_rgb_precolorcorr,
            )

        # Compute foreground coordinates
        image.compute_foreground_bounding_box()

        # crop to subject
        if data["crop"]:
            kwargs = {}
            if crop_margin:
                kwargs = {
                    "margins": [
                        crop_margin[b"top"],
                        crop_margin[b"right"],
                        crop_margin[b"bottom"],
                        crop_margin[b"left"],
                    ],
                    "absolutes": [
                        not crop_margin[b"top_relative"],
                        not crop_margin[b"right_relative"],
                        not crop_margin[b"bottom_relative"],
                        not crop_margin[b"left_relative"],
                    ],
                    "clamp": 500,
                }
            image.postproc_fn("crop_subject", **kwargs)

        # scale
        if scale_param:
            image.postproc_fn("scale_subject", scale_new=scale_param / 100.0)

        # position
        if position_param:
            image.postproc_fn(
                "position_subject",
                dx=position_param[b"x"] / 100.0,
                dy=position_param[b"y"] / 100.0,
            )

        # fill bg color or background
        if file_format == "jpg":
            bg_color[3] = 255

        if image_bg is not None:
            image.underlay_background(image_bg)
        elif bg_color[3] > 0:
            image.underlay_background(bg_color)

        times.append(time.time() - t)
        has_shadow: str = "yes" if shadow else "no"
        self.logger.info(
            f"[{processing_data.correlation_id}] postproc "
            f"({times[-1]:.2f}s) | bg_color: {bg_color}, shadow: {has_shadow}",
        )
        t = time.time()

        # encoding
        if file_format == "zip":
            res = image.zip()
            result.format = "zip"
        else:
            if only_alpha:
                if file_format == "jpg" or file_format == "auto":
                    res = image.encode("jpg_alpha")
                    result.format = "jpg"
                else:
                    res = image.encode("png_alpha")
                    result.format = "png"
            else:
                if file_format == "png" or (file_format == "auto" and image.has_transparency):
                    res = image.encode("png")
                    result.format = "png"
                else:
                    res = image.encode("jpg")
                    result.format = "jpg"

        result.type = data["api"]
        result.data = res
        result.width = image.width
        result.height = image.height
        result.width_uncropped = image.width_original
        result.height_uncropped = image.height_original
        bbox = image.foreground_bounding_box
        if bbox:
            scaling_ratio = image.width_original / image.width_pre_mplimit
            result.input_foreground_top = int(scaling_ratio * bbox[0])
            result.input_foreground_left = int(scaling_ratio * bbox[2])
            result.input_foreground_height = int(scaling_ratio * (bbox[1] - bbox[0]))
            result.input_foreground_width = int(scaling_ratio * (bbox[3] - bbox[2]))
        else:
            result.input_foreground_top = 0
            result.input_foreground_left = 0
            result.input_foreground_height = int(image.height_pre_mplimit)
            result.input_foreground_width = int(image.width_pre_mplimit)

        scale = math.sqrt(1500000.0 / (image.width_pre_mplimit * image.height_pre_mplimit))
        result.width_medium = min(int(scale * image.width_pre_mplimit), image.width_pre_mplimit)
        result.height_medium = min(int(scale * image.height_pre_mplimit), image.height_pre_mplimit)

        scale = math.sqrt(4000000.0 / (image.width_pre_mplimit * image.height_pre_mplimit))
        result.width_hd = min(int(scale * image.width_pre_mplimit), image.width_pre_mplimit)
        result.height_hd = min(int(scale * image.height_pre_mplimit), image.height_pre_mplimit)

        scale = math.sqrt(25000000.0 / (image.width_pre_mplimit * image.height_pre_mplimit))
        result.maxwidth = min(int(scale * image.width_pre_mplimit), image.width_pre_mplimit)
        result.maxheight = min(int(scale * image.height_pre_mplimit), image.height_pre_mplimit)

        times.append(time.time() - t)
        self.logger.info(
            f"[{processing_data.correlation_id}] encoding ({times[-1]:.2f}s) "
            f"| format: {result.format}, overall {sum(times):.2f}s",
        )


class RemovebgServer(ImageServer):

    PROCESSING_FILE = "currently_processing"

    def __init__(
        self,
        request_queue: str,
        rabbitmq_host: str,
        rabbitmq_port: int,
        rabbitmq_user: str,
        rabbitmq_password: str,
        *,
        worker_class: Optional[Type[Worker]],
        mock_response: bool,
        require_models: bool,
        worker_init_kwargs: Optional[Dict[str, Any]] = None,
        worker_count: int = multiprocessing.cpu_count(),
    ) -> None:
        super().__init__(
            request_queue,
            rabbitmq_host,
            rabbitmq_port,
            rabbitmq_user,
            rabbitmq_password,
            worker_class=worker_class,
            worker_init_kwargs=worker_init_kwargs,
            worker_count=worker_count,
        )
        self.removebg = None
        self.identifier = None
        self.error_count = 0
        self.mock_response = mock_response
        self.require_models = require_models
        if not self.mock_response:
            self.logger.info("initializing extractor...")
            from removebg.removebg import Identifier, Removebg

            self.removebg = Removebg(
                "networks-trained/",
                require_models=self.require_models,
                trimap_flip_mean=True,
            )
            self.identifier = Identifier("networks-trained/", require_models=self.require_models)
            assert self.removebg, "Failed to initialize Removebg"
            assert self.identifier, "Failed to initialize Identifier"

    def _process(self, data: ImageProcessingData) -> None:
        processing_data = data.data
        im, shadow = processing_data["im_cv"], processing_data["shadow"]
        result = data.result

        t = time.time()

        processing_data["data"] = None

        if self.mock_response:
            processing_data["data"] = np.dstack((im, np.ones_like(im[:, :, 0]) * 128))
            processing_data["api"] = "mock"
        else:
            # transfer to gpu
            im_tr = to_tensor(im, bgr2rgb=True)

            # overwrite if auto
            if processing_data["api"] == "auto":
                processing_data["api"] = self.identifier(im_tr)

            # be stricter with previews. this way (hopefully) no preview
            # gets accepted while the highres gets rejected.
            trimap_confidence_thresh = 0.25 if im_tr.shape[-1] * im_tr.shape[-2] < 250000 else 0.15
            try:
                # extract background
                im_tr_rgb, im_tr_alpha = self.removebg(
                    im_tr,
                    color_enabled=(processing_data["api"] == "person" or processing_data["api"] == "animal"),
                    shadow_enabled=(processing_data["api"] == "car" and shadow),
                    trimap_confidence_thresh=trimap_confidence_thresh,
                )
            except UnknownForegroundException:
                self.logger.exception(f"[{data.correlation_id}] could not detect foreground")
                result.status = ERROR_STATUS
                result.description = UNKNOWN_FOREGROUND
            else:
                im_rgb = to_numpy(im_tr_rgb, rgb2bgr=True)
                im_alpha = to_numpy(im_tr_alpha)

                processing_data["data"] = np.dstack((im_rgb, np.expand_dims(im_alpha, axis=2)))

        processing_data["time"] = time.time() - t


def main():
    rabbitmq_args = read_rabbitmq_env_variables()
    mock_response = bool(int(os.environ.get("MOCK_RESPONSE", 0)))
    require_models = bool(int(os.environ.get("REQUIRE_MODELS", 1)))
    # number of workers to spawn, defaults to number of cpus
    # be aware that the default worker count might include
    # "virtual" hyperthreaded cpus and impacts memory usage
    worker_count = min(
        int(os.environ.get("MAX_WORKER_COUNT", multiprocessing.cpu_count())), multiprocessing.cpu_count()
    )

    server = RemovebgServer(
        *rabbitmq_args,
        require_models=require_models,
        worker_class=RemovebgWorker,
        mock_response=mock_response,
        worker_count=worker_count,
    )
    server.start()


if __name__ == "__main__":
    # execute only if run as a script
    main()
