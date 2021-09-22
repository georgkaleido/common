#!/usr/bin/env python

# Standard import
import os
import json
import torch
import multiprocessing
import argparse
import shutil
from urllib.parse import urlparse
from google.cloud import storage
import logging
import glob

import pytorch_lightning as pl
from pytorch_lightning.callbacks import Callback
from pytorch_lightning.loggers import TensorBoardLogger

# Extra imports
from kaleido.training.dataset import Dataset
from kaleido.data.danni.loader import DanniOfflineLoader
from kaleido.training.gce.utilities import configure_cloud_training, configure_best_model_checkpoint_for_cloud_training

# Local imports
from removebg.training.trimap import PlTrimap


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def download_from_bucket(bucket_path, local_path):
    # Strip away quote in path
    o = urlparse(bucket_path)
    if o.scheme == 'gs':
        client = storage.Client()
        bucket_name = o.netloc
        bucket = client.get_bucket(bucket_name)
        blob_path = os.path.join(o.path[1:])
        blob = bucket.blob(blob_path)
        if not blob.exists():
            raise RuntimeError(f"No such file: {bucket_path}")
        logging.info(f"Download from bucket {bucket_path} to {local_path}")
        blob.download_to_filename(local_path)
    else:
        raise RuntimeError(f"bucket_path='{bucket_path}'\nOnly gs:// paths are supported.")


class BestCheckpointNameFixer(Callback):
    def __init__(self, dir_path, base_name="best.ckpt", name_pattern="best-v*.ckpt"):
        super().__init__()

        self.dir_path = dir_path
        self.base_name = base_name
        self.name_pattern = name_pattern

    def on_validation_end(self, trainer, pl_module):
        base_path = os.path.join(self.dir_path, self.base_name)
        if not os.path.exists(base_path):
            return
        # Get mtime of best.ckpt
        base_mtime = os.path.getmtime(base_path)

        # Get list of files matching the name pattern
        for new_path in glob.glob(os.path.join(self.dir_path, self.name_pattern)):
            new_mtime = os.path.getmtime(new_path)
            if new_mtime > base_mtime:
                logging.info(f"Best checkpoint {new_path} is newer than {self.base_name}. Replacing {self.base_name} by {new_path}")
                os.rename(new_path, base_path)
                base_mtime = new_mtime


def main():

    parser = argparse.ArgumentParser(description='Train trimap.')
    parser.add_argument('--name', required=True, type=str, help='name of the run')
    parser.add_argument('--config', required=True, help='path to the training pipeline config.')
    parser.add_argument('--bs', type=int, default=4, help='batch size.')
    parser.add_argument('--lr', type=float, default=0.00001, help='batch size.')
    parser.add_argument('--workers', type=int, help='number of workers.', default=multiprocessing.cpu_count())
    parser.add_argument('--danni_metadata_path', required=True, type=str, help='JSON file with prefetched danni paths.')
    parser.add_argument('--wandb_api_key', type=str, help='wandb api key.')
    parser.add_argument('--checkpoint_url', type=str, help='checkpoint url to start.')
    parser.add_argument('--danni_max_pages', type=int, help='limit pages.')
    parser.add_argument('--fresh', action='store_true', help='removes previous directory with results')
    args = parser.parse_args()

    if not args.wandb_api_key:
        os.environ['WANDB_MODE'] = 'dryrun'
    else:
        os.environ['WANDB_API_KEY'] = args.wandb_api_key

    # Download Danni dataset metadata
    danni_metadata_local_path = os.path.basename(args.danni_metadata_path)
    download_from_bucket(args.danni_metadata_path, danni_metadata_local_path)

    # Initialize Danni loader
    logging.info('Initializing danni loader...')
    loader = DanniOfflineLoader(danni_metadata_local_path, 'danni-data/')

    # set the seed
    pl.seed_everything(42)

    # Initialize Dataloader
    logging.info('Initializing data loaders...')
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
            logging.info(f"Argument --fresh was passed: Erasing previous checkpoint in {path}")
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

    # Callback to ensure the best checkpoint is always called best.cpkt, and not best-v1.ckpt, best-v2.ckpt etc.
    callbacks.append(BestCheckpointNameFixer(checkpoint_dir_local_path))

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
    configure_cloud_training(checkpoint_dir_local_path, callbacks, 'trimap-qi-auto', args.name,
                             bucket_category="removebg",
                             checkpoint_names=["best.ckpt", "last.ckpt"])

    # Create trainer
    last_checkpoint_path = os.path.join(checkpoint_dir_local_path, 'last.ckpt')
    trainer = pl.Trainer(logger=logger,
                         callbacks=callbacks,
                         default_root_dir=path,
                         deterministic=True,
                         progress_bar_refresh_rate=1,
                         gpus=-1,
                         # max_epochs=20,
                         precision=16,
                         resume_from_checkpoint=last_checkpoint_path if os.path.exists(last_checkpoint_path) else None)

    # Init model
    trimap_model = PlTrimap(lr=args.lr)

    if not os.path.exists(last_checkpoint_path) and args.checkpoint_url:
        checkpoint_local_path = os.path.basename(args.checkpoint_url)
        download_from_bucket(args.checkpoint_url, checkpoint_local_path)
        checkpoint = torch.load(checkpoint_local_path)
        trimap_model.model.load_state_dict(checkpoint['state_dict'])

    trainer.fit(trimap_model, train_loader, valid_loader)

    print('finished')


if __name__ == '__main__':
    main()
