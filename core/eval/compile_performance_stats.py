#!/usr/bin/env python

import argparse
import json


def handle_args():
    # arguments

    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str)

    args = parser.parse_args()

    return args


def main(args):

    with open(args.path) as f:
        data_a = json.load(f)

    preproc_count = 0
    preproc_ms_total = 0.

    inference_count = 0
    inference_ms_total = 0.

    mse_count = 0
    mse_total = 0.

    for k1, v1 in data_a.items():
        for k2, v2 in v1.items():
            preproc_ms_total += v2["preproc_ms"]
            preproc_count += 1
            inference_ms_total += v2["inference_ms"]
            inference_count += 1
            mse_total += v2["mse"]
            mse_count += 1

    preproc_ms_average = preproc_ms_total / preproc_count
    inference_ms_average = inference_ms_total / inference_count
    mse_average = mse_total / mse_count

    print(f"preproc_ms_average = {preproc_ms_average}")
    print(f"inference_ms_average = {inference_ms_average}")
    print(f"mse_average = {mse_average}")


if __name__ == "__main__":
    # execute only if run as a script
    main(handle_args())
