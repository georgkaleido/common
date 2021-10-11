import argparse
import os

from kaleido.data.danni.download import download_single
from kaleido.data.danni.loader import DanniOfflineLoader


def main():

    parser = argparse.ArgumentParser(
        description="Fetch metadata from Danni and save the dataset paths in a text file."
    )
    parser.add_argument(
        "-i", "--metadata_path", required=True, type=str, help="Path where to save the metadata."
    )
    args = parser.parse_args()

    print("initializing danni loader...")
    loader = DanniOfflineLoader(args.metadata_path, "danni-data/")

    # print(loader.samples)

    nr_of_samples = len(loader.samples.keys())
    for fpath, idx in zip(loader.samples.keys(), range(nr_of_samples)):
        sample = loader.samples[fpath]
        fpath = os.path.join("danni-data", fpath)
        print(f"{idx}/{nr_of_samples-1} - Download {sample} to {fpath}")
        download_single((sample, fpath))


if __name__ == "__main__":
    main()
