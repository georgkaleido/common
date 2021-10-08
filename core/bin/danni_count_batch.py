import os
import time
from datetime import datetime
import argparse
import requests
import json

from kaleido.data.danni.connection import DanniConnection


def main():
    parser = argparse.ArgumentParser(description='Count how many valid Dans belong to a batch, at a specific date.')
    parser.add_argument('-u', '--user', default=None, type=str, help='danni user.')
    parser.add_argument('-t', '--token', default=None, type=str, help='danni password.')
    parser.add_argument('-b', '--batch', required=True, type=str, help='batch name.')
    parser.add_argument('-d', '--date', default=datetime.today().strftime('%Y-%m-%d'), type=str, help='Get Dans up until this date, in format %Y-%m-%d')
    args = parser.parse_args()

    if "DANNI_USER" not in os.environ and args.user is None:
        raise RuntimeError(
            "Missing user credential for Danni. Either as environment variable DANNI_USER or as argument --user")
    if "DANNI_TOKEN" not in os.environ and args.token is None:
        raise RuntimeError(
            "Missing token credential for Danni. Either as environment variable DANNI_TOKEN or as argument --token")

    os.environ["DANNI_HOST"] = "https://danni.kaleido.ai/"
    if args.user:
        os.environ["DANNI_USER"] = args.user
    if args.token:
        os.environ["DANNI_TOKEN"] = args.token

    # Compute date
    try:
        dt_start = datetime.strptime(str(args.date), '%Y-%m-%d')
    except ValueError:
        print("Incorrect format for argument date")
        exit(1)

    date_boundary = int((dt_start - datetime(1970, 1, 1)).total_seconds())
    print(f"{args.date} -> {date_boundary} seconds since epoch.")

    filter_dict = {"image.remove_background.batches": args.batch, "to_delete": False,
                   "$and": [{"image.remove_background.alpha.qc.status": "ok"},
                            {"image.remove_background.alpha.qc.created_at": {"$lte": date_boundary}}]}

    params = {"filter": json.dumps(filter_dict), "bucket_uris": True, "limit": 1000}

    # create connection
    conn = DanniConnection()

    page = 1
    num_samples = 0

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

        num_samples += len(data)
        print(f"Page {page} -> {num_samples} samples")

        page += 1

    print(f"Until {args.date}, {num_samples} valid images in batch \"{args.batch}\"")


if __name__ == '__main__':
    main()
