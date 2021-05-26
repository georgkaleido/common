import json
import matplotlib.pyplot as plt
import cv2
import numpy as np
import argparse
import os
import math

parser = argparse.ArgumentParser()
parser.add_argument('old', help='path to first json')
parser.add_argument('new', help='path to second json')
parser.add_argument('--out', help='out path')
parser.add_argument('--samples', type=int, default=0, help='number of good and bad samples to visualize')
args = parser.parse_args()

if not args.out:
    args.out = 'results_{}_{}/'.format(os.path.splitext(os.path.basename(args.old))[0], os.path.splitext(os.path.basename(args.new))[0])

if not os.path.exists(args.out):
    os.makedirs(args.out)

class Subset:
    def __init__(self, data, path):
        self.path = path
        self.title = path.split('/')[-2]
        self.group = path.split('/')[-3]

        self.scores = [score for score in data[path].values()]
        self.names = [name for name in data[path].keys()]

    def get_scores(self, names):
        return [self.scores[self.names.index(name)] for name in names]

    def compare(self, set):
        if sorted(self.names) != sorted(set.names):
            raise Exception('sets are different!')

        scores = [y / x for x, y in zip(self.scores, set.scores)]
        scores, names = zip(*sorted(zip(scores, self.names), key=lambda a: a[0]))

        return list(scores), list(names)

def read_data(path):
    with open(path) as f:
        data = json.load(f)

    keys = list(data.keys())
    for k in keys:
        if os.path.normpath(k) != k:
            data[os.path.normpath(k)] = data[k]
            del data[k]

    return data

data1 = read_data(args.old)
data2 = read_data(args.new)

paths = []

keys_total = 0
d1_keys_missing = 0
d2_keys_missing = 0

for path in data1.keys():
    if path not in data2.keys():
        print('error with {} - not in new result'.format(path))
        continue

    if len(data1[path]) != len(data2[path]):
        print('error with {} - length mismatch: {} and {}'.format(path, len(data1[path]), len(data2[path])))

        d1_keys = set(data1[path].keys())
        d2_keys = set(data2[path].keys())
        keys = list(d1_keys & d2_keys)

        keys_total += len(d1_keys | d2_keys)
        d1_keys_missing += len(d2_keys) - len(keys)
        d2_keys_missing += len(d1_keys) - len(keys)

        data1[path] = dict([d for d in data1[path].items() if d[0] in keys])
        data2[path] = dict([d for d in data2[path].items() if d[0] in keys])

        #continue

    paths.append(path)

print('keys: {}/{} ({}), {}/{} ({})'.format(keys_total - d1_keys_missing, keys_total, args.old, keys_total - d2_keys_missing, keys_total, args.new))

if not paths:
    import sys
    print('did not find any paths')
    sys.exit(0)

sets1 = [Subset(data1, path) for path in paths]
sets2 = [Subset(data2, path) for path in paths]

def save_plot(scores, median, path_out, title):

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    x = range(len(scores))

    ax.set_title(title)
    ax.set_yscale('log')

    ax.set_ylim(min(scores + [1])*0.95, max(scores + [1])*1.05)
    ax.scatter(x, scores, s=5)
    ax.plot((0, len(x)-1), (median, median), c='r')

    ax.spines['top'].set_position(('data', 1))
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.set_xticks([], [])
    ax.set_xlabel('{:.2f}%'.format((1. - median) * 100.), color=('green' if median < 1. else 'red'))

    ax.yaxis.set_major_formatter(plt.ScalarFormatter())
    ax.yaxis.set_minor_formatter(plt.NullFormatter())
    ax.yaxis.set_major_locator(plt.AutoLocator())


    plt.savefig(path_out)
    plt.close()

# compare individuals

for set1, set2 in zip(sets1, sets2):

    scores, names = set1.compare(set2)
    median = np.median(scores)

    path_out = os.path.join(args.out, 'individual')
    if not os.path.exists(path_out):
        os.makedirs(path_out)

    dirname = '{:.4f}_{}_{}'.format(median, set1.title, set1.group)

    save_plot(scores, median, os.path.join(path_out, '{}.png'.format(dirname)), '{} ({})'.format(set1.title, set1.group))

    # create folder

    if not os.path.exists(os.path.join(path_out, dirname)):
        os.mkdir(os.path.join(path_out, dirname))

    # save info

    with open(os.path.join(path_out, dirname, 'data.txt'), 'w') as f:
        for score, x, y, fname in zip(scores, set1.get_scores(names), set2.get_scores(names), names):
            f.write('{:.4f} {:.4f} {:.4f} {}\n'.format(score, x, y, fname))

    # stitch images

    samples_good = list(zip(scores, names))[:args.samples]
    samples_bad = list(zip(scores, names))[-args.samples:] if args.samples > 0 else []

    def save_samples(samples):

        for score, name in samples:
            path_col = os.path.join(os.path.join(set1.path, name, 'color.jpg'))
            path_gt = os.path.join(os.path.join(set1.path, name, 'alpha.png'))
            path_old = os.path.join(os.path.join(set1.path, name, '{}_result.png'.format(os.path.splitext(os.path.basename(args.old))[0])))
            path_new = os.path.join(os.path.join(set1.path, name, '{}_result.png'.format(os.path.splitext(os.path.basename(args.new))[0])))

            if not (os.path.exists(path_col) and os.path.exists(path_gt) and os.path.exists(path_old) and os.path.exists(path_new)):
                print('could not generate visualization. images are missing: \n\t{}\n\t{}\n\t{}\n\t{}'.format(path_col, path_gt, path_old, path_new))
                return

            # read images and pad them

            im_col = cv2.imread(path_col, cv2.IMREAD_COLOR)
            im_alpha = cv2.imread(path_gt, cv2.IMREAD_GRAYSCALE)

            im = np.dstack((im_col, np.expand_dims(im_alpha, 2)))
            im_old = cv2.imread(path_old, cv2.IMREAD_UNCHANGED)
            im_new = cv2.imread(path_new, cv2.IMREAD_UNCHANGED)

            # resize them to 0.25mp

            scale = math.sqrt(250000 / (im.shape[0] * im.shape[1]))
            w = int(im.shape[1] * scale)
            h = int(im.shape[0] * scale)

            im = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)
            im_old = cv2.resize(im_old, (w, h), interpolation=cv2.INTER_AREA)
            im_new = cv2.resize(im_new, (w, h), interpolation=cv2.INTER_AREA)

            # blend on red

            im_gt = im[:, :, :3] * (im[:, :, 3:4] / 255.) + [0, 0, 255] * (1. - im[:, :, 3:4] / 255.)
            im_old = im_old[:, :, :3] * (im_old[:, :, 3:4] / 255.) + [0, 0, 255] * (1. - im_old[:, :, 3:4] / 255.)
            im_new = im_new[:, :, :3] * (im_new[:, :, 3:4] / 255.) + [0, 0, 255] * (1. - im_new[:, :, 3:4] / 255.)

            # concatenate

            im = np.vstack((np.hstack((im[:, :, :3], im_gt)), np.hstack((im_old, im_new))))


            def putText(text, pos):
                cv2.putText(im, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 5, cv2.LINE_AA)
                cv2.putText(im, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

            offset = 25
            putText('color', (offset, offset))
            putText('gt', (offset + w, offset))
            putText('old', (offset, offset + h))
            putText('new', (offset + w, offset + h))

            # save

            cv2.imwrite(os.path.join(path_out, dirname, '{:.4f}.png'.format(score)), im)

    save_samples(samples_good)
    save_samples(samples_bad)

# compare groups

groups_scores = {}
for set1, set2 in zip(sets1, sets2):

    if set1.group not in groups_scores:
        groups_scores[set1.group] = []

    groups_scores[set1.group].append(np.median(set1.compare(set2)[0]))

scores_all = []
for group, scores in groups_scores.items():

    mean = np.mean(scores)
    dirname = '{:.4f}_{}'.format(mean, group)

    save_plot(sorted(scores), mean, os.path.join(args.out, '{}.png'.format(dirname)), '{}'.format(group))

    scores_all.append(mean)

# all

save_plot(sorted(scores_all), np.mean(scores_all), os.path.join(args.out, 'all.png'), 'all')

