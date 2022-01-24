#!/usr/bin/env python

import argparse
import torch
import os
from datetime import datetime, timedelta

import cv2
import numpy as np


def handle_args():
    # arguments

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to images or to an image")
    parser.add_argument("--name_preview", default="ref_preview_result.png")
    parser.add_argument("--name_fullres", default="ref_fullres_result.png")

    parser.add_argument(
        "--result_file",
        default="{}.json".format(datetime.now().strftime("%d.%m.%Y_%H:%M:%S")),
        help="file where to store the evaluation results",
    )

    args = parser.parse_args()

    return args


def accuracy(trimap, trimap_target):
    trimap = torch.from_numpy(trimap)
    trimap_target = torch.from_numpy(trimap_target)

    num_class = 3

    # trimap = torch.argmax(trimap_output, dim=1).unsqueeze(dim=1)
    mask = (trimap_target >= 0) & (trimap_target < num_class)
    # mask = mask & (weights > 0)
    label = num_class * trimap_target[mask].long() + trimap[mask]

    cm = torch.bincount(label, None, num_class ** 2).reshape(num_class, num_class).float()
    iou = cm.diag() / (cm.sum(dim=0) + cm.sum(dim=1) - cm.diag())
    miou = iou[~torch.isnan(iou)].mean()

    return miou


def main(args):

    samples = []
    for root, dirs, _ in os.walk(args.path):
        if os.path.basename(root) == "test":
            samples.extend([os.path.join(root, fname) for fname in dirs])

    samples_with_low_iou = []
    low_iou_threshold = 0.95

    total = len(samples)
    for idx, sample in enumerate(samples):

        print(f"{(idx+1):06d}/{total}: {sample}")

        path_preview = os.path.join(sample, args.name_preview)
        path_fullres = os.path.join(sample, args.name_fullres)

        # Load image
        trimap_preview = cv2.imread(path_preview, cv2.IMREAD_UNCHANGED)
        trimap_fullres = cv2.imread(path_fullres, cv2.IMREAD_UNCHANGED)

        if trimap_preview is None:
            print("Could not load preview trimap")
            continue
        if trimap_fullres is None:
            print("Could not load fullres trimap")
            continue

        # Normalize trimaps to [0;num_class] instead of [0;255]
        trimap_preview = (trimap_preview / 127).astype(np.uint8)
        trimap_fullres = (trimap_fullres / 127).astype(np.uint8)

        # resize fullres
        trimap_fullres = cv2.resize(trimap_fullres, (trimap_preview.shape[1], trimap_preview.shape[0]), interpolation=cv2.INTER_NEAREST)

        mIoU = accuracy(trimap_fullres, trimap_preview)

        if mIoU < low_iou_threshold:
            samples_with_low_iou.append(sample)

    print(f"Samples with IoU < {low_iou_threshold}")
    for sample in samples_with_low_iou:
        print(sample)

    print(f"Total samples with IoU < {low_iou_threshold}: {len(samples_with_low_iou)}")


if __name__ == "__main__":
    # execute only if run as a script
    main(handle_args())
