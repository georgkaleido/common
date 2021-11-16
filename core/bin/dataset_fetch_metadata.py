import argparse
import os

from kaleido.data.danni.loader import DanniLoader


def dataset_fetch_metadata(user, token, metadata_output_path, max_pages, test_split, batch_names=None):
    os.environ["DANNI_HOST"] = "https://danni.kaleido.ai/"
    os.environ["DANNI_USER"] = user
    os.environ["DANNI_TOKEN"] = token

    filter_ = {"worker_history.danni-image-remove_background-alpha-thumbnails": True}

    fields = ["image.file300k.url", "image.remove_background.alpha[].file300k.url", "image.remove_background.batches"]
    result_fn_names = ["color.jpg", "alpha.png"]

    if test_split:
        filter_["set"] = "test"

        fields.append("source.user_id")
        fields.append("source.source")
    else:
        filter_["$or"] = [{"set": "train"}, {"set": "valid"}]

    if batch_names:
        batch_names_dict_list = []
        for batch_name in batch_names:
            batch_names_dict_list.append({"image.remove_background.batches": batch_name})
        if "$or" in filter_.keys():
            previous_or = filter_["$or"]
            del filter_["$or"]
            filter_["$and"] = [{"$or": previous_or}, {"$or": batch_names_dict_list}]
        else:
            filter_["$or"] = batch_names_dict_list

    def result_fn(d):
        im_color_url = d.get("image", {}).get("file300k", {}).get("url")

        # Get list of alpha masks
        alpha_mask_list = im_alpha_url = d.get("image", {}).get("remove_background", {}).get("alpha", [{}])
        # Sort the list with field `created_at`, in reverse order: Most recent first
        alpha_mask_list.sort(key=lambda alpha_mask: alpha_mask.get("created_at"), reverse=True)
        # Get the first mask with `file300k` field
        im_alpha_url = None
        for alpha_mask in alpha_mask_list:
            im_alpha_url = alpha_mask.get("file300k", {}).get("url")
            if im_alpha_url is not None:
                break

        if not im_color_url or not im_alpha_url:
            return None

        return [im_color_url, im_alpha_url]

    def group_fn(d):
        group = "other"
        if "source" in d:
            if "source" in d["source"]:
                group = d["source"]["source"]
            elif "user_id" in d["source"] and d["source"]["user_id"]:
                group = d["source"]["user_id"]
        return group

    def batch_fn(d):
        batch = "other"
        if "image" in d and "remove_background" in d["image"] and "batches" in d["image"]["remove_background"]:
            if d["image"]["remove_background"]["batches"]:
                batch = d["image"]["remove_background"]["batches"][0]
        return batch

    print("initializing danni loader...")
    danni_loader = DanniLoader(
        filter_,
        fields,
        result_fn,
        result_fn_names,
        group_fn=(batch_fn if batch_names else group_fn) if test_split else None,
        mode="save",
        metadata_output_path=metadata_output_path,
        limit=1000,
        max_pages=max_pages,
    )

    print(f"Effective number of samples fetched: {len(danni_loader.samples)}")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch metadata from Danni and save the dataset paths in a json file."
    )
    parser.add_argument(
        "-o", "--metadata_output_path", required=True, type=str, help="Path where to save the metadata."
    )
    parser.add_argument("-u", "--user", required=True, type=str, help="danni user.")
    parser.add_argument("-t", "--token", required=True, type=str, help="danni password.")
    parser.add_argument("-m", "--max_pages", type=int, default=None, help="limit pages.")
    parser.add_argument("--test_split", action="store_true", help="Grab test split instead of train/valid")
    parser.add_argument("-b", "--batch_names", required=False, type=str, default=[], nargs="+",
                        help="Optionally filter with batch names")
    args = parser.parse_args()

    dataset_fetch_metadata(
        user=args.user,
        token=args.token,
        metadata_output_path=args.metadata_output_path,
        max_pages=args.max_pages,
        test_split=args.test_split,
        batch_names=args.batch_names,
    )


if __name__ == "__main__":
    main()
