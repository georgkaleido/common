#!/usr/bin/env python

# Standard import
import os
import json
import torch
import multiprocessing
import argparse
import shutil

from removebg.training.trimap import PlTrimap
from kaleido.training.dataset import Dataset
from kaleido.data.danni.loader import DanniLoader, DanniOfflineLoader

# Extra imports
import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger

from kaleido.training.helpers import download_checkpoint
from kaleido.training.gce.utilities import configure_cloud_training, configure_best_model_checkpoint_for_cloud_training


def main():

    parser = argparse.ArgumentParser(description='Train trimap.')
    parser.add_argument('--name', required=True, type=str, help='name of the run')
    parser.add_argument('--config', required=True, help='path to the training pipeline config.')
    parser.add_argument('--bs', type=int, default=4, help='batch size.')
    parser.add_argument('--lr', type=float, default=0.00001, help='batch size.')
    parser.add_argument('--workers', type=int, help='number of workers.', default=multiprocessing.cpu_count())
    parser.add_argument('--danni_user', required=False, type=str, help='danni user.')
    parser.add_argument('--danni_token', required=False, type=str, help='danni password.')
    parser.add_argument('--danni_metadata_path', required=False, type=str, help='JSON file with prefetched danni paths.')
    parser.add_argument('--wandb_api_key', type=str, help='wandb api key.')
    parser.add_argument('--checkpoint_url', type=str, help='checkpoint url to start.')
    parser.add_argument('--danni_max_pages', type=int, help='limit pages.')
    parser.add_argument('--fresh', action='store_true', help='removes previous directory with results')
    args = parser.parse_args()

    if not (args.danni_user and args.danni_token) and not args.danni_metadata_path:
        parser.error("Either --danni_user and --danni_token, or --danni_metadata_path is required.")
    if args.danni_user and args.danni_token and args.danni_metadata_path:
        parser.error("The argument --danni_metadata_path and the two arguments --danni_user and --danni_token are mutually exclusive.")

    if not args.wandb_api_key:
        os.environ['WANDB_MODE'] = 'dryrun'
    else:
        os.environ['WANDB_API_KEY'] = args.wandb_api_key

    print('initializing danni loader...')
    if args.danni_user is not None:

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
            im_alpha_url = d.get('image', {}).get('remove_background', {}).get('alpha', [{}])[0].get('file300k', {}).get('url')

            if not im_color_url or not im_alpha_url:
                return None

            return [im_color_url, im_alpha_url]

        loader = DanniLoader(filter_, fields, result_fn, result_fn_names, mode='load', root='danni-data/', limit=1000, max_pages=args.danni_max_pages)
    else:
        loader = DanniOfflineLoader(args.danni_metadata_path, 'danni-data/')

    # set the seed

    pl.seed_everything(42)

    # Initialize Dataloader

    print('initializing data loaders...')
    with open(args.config, 'r') as f:
        config = json.load(f)

    train_dataset = Dataset('danni-data/', config, is_train=True, report_augmentation_timings=False, pre_load_callback=loader.pre_load_callback)
    valid_dataset = Dataset('danni-data/', config, is_train=False, report_augmentation_timings=False, pre_load_callback=loader.pre_load_callback)

    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=args.bs, shuffle=True, num_workers=args.workers, drop_last=True)
    valid_loader = torch.utils.data.DataLoader(valid_dataset, batch_size=8, shuffle=False, num_workers=args.workers)

    # Setup logger

    path = f'results_{args.name}/'

    # If fresh is passed, delete previous checkpoints
    if args.fresh:
        if os.path.exists(path):
            print(f"Argument --fresh was passed: Erasing previous checkpoint in {path}")
            if '/' == path:
                raise Exception(f"The script was about to delete '/'.")
            elif '*' in path:
                raise Exception(f"The script was about to delete a path with a wildcard, this is unsafe.")
            else:
                shutil.rmtree(path)

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

    # Checkpoints creation
    model_checkppint_callback = pl.callbacks.ModelCheckpoint(
            save_last=True,
            save_top_k=1,
            dirpath=checkpoint_dir_local_path,
            filename='best',
            verbose=True,
            monitor='avg_val_accuracy',
            mode='max'
        )

    best_model_checkpoint_path = os.path.join(checkpoint_dir_local_path, "best.ckpt")
    configure_best_model_checkpoint_for_cloud_training(best_model_checkpoint_path, model_checkppint_callback)
    callbacks.append(model_checkppint_callback)

    # Progress bar
    callbacks.append(pl.callbacks.ProgressBar(5, 0))

    # Configure cloud training on GCP -> Checkpoint synchronization on bucket
    configure_cloud_training(checkpoint_dir_local_path, callbacks, 'removebg', args.name, bucket_category="torchelastic", checkpoint_names=["last.ckpt", "best.ckpt"])

    # Create trainer
    last_checkpoint_dir = os.path.join(checkpoint_dir_local_path, 'last.ckpt')
    trainer = pl.Trainer(logger=logger,
                         callbacks=callbacks,
                         default_root_dir=path,
                         deterministic=True,
                         progress_bar_refresh_rate=1,
                         gpus=-1,
                         # max_epochs=20,
                         precision=16,
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
