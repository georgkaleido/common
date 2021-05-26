import os
import argparse

from kaleido.data.danni.loader import DanniLoader


def main():

    parser = argparse.ArgumentParser(description='Fetch metadata from Danni and save the dataset paths in a json file.')
    parser.add_argument('-o', '--metadata_output_path', required=True, type=str, help='Path where to save the metadata.')
    parser.add_argument('-u', '--user', required=True, type=str, help='danni user.')
    parser.add_argument('-t', '--token', required=True, type=str, help='danni password.')
    parser.add_argument('-m', '--max_pages', type=int, default=None, help='limit pages.')
    parser.add_argument('-f', '--filter', type=str, default=None, help='limit pages.')
    args = parser.parse_args()

    os.environ['DANNI_HOST'] = 'https://danni.kaleido.ai/'
    os.environ['DANNI_USER'] = args.user
    os.environ['DANNI_TOKEN'] = args.token

    filter_ = {
        'worker_history.danni-image-remove_background-alpha-thumbnails': True,
    }

    fields = ['image.file300k.url', 'image.remove_background.alpha[].file300k.url']
    result_fn_names = ['color.jpg', 'alpha.png']

    def result_fn(d):
        im_color_url = d.get('image', {}).get('file300k', {}).get('url')

        # Get list of alpha masks
        alpha_mask_list = im_alpha_url = d.get('image', {}).get('remove_background', {}).get('alpha', [{}])
        # Sort the list with field `created_at`, in reverse order: Most recent first
        alpha_mask_list.sort(key=lambda alpha_mask: alpha_mask.get('created_at'), reverse=True)
        # Get the first mask with `file300k` field
        im_alpha_url = None
        for alpha_mask in alpha_mask_list:
            im_alpha_url = alpha_mask.get('file300k', {}).get('url')
            if im_alpha_url is not None:
                break

        if not im_color_url or not im_alpha_url:
            return None

        return [im_color_url, im_alpha_url]

    print('initializing danni loader...')
    danni_loader = DanniLoader(filter_, fields, result_fn, result_fn_names,
                               mode="save",
                               metadata_output_path=args.metadata_output_path,
                               limit=1000,
                               max_pages=args.max_pages)

    print(f"Effective number of samples fetched: {len(danni_loader.samples)}")


if __name__ == '__main__':
    main()
