import os
import argparse

from kaleido.data.danni.loader import DanniOfflineLoader
from kaleido.data.danni.download import download_single


def main():

    parser = argparse.ArgumentParser(description='Fetch metadata from Danni and save the dataset paths in a text file.')
    parser.add_argument('-i', '--metadata_path', required=True, type=str, help='Path where to save the metadata.')
    args = parser.parse_args()

    print('initializing danni loader...')
    loader = DanniOfflineLoader(args.metadata_path, 'danni-data/')

    # print(loader.samples)

    l = len(loader.samples.keys())
    for fpath, idx in zip(loader.samples.keys(), range(l)):
        sample = loader.samples[fpath]
        fpath = os.path.join('danni-data', fpath)
        print(f"{idx}/{l-1} - Download {sample} to {fpath}")
        download_single((sample, fpath))


if __name__ == '__main__':
    main()
