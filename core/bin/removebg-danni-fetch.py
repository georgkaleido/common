import argparse
import json
import os

import requests
from kaleido.data.danni.connection import DanniConnection
from kaleido.data.danni.download import download_multiple

parser = argparse.ArgumentParser(description="Generates the danni meta file")
parser.add_argument("--root", required=True, type=str, help="danni user.")
parser.add_argument("--host", default="https://danni.kaleido.ai/", type=str, help="danni user.")
parser.add_argument("--user", required=True, type=str, help="danni user.")
parser.add_argument("--token", required=True, type=str, help="danni password.")
parser.add_argument("--limit", type=int, default=50000, help="limit pages.")
args = parser.parse_args()


os.environ["DANNI_HOST"] = args.host
os.environ["DANNI_USER"] = args.user
os.environ["DANNI_TOKEN"] = args.token

filter_ = {"worker_history.danni-image-remove_background-alpha-thumbnails": True, "set": "test"}

fields = [
    "image.file300k.url",
    "image.remove_background.alpha[].file300k.url",
    "source.user_id",
    "source.source",
]
result_fn_fnames = ["color.jpg", "alpha.png"]


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


print("initializing danni loader...")
conn = DanniConnection()

# add additional filters

filter_ = {"$and": [filter_, {"to_delete": False}]}

params = {
    "fields": ",".join(fields + ["set", "id"]),
    "filter": json.dumps(filter_),
    "limit": args.limit,
    # 'bucket_uris': False
}

page = 1


urls = []
paths = []

while True:

    params["page"] = page

    try:
        data = conn.req(requests.get, "/api/dans", params=params)
    except Exception as e:
        print("got exception while fetching danni data: {}".format(e))
        break

    # no more dans, break
    if not data:
        break

    print("found {} dans".format(len(data)))

    for d in data:

        # create path

        data_sample = result_fn(d)

        # if none is returned, sample is skipped
        if data_sample is None:
            continue

        gr = "other"
        if "source" in d:
            if "source" in d["source"]:
                gr = d["source"]["source"]

            elif "user_id" in d["source"] and d["source"]["user_id"]:
                gr = d["source"]["user_id"]

        fpath = os.path.join(args.root, gr, d["set"], d["id"])
        os.makedirs(fpath, exist_ok=True)

        for fname, ds in zip(result_fn_fnames, data_sample):
            fpath_full = os.path.join(fpath, fname)

            paths.append(fpath_full)
            urls.append(ds)

    page += 1


print("downloading...")
download_multiple(urls, paths)
