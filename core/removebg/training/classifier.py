
import torch

from removebg.models.classifier import Classifier

from kaleido.training.loss.common import cross_entropy_loss
from kaleido.training.optimizer.radam import RAdam
from kaleido.tensor.utils import to_numpy

import pytorch_lightning as pl


class PlClassifier(pl.LightningModule):

    def __init__(self, num_classes, lr=0.00001):
        super(PlClassifier, self).__init__()

        self.lr = lr
        self.model = Classifier(num_classes)

    def forward(self, x):
        return self.model(x)

    def training_step(self, train_batch, batch_idx):
        image_input, label_target, sample_index = train_batch

        label_output = self.forward(image_input)

        # compute loss and accuracy

        loss = cross_entropy_loss(label_output, label_target)

        self.log("train_loss", loss)

        return loss

    def validation_step(self, val_batch, batch_idx):
        image_input, label_target, sample_index = val_batch

        label_output = self.forward(image_input)

        # compute loss and accuracy

        loss = cross_entropy_loss(label_output, label_target)

        # log image

        import wandb

        if batch_idx == 0 and wandb.run:

            vis = [wandb.Image(to_numpy(image_input_, rgb2bgr=False, normalize=True), caption=self.to_label(label_output_)) for image_input_, label_output_ in zip(image_input, label_output)]
            wandb.log({"val_visualizations": vis})

        return {"val_loss": loss}

    def validation_epoch_end(self, outputs):
        avg_loss = torch.stack([x["val_loss"] for x in outputs]).mean()

        self.log("avg_val_loss", avg_loss)
        self.log("avg_val_accuracy", 1. / (avg_loss + 0.00001))

        # needed for tune
        self.log("epoch", torch.tensor(self.current_epoch))

    def configure_optimizers(self):
        return RAdam(self.parameters(), lr=self.lr, betas=(0.9, 0.999), weight_decay=5e-5)
