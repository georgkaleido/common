import torch.nn as nn
from kaleido.models import DeepLab


class Trimap(nn.Module):
    def __init__(self, encoder="res2net101", aspp=True, output_stride=16, pretrained=False):
        super(Trimap, self).__init__()

        self.model = DeepLab(
            encoder_name=encoder,
            num_classes=3,
            multi_grid=True,
            aspp=aspp,
            pretrained=pretrained,
            output_stride=output_stride,
        )

    def forward(self, x):
        return self.model(x)
