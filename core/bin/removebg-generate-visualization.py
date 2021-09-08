import os
import sys
import cv2
import argparse
import numpy as np

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('path_color', help='path to the color image')
parser.add_argument('path_alpha', help='path to the alpha image')

args = parser.parse_args()

if not os.path.exists(args.path_color):
    sys.exit('{} does not exist!'.format(args.path_color))

if not os.path.exists(args.path_alpha):
    sys.exit('{} does not exist!'.format(args.path_alpha))

im_color = cv2.imread(args.path_color, cv2.IMREAD_COLOR)
im_alpha = cv2.imread(args.path_alpha, cv2.IMREAD_GRAYSCALE)

# generate visualization

m = im_alpha > 0
im_color[..., 2][m] = (im_color[..., 2][m] + 255.).clip(0, 255).astype(np.uint8)

contours, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)[-2:]
cv2.drawContours(im_color, contours, -1, 255, 3, lineType=cv2.LINE_AA)

cv2.imwrite(args.path_color + '_vis.jpg', im_color)
