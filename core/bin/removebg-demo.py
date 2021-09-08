#!/usr/bin/env python

import argparse
import cv2
import os
import time
import numpy as np
import sys
import json
from datetime import datetime

from kaleido.tensor.utils import to_tensor, to_numpy
from removebg.image import SmartAlphaImage
from removebg.removebg import Removebg, UnknownForegroundException, Identifier


def handle_args():
    # arguments

    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path to images or to an image')
    parser.add_argument('--path_parent', help='added to suffixes of result images')
    parser.add_argument('--path_networks', default='../../kaleido-models/', help='added to the networks')
    parser.add_argument('--caption', help='added to suffixes of result images')
    parser.add_argument('--mp', type=float, default=4, help='megapixels to output.')
    parser.add_argument('--no_color', action='store_true', help='disable color correction')
    parser.add_argument('--bg_image', help='underlay background image')
    parser.add_argument('--bg_color', help='fill with bg color. e.g. ffffffff')
    parser.add_argument('--dont_save', action='store_true', help='do not save the result files.')
    parser.add_argument('--evaluate', action='store_true', help='enables accuracy evaluation. the input images MUST have a ground truth alpha channel')
    parser.add_argument('--evaluate_file', default='{}.json'.format(datetime.now().strftime("%d.%m.%Y_%H:%M:%S")), help='file where to store the evaluation results')
    parser.add_argument('--shadow', action='store_true', help='add shadow to im.')
    parser.add_argument('--disable_confidence_thresh', action='store_true', help='disables the bad-quality filtering')
    parser.add_argument('--only_alpha', action='store_true', help='extract only alpha channel.')
    parser.add_argument('--only_color', action='store_true', help='extract only color channels.')
    parser.add_argument('--no_semitransparency', action='store_true', help='no semitransparent car windows.')
    parser.add_argument('--skip', action='store_true', help='skip already processed images.')

    parser.add_argument('--subject_scale', type=float, help='scales the output subject. between [0, 1]')
    parser.add_argument('--subject_x', type=float, help='positions the output subject. between [0, 1]')
    parser.add_argument('--subject_y', type=float, help='positions the output subject. between [0, 1]')
    parser.add_argument('--subject_crop', action='store_true', help='crops the image to the subject')
    parser.add_argument('--subject_crop_margin', default=0, type=int, help='relative crop margin')

    args = parser.parse_args()
    return args


def demo(args):

    removebg = Removebg(args.path_networks, require_models=False, trimap_flip_mean=True)
    identifier = Identifier(args.path_networks, require_models=False)

    eval_data = {}
    path_eval = 'evaluation/'
    if args.evaluate:
        args.disable_confidence_thresh = True

        if not args.evaluate_file:
            sys.exit('must set an evaluate file')

        if not os.path.exists(args.evaluate_file):
            with open(args.evaluate_file, 'w+'):
                pass

        with open(args.evaluate_file) as f:
            try:
                eval_data = json.load(f)
            except:
                pass

    if args.bg_image:
        background = cv2.imread(args.bg_image, cv2.IMREAD_UNCHANGED)
        assert(background is not None)

    if args.bg_color:
        args.bg_color = list(int(args.bg_color[i:i + 2], 16) for i in (0, 2, 4, 6))
        assert(len(args.bg_color) == 4)

    if args.path:
        if os.path.isfile(args.path):
            files = [args.path]
        elif args.path_parent:
            files = set()
            for root, dirs, _ in os.walk(args.path):
                if os.path.basename(root) == args.path_parent:
                    files.update(os.path.join(root, fname) for fname in dirs)
            files = list(files)
        else:
            files = [os.path.join(args.path, fname) for fname in os.listdir(args.path)]

        t_start = time.time()

        for file in files:

            is_folder = not os.path.isfile(file)

            if is_folder:
                path_save = os.path.join(file, (args.caption + '_' if args.caption else '') + 'result.png')
            else:
                path_save = os.path.join(os.path.dirname(file), os.path.basename(file) + ('_' + args.caption if args.caption else '') + '_result.png')

            if args.skip and os.path.exists(path_save):
                print('skipping {}'.format(path_save))
                continue

            t0 = time.time()

            # ====================================================
            # data reading + preprocessing

            im_alpha_gt = None

            if os.path.isfile(file):
                if (not file.lower().endswith('.jpg') and not file.lower().endswith('.png') and not file.lower().endswith('.jpeg')) or file.endswith('_result.png'):
                    continue

                image = SmartAlphaImage(file, megapixel_limit=args.mp)

            else:
                subfiles = os.listdir(file)

                if 'color.jpg' not in subfiles or 'alpha.png' not in subfiles:
                    print('skipping {} because did not find color.jpg, alpha.png'.format(file))
                    continue

                image = SmartAlphaImage(os.path.join(file, 'color.jpg'), megapixel_limit=args.mp)
                im_alpha_gt = cv2.imread(os.path.join(file, 'alpha.png'), cv2.IMREAD_GRAYSCALE)

            if args.evaluate and im_alpha_gt is None:
                print('error! image {} does not have an alpha channel'.format(os.path.basename(file)))
                continue

            s = 224. / max(image.width, image.height)
            if s * image.width < 5 or s * image.height < 5:
                print('shape too small: {}x{}'.format(image.width, image.height))
                continue

            # generate small image

            t1 = time.time()

            # ====================================================
            # inference

            im_tr = to_tensor(image.get('rgb'), bgr2rgb=False, cuda=True)

            cls = identifier(im_tr)

            if args.disable_confidence_thresh:
                trimap_confidence_thresh = 0
            else:
                trimap_confidence_thresh = 0.55 if im_tr.shape[-1] * im_tr.shape[-2] < 250000 else 0.45

            try:
                im_tr_bgr, im_tr_alpha = removebg(im_tr, color_enabled=(not args.no_color), shadow_enabled=args.shadow, trimap_confidence_thresh=trimap_confidence_thresh)
            except UnknownForegroundException as e:
                print('could not detect foreground: {}'.format(e))
                continue

            im_bgr = to_numpy(im_tr_bgr, rgb2bgr=True)
            im_alpha = to_numpy(im_tr_alpha)

            # set the result but keep the original version

            im_rgb_precolorcorr = image.get('rgb')
            image.set(np.dstack((im_bgr, np.expand_dims(im_alpha, axis=2))), 'bgra', limit_alpha=True)

            t2 = time.time()

            # ====================================================
            # postprocessing

            if not args.evaluate:
                if cls == 'car':
                    image.fill_holes(255 if args.no_semitransparency else 200, mode='car', average=(not args.no_semitransparency), im_rgb_precolorcorr=im_rgb_precolorcorr)

                elif cls == 'car_interior':
                    image.fill_holes(0 if args.no_semitransparency else 200, mode='all', average=True, im_rgb_precolorcorr=im_rgb_precolorcorr)

                if args.subject_crop:
                    image.postproc_fn('crop_subject', margins=[args.subject_crop_margin, args.subject_crop_margin, args.subject_crop_margin, args.subject_crop_margin])

                if args.subject_scale is not None:
                    image.postproc_fn('scale_subject', scale_new=args.subject_scale)

                if args.subject_x is not None or args.subject_y is not None:
                    image.postproc_fn('position_subject', dx=args.subject_x or 0.5, dy=args.subject_y or 0.5)

                if args.bg_image:
                    image.underlay_background(background)

                if args.bg_color:
                    image.underlay_background(args.bg_color)

            elif args.evaluate_file:
                if os.path.dirname(file) not in eval_data:
                    eval_data[os.path.dirname(file)] = {}

                im_alpha_gt = cv2.resize(im_alpha_gt, (image.im_alpha.shape[1], image.im_alpha.shape[0]), interpolation=cv2.INTER_AREA)
                eval_data[os.path.dirname(file)][os.path.basename(file)] = np.sqrt((1. * im_alpha_gt - 1. * image.im_alpha) ** 2).mean()

                with open(args.evaluate_file, 'w') as f:
                    json.dump(eval_data, f, sort_keys=True, indent=4)

            t3 = time.time()

            if not args.dont_save:

                if is_folder:
                    path_out = os.path.join(file, (args.caption + '_' if args.caption else '') + 'result.png')
                else:
                    path_out = os.path.join(os.path.dirname(file), os.path.basename(file) + ('_' + args.caption if args.caption else '') + '_result.png')

                if args.only_alpha:
                    im_bytes = image.encode('png_alpha')
                elif args.only_color:
                    im_bytes = image.encode('jpg_color')
                else:
                    im_bytes = image.encode('png')

                with open(path_out, 'wb') as f:
                    f.write(im_bytes)

            t4 = time.time()

            # ====================================================
            # timing

            print('finished {:.2f}mp after (+{:.2f}s imread + preproc) {:.2f}s (+{:.2f}s postproc) (+{:.2f}s saving), class {} [{}]'.format(image.width * image.height / 1000000.0, t1 - t0, t4 - t1, t3 - t2, t4 - t3, cls, os.path.basename(file)))

        print('finished after {:.2f}s'.format(time.time() - t_start))


if __name__ == "__main__":
    # execute only if run as a script
    demo(handle_args())
