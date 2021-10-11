import argparse

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

    print(loader.samples)


if __name__ == "__main__":
    main()
