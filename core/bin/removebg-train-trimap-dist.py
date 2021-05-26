#!/usr/bin/env python

# Standard import
import os
import json
import torch
import multiprocessing

from removebg.training.trimap import PlTrimap
from kaleido.training.dataset import Dataset
from kaleido.data.danni.loader import DanniLoader

# Extra imports
import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger

from kaleido.training.helpers import download_checkpoint
from kaleido.training.gce.utilities import configure_cloud_training
from kaleido.training.distributed.utilities import configure_distributed, callbacks_distributed

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Train trimap.')
    parser.add_argument('--name', required=True, type=str, help='name of the run')
    parser.add_argument('--config', required=True, help='path to the training pipeline config.')
    parser.add_argument('--bs', type=int, default=4, help='batch size.')
    parser.add_argument('--lr', type=float, default=0.00001, help='batch size.')
    parser.add_argument('--workers', type=int, help='number of workers.', default=multiprocessing.cpu_count())
    parser.add_argument('--danni_user', required=True, type=str, help='danni user.')
    parser.add_argument('--danni_token', required=True, type=str, help='danni password.')
    parser.add_argument('--wandb_api_key', type=str, help='wandb api key.')
    parser.add_argument('--checkpoint_url', type=str, help='checkpoint url to start.')
    parser.add_argument('--danni_max_pages', type=int, help='limit pages.')
    parser.add_argument('--danni_page_size', type=int, default=10000, help='limit pages.')
    args = parser.parse_args()

    if not args.wandb_api_key:
        os.environ['WANDB_MODE'] = 'dryrun'
    else:
        os.environ['WANDB_API_KEY'] = args.wandb_api_key

    os.environ['DANNI_HOST'] = 'https://danni.kaleido.ai/'
    os.environ['DANNI_USER'] = args.danni_user
    os.environ['DANNI_TOKEN'] = args.danni_token

    filter_ = {
      'worker_history.danni-image-remove_background-alpha-thumbnails': True
    }

    fields = ['image.file300k.url', 'image.remove_background.alpha[].file300k.url']
    result_fn_names = ['color.jpg', 'alpha.png']

    def result_fn(d):

      im_color_url = d.get('image', {}).get('file300k', {}).get('url')
      im_alpha_url = d.get('image', {}).get('remove_background', {}).get('alpha', [{}])[-1].get('file300k', {}).get('url')

      if not im_color_url or not im_alpha_url:
        return None

      return [im_color_url, im_alpha_url]

    print('initializing danni loader...')
    loader = DanniLoader('danni-data/', filter_, fields, result_fn, result_fn_names, limit=args.danni_page_size, max_pages=args.danni_max_pages)

    # set the seed

    pl.seed_everything(42)

    # Initialize Dataloader

    print('initializing data loaders...')
    with open(args.config, 'r') as f:
        config = json.load(f)

    '''
    def pre_load_callback(fpath):
        from kaleido.data.danni.download import download_single

        # check if the files are empty and if yes, download

        if not os.path.exists(fpath):
            raise RuntimeError('path must exist! {}'.format(fpath))

        print('CALLBACK')

        # if not empty, return (already loaded)
        if os.path.getsize(fpath) != 0:
            return

        print('getsize')

        # check if file is in list
        fpath_rel = loader._to_relative_path(fpath)

        print('relpath', fpath_rel)

        if fpath_rel not in loader.samples:
            raise RuntimeError(
                '{} was not fetched during initialization! maybe the training was restarted and the dan was deleted in danni?')

        print('downloading')
        # download the url
        import shutil
        import requests
        from urllib.parse import urlparse
        from kaleido.data.download import download_blob

        url, path = loader.samples[fpath_rel], fpath

        try:
            print(url, path)

            o = urlparse(url)

            print(o.scheme)

            if o.scheme == 'gs':
                download_blob(o.netloc, o.path[1:], path)

                print('downloaded blob')
            else:
                # not a bucket url
                response = requests.get(url, stream=True)

                with open(path, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)

                print('downloaded other')

        except Exception as e:
            print('{} error: {}'.format(url, e))

        print('done')
    '''

    train_dataset = Dataset('danni-data/', config, is_train=True, report_augmentation_timings=False, pre_load_callback=loader.pre_load_callback)
    valid_dataset = Dataset('danni-data/', config, is_train=False, report_augmentation_timings=False, pre_load_callback=loader.pre_load_callback)
    #train_dataset = Dataset('danni-data/', config, is_train=True, report_augmentation_timings=False, pre_load_callback=pre_load_callback)
    #valid_dataset = Dataset('danni-data/', config, is_train=False, report_augmentation_timings=False, pre_load_callback=pre_load_callback)

    num_replicas = int(os.environ['WORLD_SIZE'])
    rank = int(os.environ['RANK'])
    train_sampler = torch.utils.data.distributed.DistributedSampler(train_dataset, num_replicas=num_replicas, rank=rank, shuffle=True)
    valid_sampler = torch.utils.data.distributed.DistributedSampler(valid_dataset, num_replicas=num_replicas, rank=rank, shuffle=False)

    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=args.bs, num_workers=args.workers, sampler=train_sampler, drop_last=True)
    valid_loader = torch.utils.data.DataLoader(valid_dataset, batch_size=8, num_workers=args.workers, sampler=valid_sampler)

    # Setup logger

    path = f'results_{args.name}/'
    os.makedirs(path, exist_ok=True)

    logger = pl.loggers.WandbLogger(
        name=args.name,
        project='trimap',
        save_dir=path,
        offline=False,
        id=args.name  # for resuming
    )

    checkpoint_dir_local_path = os.path.join(path, 'checkpoints')

    # Define callbacks

    callbacks = []

    callbacks.append(
        pl.callbacks.ModelCheckpoint(
            save_last=True,
            save_top_k=1,
            dirpath=checkpoint_dir_local_path,
            filename='best',
            verbose=True,
            monitor='avg_val_accuracy',
            mode='max'
        )
    )

    callbacks.append(pl.callbacks.ProgressBar(5, 0))

    # Configure cloud training on GCP -> Checkpoint synchronization on bucket

    configure_cloud_training(checkpoint_dir_local_path, callbacks, 'removebg', args.name, bucket_category="torchelastic", checkpoint_names=["last.ckpt", "best.ckpt"])

    # Create trainer

    last_checkpoint_dir = os.path.join(checkpoint_dir_local_path, 'last.ckpt')
    trainer = pl.Trainer(logger=logger,
                         callbacks=callbacks + callbacks_distributed(),
                         default_root_dir=path,
                         deterministic=True,
                         progress_bar_refresh_rate=1,
                         **configure_distributed(),
                         resume_from_checkpoint=last_checkpoint_dir if os.path.exists(last_checkpoint_dir) else None)

    # Init model

    model = PlTrimap(lr=args.lr)

    if args.checkpoint_url:
        checkpoint = download_checkpoint(args.checkpoint_url)
        model.model.load_state_dict(checkpoint['state_dict'])

        #if 'optimizer' in checkpoint:
        #    self.optimizer_checkpoint = checkpoint['optimizer']

        print('downloaded checkpoint')

    trainer.fit(model, train_loader, valid_loader)

    print('finished')


if __name__ == '__main__':
    main()
