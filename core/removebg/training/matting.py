import torch

from kaleido.image.gradient import image_gradient
from kaleido.training.helpers import freeze
from kaleido.training.optimizer.radam import RAdam
from kaleido.training.loss.common import distance_loss, laplace_loss, exclusion_loss

from removebg.models.matting import Matting

import pytorch_lightning as pl


class PlMatting(pl.LightningModule):

    @staticmethod
    def add_model_specific_args(parser):
        # Define a group in parser, with same name as current class
        parser.add_argument('--initialize', action='store_true')
        parser.add_argument('--no_weight_transitions', action='store_true')
        parser.add_argument('--freeze_mode', type=str)
        parser.add_argument('--lr', type=float, default=0.00001, help="")

    def __init__(self, config={}):
        super(PlMatting, self).__init__()

        self.freeze_mode = config.get('freeze_mode', None)
        self.weight_transitions = not config.get('no_weight_transitions', False)
        self.lr = config.get('lr', None)

        self.model = Matting(fba_fusion=False, pretrained=config.get('initialize', False))

    def forward(self, *args, **kwargs):
        return self.model(*args, **kwargs)

    def train(self, mode=True):
        super(PlMatting, self).train(mode)

        if mode:
            if self.freeze_mode == 'encoder':
                freeze(self, blacklist=[self.model.encoder])
            elif self.freeze_mode:
                raise NotImplementedError

    def compute_loss(self, image_output, color, trimap2c, alpha_target, fg_target, bg_target):
        only_alpha = fg_target.shape[-1] == 0

        a = alpha_target
        F = fg_target
        B = bg_target

        a_ = image_output[:, 0:1]
        F_ = image_output[:, 1:4]
        B_ = image_output[:, 4:7]

        # compute loss and score

        weight_unknown = 1 - trimap2c[:, 0:1] - trimap2c[:, 1:2]
        weight_alpha = (weight_unknown > 0.01).type(color.type())
        weight_alpha_transitions = weight_alpha * ((a > 0.01) & (a < 0.99)).type(color.type())

        # gradients

        g_a = image_gradient(a)
        g_a_ = image_gradient(a_)

        loss_a_1 = distance_loss(a_, a, weight_alpha if self.weight_transitions else None, loss_type='l1')
        loss_a_g = distance_loss(g_a, g_a_, weight_alpha if self.weight_transitions else None, loss_type='l1')
        loss_a_l = laplace_loss(a_, a, weight_alpha if self.weight_transitions else None, scales=5, loss_type='l1')

        loss = loss_a_1 + loss_a_g + loss_a_l
        loss_valid = loss_a_1

        if not only_alpha:
            g_F_ = image_gradient(F_)
            g_B_ = image_gradient(B_)

            def loss_color(w):
                loss_a_c = distance_loss(a_ * F + (1 - a_) * B, color, w, loss_type='l1')

                # divide by three since the loss was summed over three color channels
                loss_fb_1 = distance_loss(F_, F, w, loss_type='l1') / 3. + distance_loss(B_, B, w, loss_type='l1') / 3.
                loss_fb_c = distance_loss(a * F_ + (1 - a) * B_, color, w, loss_type='l1') / 3.
                loss_fb_e = exclusion_loss(g_F_, g_B_, w)
                loss_fb_l = laplace_loss(F_, F, w, scales=5, loss_type='l1') / 3. + laplace_loss(B_, B, w, scales=5,
                                                                                                 loss_type='l1') / 3.

                loss_fba_c = distance_loss(a_ * F_ + (1 - a_) * B_, color, w, loss_type='l1') / 3.

                return loss_a_c + loss_fb_1 + loss_fb_c + loss_fb_e + loss_fb_l + loss_fba_c

            loss = loss + loss_color(weight_alpha_transitions if self.weight_transitions else None)
            loss_valid = distance_loss(a_ * F_, a * F, weight_alpha_transitions if self.weight_transitions else None, loss_type='l1')

        return loss, loss_valid

    def training_step(self, train_batch, batch_idx):
        color, color_norm, trimap2c, alpha_target, fg_target, bg_target, sample_index = train_batch

        image_output = self.forward(color, color_norm, trimap2c)

        loss, loss_valid = self.compute_loss(image_output, color, trimap2c, alpha_target, fg_target, bg_target)

        self.log("train_loss", loss)

        return loss

    def validation_step(self, val_batch, batch_idx):
        color, color_norm, trimap2c, alpha_target, fg_target, bg_target, sample_index = val_batch

        image_output = self.model(color, color_norm, trimap2c)
        image_output = torch.clamp(image_output, 0, 1)

        loss, loss_valid = self.compute_loss(image_output, color, trimap2c, alpha_target, fg_target, bg_target)

        # log image

        import wandb

        if batch_idx == 0 and wandb.run:

            wandb.log({
                'target alpha': [wandb.Image(image.cpu()) for image in alpha_target],
                'output alpha': [wandb.Image(image.cpu()) for image in image_output[:, 0:1]]
            })

        return {"val_loss": loss_valid}

    def validation_epoch_end(self, outputs):
        avg_loss = torch.stack([x["val_loss"] for x in outputs]).mean()

        self.log("avg_val_loss", avg_loss)
        self.log("avg_val_accuracy", 1. / (avg_loss + 0.00001))

        # needed for tune
        self.log("epoch", torch.tensor(self.current_epoch))

    def configure_optimizers(self):
        return RAdam(self.parameters(), lr=self.lr, betas=(0.9, 0.999), weight_decay=5e-5)
