import torch
import torch.nn as nn
from kaleido.models import ResNet50, ResnetDilated
from kaleido.models.fba.layers_wn import Conv2d as Conv2d_WN
from kaleido.models.fba.models import MattingModule, fba_decoder
from kaleido.training.helpers import set_input_channels


class Matting(nn.Module):
    def __init__(self, fba_fusion=True, pretrained=False):
        super(Matting, self).__init__()

        def norm(dim):
            return nn.GroupNorm(32, dim)

        conv = Conv2d_WN

        net_encoder = ResnetDilated(ResNet50(pretrained=pretrained, conv=conv, norm=norm), dilate_scale=8)
        net_decoder = fba_decoder(
            conv=conv, norm=norm, alpha_sigmoid=False, color_sigmoid=False, fba_fusion=fba_fusion
        )

        self.model = MattingModule(net_encoder, net_decoder)

        set_input_channels(self.model, 5)

    def forward(self, color, color_norm, trimap2c):
        image_output = self.model(color, color_norm, trimap2c)
        image_output = torch.clamp(image_output, 0, 1)

        return image_output
