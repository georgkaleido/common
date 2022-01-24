#!/usr/bin/env python

import argparse
import json
import os
import sys
import time
import PIL
from datetime import datetime, timedelta

import cv2
import numpy as np
import torch
from kaleido.tensor.utils import to_numpy, to_tensor
from removebg.image import SmartAlphaImage
from removebg.removebg import Identifier, Removebg, UnknownForegroundException
from qi_auto.utilities import Bucket


def handle_args():
    # arguments

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to images or to an image")
    parser.add_argument("--path_parent", help="added to suffixes of result images")
    parser.add_argument("--path_networks", default="../../kaleido-models/", help="added to the networks")

    parser.add_argument("--caption", help="added to suffixes of result images")
    parser.add_argument("--mp", type=float, default=4, help="megapixels to output.")
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="enables accuracy evaluation. the input images MUST have a ground truth alpha channel",
    )
    parser.add_argument(
        "--evaluate_file",
        default="{}.json".format(datetime.now().strftime("%d.%m.%Y_%H:%M:%S")),
        help="file where to store the evaluation results",
    )
    parser.add_argument("--skip", action="store_true", help="skip already processed images.")
    parser.add_argument("--save_images", action="store_true", help="Save result images")
    parser.add_argument("--new_archi", action="store_true", help="")

    args = parser.parse_args()

    return args


def demo(args):

    removebg = Removebg(args.path_networks, require_models=False, trimap_flip_mean=True)
    identifier = Identifier(args.path_networks, require_models=False)

    if args.evaluate_file.startswith("gs://"):
        evaluate_file_local = os.path.join("/tmp", os.path.basename(args.evaluate_file))
        on_cloud = True
    else:
        evaluate_file_local = args.evaluate_file
        on_cloud = False

    if on_cloud:
        bucket = Bucket("kaleido-train-checkpoints")
        if bucket.exists(args.evaluate_file):
            bucket.download(args.evaluate_file, evaluate_file_local)

    eval_data = {}
    if args.evaluate:
        args.disable_confidence_thresh = True

        if not args.evaluate_file:
            sys.exit("must set an evaluate file")

        if not os.path.exists(evaluate_file_local):
            with open(evaluate_file_local, "w+"):
                pass

        with open(evaluate_file_local) as f:
            try:
                eval_data = json.load(f)
            except Exception:
                pass

    if args.path:
        if os.path.isfile(args.path):
            files = [args.path]
        elif args.path_parent:
            files = []
            for root, dirs, _ in os.walk(args.path):
                if os.path.basename(root) == args.path_parent:
                    files.extend([os.path.join(root, fname) for fname in dirs])
        else:
            files = [os.path.join(args.path, fname) for fname in os.listdir(args.path)]

        t_start = time.time()

        total = len(files)
        total_elapsed_time = 0
        count_time = 0
        estimated_remaining_time = 0
        for idx, file in enumerate(files):

            is_folder = not os.path.isfile(file)

            if is_folder:
                path_save = os.path.join(file, (args.caption + "_" if args.caption else "") + "result.png")
            else:
                path_save = os.path.join(
                    os.path.dirname(file),
                    os.path.basename(file) + ("_" + args.caption if args.caption else "") + "_result.png",
                )

            dirname = os.path.abspath(os.path.dirname(file)).replace(os.path.abspath(os.path.dirname(args.path)), ".")
            filename = os.path.basename(file)
            if args.skip:
                if args.save_images and os.path.exists(path_save):
                    print(f"Skipping {path_save}")
                    continue
                elif dirname in eval_data.keys() and filename in eval_data[dirname].keys():
                    print(f"Skipping key {dirname} {filename}")
                    continue

            print(f"Processing {idx+1:5d}/{total} "
                  f"Estimated remaining duration {str(timedelta(seconds=estimated_remaining_time))}")

            t0 = time.time()

            # ====================================================
            # data reading + preprocessing

            im_alpha_gt = None

            if os.path.isfile(file):
                if (
                    not file.lower().endswith(".jpg")
                    and not file.lower().endswith(".png")
                    and not file.lower().endswith(".jpeg")
                ) or file.endswith("_result.png"):
                    continue

                image = SmartAlphaImage(file,
                                        megapixel_limit=args.mp,
                                        megapixel_limit_trimap=0.25)

            else:
                subfiles = os.listdir(file)

                if "color.jpg" not in subfiles or "alpha.png" not in subfiles:
                    print("skipping {} because did not find color.jpg, alpha.png".format(file))
                    continue

                image = SmartAlphaImage(os.path.join(file, "color.jpg"),
                                        megapixel_limit=args.mp,
                                        megapixel_limit_trimap=0.25 if args.new_archi else None)
                im_alpha_gt = cv2.imread(os.path.join(file, "alpha.png"), cv2.IMREAD_GRAYSCALE)

            if args.evaluate and im_alpha_gt is None:
                print("error! image {} does not have an alpha channel".format(os.path.basename(file)))
                continue

            s = 224.0 / max(image.width, image.height)
            if s * image.width < 5 or s * image.height < 5:
                print("shape too small: {}x{}".format(image.width, image.height))
                continue

            # generate small image

            t1 = time.time()

            # ====================================================
            # inference

            im_tr = to_tensor(image.get("rgb"), bgr2rgb=False, cuda=True)
            if args.new_archi:
                im_for_trimap_tr = to_tensor(image.get("trimap_opti"), bgr2rgb=False, cuda=True)
            else:
                im_for_trimap_tr = None

            cls = identifier(im_tr)

            if args.disable_confidence_thresh:
                trimap_confidence_thresh = 0
            else:
                trimap_confidence_thresh = 0.55 if im_tr.shape[-1] * im_tr.shape[-2] < 250000 else 0.45

            try:
                im_tr_bgr, im_tr_alpha, trimap_tr = removebg(
                    im_tr,
                    im_for_trimap_tr,
                    color_enabled=True,
                    shadow_enabled=False,
                    trimap_confidence_thresh=trimap_confidence_thresh,
                    extra_trimap_output=True,
                )
            except UnknownForegroundException as e:
                print("could not detect foreground: {}".format(e))
                continue

            # ====================================================
            # postprocessing
            im_bgr = to_numpy(im_tr_bgr, rgb2bgr=True)
            im_alpha = to_numpy(im_tr_alpha)

            # set the result but keep the original version

            im_rgb_precolorcorr = image.get("rgb")
            image.set(np.dstack((im_bgr, np.expand_dims(im_alpha, axis=2))), "bgra", limit_alpha=True)

            t2 = time.time()

            # ====================================================
            # postprocessing

            if not args.evaluate:
                if cls == "car":
                    image.fill_holes(
                        255 if args.no_semitransparency else 200,
                        mode="car",
                        average=(not args.no_semitransparency),
                        im_rgb_precolorcorr=im_rgb_precolorcorr,
                    )

                elif cls == "car_interior":
                    image.fill_holes(
                        0 if args.no_semitransparency else 200,
                        mode="all",
                        average=True,
                        im_rgb_precolorcorr=im_rgb_precolorcorr,
                    )

                if args.subject_crop:
                    image.postproc_fn(
                        "crop_subject",
                        margins=[
                            args.subject_crop_margin,
                            args.subject_crop_margin,
                            args.subject_crop_margin,
                            args.subject_crop_margin,
                        ],
                    )

                if args.subject_scale is not None:
                    image.postproc_fn("scale_subject", scale_new=args.subject_scale)

                if args.subject_x is not None or args.subject_y is not None:
                    image.postproc_fn("position_subject", dx=args.subject_x or 0.5, dy=args.subject_y or 0.5)

            elif args.evaluate_file:
                if os.path.dirname(file) not in eval_data:
                    eval_data[os.path.dirname(file)] = {}

                im_alpha_gt = cv2.resize(
                    im_alpha_gt,
                    (image.im_alpha.shape[1], image.im_alpha.shape[0]),
                    interpolation=cv2.INTER_AREA,
                )

            t3 = time.time()

            # Post process trimap
            trimap_norm_tr = torch.zeros(trimap_tr.shape, dtype=torch.uint8)
            trimap_norm_tr[trimap_tr >= 0.5] = 127
            trimap_norm_tr[trimap_tr >= 1.5] = 255
            trimap = to_numpy(trimap_norm_tr, to_uint8=False)

            if args.save_images:
                if is_folder:
                    path_out = os.path.join(file, (args.caption + "_" if args.caption else "") + "result.png")
                    path_out_trimap = os.path.join(file, (args.caption + "_" if args.caption else "") + "trimap.png")
                else:
                    path_out = os.path.join(
                        os.path.dirname(file),
                        os.path.basename(file) + ("_" + args.caption if args.caption else "") + "_result.png",
                    )
                    path_out_trimap = os.path.join(
                        os.path.dirname(file),
                        os.path.basename(file) + ("_" + args.caption if args.caption else "") + "_trimap.png",
                    )

                im_bytes = image.encode("png")

                with open(path_out, "wb") as f:
                    f.write(im_bytes)
                cv2.imwrite(path_out_trimap, trimap)

            t4 = time.time()

            if dirname not in eval_data:
                eval_data[dirname] = {}
            mse = np.sqrt((1.0 * im_alpha_gt - 1.0 * image.im_alpha) ** 2).mean()
            preproc_ms = (t1 - t0) * 1e3
            inference_ms = (t2 - t1) * 1e3
            eval_data[dirname][filename] = {
                "mse": mse, "preproc_ms": preproc_ms, "inference_ms": inference_ms
            }

            if 0 == (idx % 100) or (idx + 1) == total:
                print(f"Save eval {evaluate_file_local}")
                with open(evaluate_file_local, "w") as f:
                    json.dump(eval_data, f, sort_keys=True, indent=4)
                if on_cloud:
                    print(evaluate_file_local)
                    print(args.evaluate_file)
                    bucket.upload(evaluate_file_local, args.evaluate_file)

            # ====================================================
            # timing

            elapsed_time = t4 - t0
            total_elapsed_time += elapsed_time
            count_time += 1

            avg_elapsed_time = total_elapsed_time/count_time
            estimated_remaining_time = avg_elapsed_time * (total - idx + 1)

            # print(
            #     f"finished {image.width * image.height / 1000000.0:.2f}mp after (+{t1 - t0:.2f}s imread + preproc) "
            #     f"{t4 - t1:.2f}s (+{t3 - t2:.2f}s postproc) (+{t4 - t3:.2f}s saving), "
            #     f"class {cls} [{os.path.basename(file)}]"
            # )

        print("finished after {:.2f}s".format(time.time() - t_start))

        if on_cloud:
            # Upload empty file when finished
            os.system("touch ./dummy")
            bucket.upload("./dummy", f"{args.evaluate_file}_finished")

        os.system("touch /tmp/dummy")


if __name__ == "__main__":
    # execute only if run as a script
    demo(handle_args())
