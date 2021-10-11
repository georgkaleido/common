import pytorch_lightning as pl
import torch
from kaleido.aug import image as aug_img
from kaleido.training.loss.common import cross_entropy_loss
from kaleido.training.optimizer.radam import RAdam
from removebg.models.trimap import Trimap


class PlTrimap(pl.LightningModule):
    def __init__(self, lr=0.00001, **kwargs_model):
        super(PlTrimap, self).__init__()

        self.lr = lr

        self.model = Trimap(**kwargs_model)

    def forward(self, x):
        return self.model(x)

    def accuracy(self, trimap_output, trimap_target, weights):
        num_class = 3

        trimap = torch.argmax(trimap_output, dim=1).unsqueeze(dim=1)
        mask = (trimap_target >= 0) & (trimap_target < num_class)
        mask = mask & (weights > 0)
        label = num_class * trimap_target[mask].long() + trimap[mask]

        cm = torch.bincount(label, None, num_class ** 2).reshape(num_class, num_class).float()
        iou = cm.diag() / (cm.sum(dim=0) + cm.sum(dim=1) - cm.diag())
        miou = iou[~torch.isnan(iou)].mean()

        return miou

    def training_step(self, train_batch, batch_idx):
        image_input, trimap_target, crop_info, sample_index = train_batch

        if image_input.shape[0] == 1:
            raise RuntimeError("batch size 1 is not supported!")

        trimap_output = self.forward(image_input)
        weights = aug_img.Crop.to_weights(trimap_target, crop_info)

        # compute loss and accuracy

        loss = cross_entropy_loss(trimap_output, trimap_target, weights, per_sample=True)
        accuracy = self.accuracy(trimap_output, trimap_target, weights)

        self.log("train_loss", loss.mean())
        self.log("train_accuracy", accuracy)

        # random sampling support for train dataloader
        self.log("train_loss_sample", loss, logger=False)
        self.log("train_indices_sample", sample_index, logger=False)

        return loss.mean()

    def validation_step(self, val_batch, batch_idx):
        image_input, trimap_target, crop_info, sample_index = val_batch

        trimap_output = self.forward(image_input)
        weights = aug_img.Crop.to_weights(trimap_target, crop_info)

        # compute loss and accuracy

        loss = cross_entropy_loss(trimap_output, trimap_target, weights)
        accuracy = self.accuracy(trimap_output, trimap_target, weights)

        # log image

        import wandb

        if batch_idx == 0 and wandb.run:
            trimap_output = trimap_output.argmax(dim=1, keepdim=True).float()

            wandb.log(
                {
                    "input image": [wandb.Image(image.cpu()) for image in image_input],
                    "output trimap": [wandb.Image(image.cpu()) for image in trimap_output],
                    "target trimap": [wandb.Image(image.cpu()) for image in trimap_target],
                }
            )

        return {"val_loss": loss, "val_accuracy": accuracy}

    def validation_epoch_end(self, outputs):
        avg_loss = torch.stack([x["val_loss"] for x in outputs]).mean()
        avg_accuracy = torch.stack([x["val_accuracy"] for x in outputs]).mean()

        self.log("avg_val_loss", avg_loss)
        self.log("avg_val_accuracy", avg_accuracy)

        # needed for tune
        self.log("epoch", torch.tensor(self.current_epoch))

    def configure_optimizers(self):

        return RAdam(self.parameters(), lr=self.lr, betas=(0.9, 0.999), weight_decay=5e-5)
