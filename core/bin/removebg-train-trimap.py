#!/usr/bin/env python

# Standard import
import os
import json
import time
import torch
import copy
import multiprocessing

from removebg.training.trimap import PlTrimap
from kaleido.training.dataset import Dataset
from kaleido.data.danni.loader import DanniLoader

# Extra imports
import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Train trimap.')
    parser.add_argument('--config', required=True, help='path to the training pipeline config.')
    parser.add_argument('--bs', type=int, default=4, help='batch size.')
    parser.add_argument('--path', type=str, help='results directory. default results_<timestamp>', default='results_{}'.format(time.time()))
    parser.add_argument('--workers', type=int, help='number of workers.', default=multiprocessing.cpu_count())
    args = parser.parse_args()

    os.environ['WANDB_API_KEY'] = 'asdf'
    os.environ['WANDB_MODE'] = 'dryrun'

    os.environ['DANNI_HOST'] = 'https://danni.kaleido.ai/'
    os.environ['DANNI_USER'] = 'david.fankhauser'
    os.environ['DANNI_TOKEN'] = '7rbnKHj02KFH4qF0tTanRUTC'

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
    loader = DanniLoader('danni-data/', filter_, fields, result_fn, result_fn_names, limit=1000)

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

    os.makedirs(args.path, exist_ok=True)

    logger = pl.loggers.WandbLogger(
        name='',
        project='trimap',
        save_dir=args.path,
        offline=False
    )

    logger_dir = logger.save_dir

    # Define callbacks

    callbacks = []

    callbacks.append(
        pl.callbacks.ModelCheckpoint(
            save_last=True,
            save_top_k=1,
            dirpath=os.path.join(logger_dir, 'checkpoints'),
            filename='best-{epoch:04d}-{avg_val_loss:.5f}',
            verbose=True,
            monitor='avg_val_accuracy',
            mode='max'
        )
    )

    # Create trainer

    last_checkpoint_dir = os.path.join(logger_dir, 'checkpoints', 'last.ckpt')
    trainer = pl.Trainer(logger=logger,
                         callbacks=callbacks,
                         default_root_dir=args.path,
                         checkpoint_callback=True,
                         gpus=1,
                         deterministic=True,
                         #overfit_batches=5,
                         resume_from_checkpoint=last_checkpoint_dir if os.path.exists(last_checkpoint_dir) else None)

    # Init model

    model = PlTrimap()

    trainer.fit(model, train_loader, valid_loader)

    print('finished')


if __name__ == '__main__':
    main()
