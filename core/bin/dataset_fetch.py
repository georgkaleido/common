import os
import argparse

# Extra imports
from kaleido.data.danni.download import download_single
from kaleido.data.danni.loader import DanniMetadataSerializer


def fetch_dataset(metadata_path, output_path):

    print('initializing danni loader...')
    samples = DanniMetadataSerializer.read_samples_list(metadata_path)

    for rel_path, url in samples.items():
        path = os.path.join(output_path, rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        download_single((url, path))


def main():
    parser = argparse.ArgumentParser(description='Fetch metadata from Danni and save the dataset paths in a json file.')
    parser.add_argument('-i', '--metadata_path', required=True, type=str, help='Path to a .json file containing the metadata.')
    parser.add_argument('-o', '--output_path', required=True, type=str, help='Path where to save the dataset')
    args = parser.parse_args()

    fetch_dataset(args.metadata_path, args.output_path)


if __name__ == '__main__':
    main()
