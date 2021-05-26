import torch.nn as nn

from kaleido.models.mobilenet import MobileNetV2


class Classifier(nn.Module):

    def __init__(self, num_classes):
        super(Classifier, self).__init__()

        self.model = MobileNetV2(num_classes)

    def forward(self, x):
        return self.model(x)
