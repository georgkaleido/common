import torch
import os
import math
import torch.nn.functional as F

from removebg.models import Trimap, Matting, Classifier

from kaleido.aug import image as aug_img
from kaleido.aug import mask as aug_mask
from kaleido.alpha.bounding_box import bounding_box
from kaleido.alpha.trimap import force_transitions
from kaleido.image.resize import resize_tensor
from kaleido.models.gaussian import GaussianSmoothing

from ccl import ConnectedComponentsLabeling

# TODO
#from shadowgen.models.oriented_shadow import OrientedShadow


class UnknownForegroundException(Exception):
    """Raised when the foreground is unknown"""
    pass


class Removebg:

    def __init__(self, model_paths, require_models=True, trimap_flip_mean=False):

        self.trimap_flip_mean = trimap_flip_mean

        size_trimap = 513  # size of trimap
        upscale_max = 4  # maximal supported upscale
        self.max_matting_size = size_trimap * upscale_max
        self.max_matting_mp = 4

        self.aug_trimap_scale = aug_img.Scale(size_trimap, random=False, mode='max')
        self.aug_trimap_crop = aug_img.Crop(size_trimap)

        self.aug_trimap2c = aug_mask.TrimapTwoChannel()
        self.aug_trimap_erode = aug_mask.TrimapMorphology(erode_uk_ks=5, dilate_uk_ks=3, opencv_morph=False)

        self.aug_mul_matting = aug_img.SizeToMultiple(mul=8, mode='replicate')
        self.ccl_cuda = ConnectedComponentsLabeling(4)

        self.max_color_mp = 4
        self.aug_color_scale = aug_img.Scale(self.max_color_mp * 1000000, random=False, mode='area', allow_scale_up=False)

        self.aug_shadow_reframe = aug_mask.NormSubjectDeprecated(256, 205, 205)
        self.aug_shadow_gray = aug_img.Grayscale(False)
        self.aug_shadow_bg = aug_mask.ReplaceBackground(modes=['white'])

        self.aug_shadow2_reframe = aug_img.ReFrame(256, border=0.2, noise=0, mode='constant', fill_value=0)
        self.gauss_k = 5
        self.gauss = GaussianSmoothing(1, self.gauss_k, 1.0)

        self.aug_norm = aug_img.Normalize()

        torch.cuda.set_device(0)

        def load_model(model, path, key='state_dict'):
            if not os.path.exists(path):
                error_msg = 'warning! model {} does not exist!'.format(path)

                if require_models:
                    raise RuntimeError(error_msg)
                else:
                    print(error_msg)
            else:
                model.load_state_dict(torch.load(path)[key])

            model.cuda()
            model.half()
            model.eval()

        self.model_trimap = Trimap()
        load_model(self.model_trimap, os.path.join(model_paths, 'trimap513-deeplab-res2net.pth.tar'))

        self.model_matting = Matting()
        load_model(self.model_matting, os.path.join(model_paths, 'matting-fba.pth.tar'))
        self.model_matting.float()

        #self.model_shadow = OrientedShadow()
        #load_model(self.model_shadow, os.path.join(model_paths, 'shadowgen256_car.ckpt'))
        self.mode_shadow = None

    def __call__(self, im, color_enabled=False, shadow_enabled=False, trimap_confidence_thresh=0.5):

        # all operations are done with half precision

        im = im.half()

        with torch.no_grad():

            # unsqueeze

            im = im[None]

            # trimap

            trimap = self.trimap(im, confidence_thresh=trimap_confidence_thresh)

            # alpha

            trimap_scaled = resize_tensor(trimap, 'auto', (im.shape[2], im.shape[3]))
            im_color, im_alpha = self.matting(im, trimap_scaled)

            if color_enabled:
                im = im_color

            # shadow

            if shadow_enabled:
                im, im_alpha = self.shadow(im, im_alpha)

            # return

            return im[0], im_alpha[0]

    def trimap(self, im, confidence_thresh):

        assert(len(im.shape) == 4 and im.shape[0] == 1)

        # rescale and take crop

        im_ds = self.aug_trimap_scale(im[0])['result']
        im_ds, info = self.aug_trimap_crop(im_ds).values()

        im_ds = self.aug_norm(im_ds)['result']
        im_ds = im_ds[None]

        if self.trimap_flip_mean:
            trimap_raw = self.model_trimap(torch.cat((im_ds, torch.flip(im_ds, dims=(3,))), dim=0))
            trimap_raw = F.softmax(.5 * trimap_raw[0:1] + .5 * torch.flip(trimap_raw[1:2], dims=(3, )), dim=1)
        else:
            trimap_raw = self.model_trimap(im_ds)
            trimap_raw = F.softmax(trimap_raw, dim=1)

        trimap_raw = trimap_raw[0]
        trimap_raw = self.aug_trimap_crop.remove_padding(trimap_raw, info)

        # arg max

        trimap = trimap_raw.max(0, keepdim=True)[1]
        trimap = trimap.type(im_ds.type())

        # filter trimap

        if confidence_thresh > 0:

            trimap_mask = (trimap > 0).byte()

            # sanity check

            if not trimap_mask.any():
                raise UnknownForegroundException('only background pixels detected')

            labels, count = self.ccl_cuda(trimap_mask)

            # CCL very rarely returns more labels than the count

            count_labels = int(labels.max() + 1)
            if count_labels != count:
                indices, counts = labels.unique(return_counts=True)
                indices, counts = indices.cpu().numpy(), counts.cpu().numpy()

                print('detected inconsistency in CCL labels. indices: {}, counts: {}, count: {}'.format(indices, counts, count))

                # overwrite
                count = count_labels

            # only if regions are found - this should always be true

            if count > 0:

                trimap_unc = ((trimap_raw[1:2] < 0.25) & (torch.abs(trimap_raw[0:1] - trimap_raw[2:3]) < 0.5))
                trimap_c = (trimap_raw[1:2] > 0.9)

                unc_idx, unc_counts = (trimap_unc * labels).unique(return_counts=True)
                c_idx, c_counts = (trimap_c * labels).unique(return_counts=True)

                uncertain = torch.zeros(int(count), dtype=unc_counts.dtype, device=unc_counts.device)
                certain = torch.zeros(int(count), dtype=c_counts.dtype, device=c_counts.device)

                uncertain = uncertain.index_copy(0, unc_idx.long(), unc_counts).float()
                certain = certain.index_copy(0, c_idx.long(), c_counts).float()

                score = torch.exp(-uncertain / certain)
                score.masked_fill_(torch.isnan(score), 0)

                idx = torch.nonzero(score < confidence_thresh).int()

                mask = torch.zeros((1, labels.shape[-2], labels.shape[-1]), dtype=bool, device=labels.device)
                for idx_ in idx[1:]:
                    mask = mask | (labels == idx_)

                trimap.masked_fill_(mask, 0)
                frac_removed = mask.sum().float() / (labels > 0).sum().float()

                if frac_removed > 0.8:
                    raise UnknownForegroundException('removed {}% of all pixels'.format(frac_removed*100))

        trimap = trimap[None]

        # replace direct transitions from background to foreground

        trimap = force_transitions(trimap)

        # erode / dilate

        trimap = self.aug_trimap_erode(trimap)['result']

        return trimap

    def matting(self, im, trimap):

        # crop image and trimap to bounding box

        im_original = im.clone()

        w_precrop, h_precrop = im.shape[3], im.shape[2]
        bb = bounding_box(trimap.squeeze() > 0)

        if bb[2] < 10 or bb[3] < 10:
            print('Warning: Could not find a matting bounding box: {}x{}. returning empty image.'.format(bb[2], bb[3]))
            return im, torch.zeros_like(trimap)

        im = im[:, :, bb[1]:(bb[1] + bb[3]), bb[0]:(bb[0] + bb[2])]
        trimap = trimap[:, :, bb[1]:(bb[1] + bb[3]), bb[0]:(bb[0] + bb[2])]

        im_original_postcrop = im.clone()

        w, h = im.shape[3], im.shape[2]

        # limit matting scale to max mp and max length

        scale = min(math.sqrt(self.max_matting_mp * 1000000.0 / (w_precrop * h_precrop)), 1.0 * self.max_matting_size / max(w_precrop, h_precrop))
        if scale < 1.0:
            if scale < 0.4:
                print('Warning: scaling image {} down with factor {}'.format((w, h), scale))

            im = resize_tensor(im, 'auto', scale=scale)
            trimap = resize_tensor(trimap, 'auto', scale=scale)

        # trimap to two channels

        trimap2c = self.aug_trimap2c(trimap)['result']

        # normalize color

        im_norm = self.aug_norm(im)['result']

        # cat everything

        input = torch.cat([im, im_norm, trimap2c], dim=1)

        # to multiple of 8

        input, info = self.aug_mul_matting(input).values()

        # to float (because fba doesnt like half)

        input = input.float()

        # to both networks

        matting_output = self.model_matting(input[:, :3], input[:, 3:6], input[:, 6:])

        # back to half

        matting_output = matting_output.half()

        # remove paddings

        matting_output = self.aug_mul_matting.to_original(matting_output, info)
        #matting_output = matting_output[:, :, pad_matting:-pad_matting, pad_matting:-pad_matting]

        # prepare alpha output: interpolate trimap into alpha output

        m1 = 0.1
        m2 = 0.5

        l1 = torch.clamp((trimap - m1) / (m2 - m1), 0, 1)
        l2 = torch.clamp((trimap - (2.0 - m2)) / (m2 - m1), 0, 1)

        matting_output[:, :1] = l1 * matting_output[:, :1] + (1 - l1) * torch.zeros_like(matting_output[:, :1])
        matting_output[:, :1] = (1 - l2) * matting_output[:, :1] + l2 * torch.ones_like(matting_output[:, :1])

        # scale back up

        if scale < 1.0:

            matting_output = resize_tensor(matting_output, 'auto', size=(h, w))
            residual = im_original_postcrop - resize_tensor(im, 'auto', size=(h, w))
            matting_output[:, 1:4] = matting_output[:, 1:4] + residual

        l = ((matting_output[:, :1] > 0) & (matting_output[:, :1] < 1)).type(matting_output.type())
        matting_output[:, 1:4] = l * matting_output[:, 1:4] + (1 - l) * im_original_postcrop

        # uncrop

        matting_output_alpha = F.pad(matting_output[:, :1], (bb[0], w_precrop - (bb[0] + bb[2]), bb[1], h_precrop - (bb[1] + bb[3])), 'constant')
        matting_output_color = im_original
        matting_output_color[..., bb[1]:bb[1]+bb[3], bb[0]:bb[0]+bb[2]] = matting_output[:, 1:4]

        return matting_output_color, matting_output_alpha

    def shadow(self, im, alpha, darkness=0.9):

        # reframe
        im_input = torch.cat((im, alpha), dim=1)
        in_input_ = self.aug_shadow2_reframe(im_input, mask=alpha > 0)
        im_input = in_input_['result']

        # adjust shape and normalize
        im_input[:, :3] *= im_input[:, 3:4] > 0
        im_input[:, :3] = self.aug_norm(im_input[:, :3])['result']

        # forward
        _, shadow = self.model_shadow(im_input, torch.zeros(1, 1, dtype=im.dtype, device=im.device))

        # apply some postprocessing (blur + remap)

        lut = torch.tensor([0, 0.1 * 0.1, 0.2 * 0.5, 0.3 * 0.8, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], dtype=im.dtype, device=im.device)

        shadow = shadow.permute(0, 2, 3, 1)
        shadow = torch.cat((shadow, torch.zeros_like(shadow)), dim=3)
        shadow = torch.nn.functional.grid_sample(lut.view(1, 1, 1, -1), (shadow - .5) * 2., align_corners=True)

        # blur
        shadow = self.gauss(shadow)

        # restore original size
        shadow = self.aug_shadow2_reframe.to_original(shadow[0], in_input_['reframe_info'])[None]

        alpha_new = torch.max(alpha, shadow * darkness)
        im = im * (alpha + (shadow == 0)).clamp(0, 1)

        return im, alpha_new


class Identifier:

    def __init__(self, model_paths, cuda_enabled=True, cpu_cores=None, require_models=True):

        size = 224

        self.aug_scale = aug_img.Scale(size, random=False, mode='max')
        self.aug_crop = aug_img.Crop(size, fill='reflect')
        self.aug_norm = aug_img.Normalize()

        self.cuda_enabled = cuda_enabled

        if cuda_enabled:
            torch.cuda.set_device(0)

        if cpu_cores:
            torch.set_num_threads(cpu_cores)

        self.model = Classifier(9)
        self.labels = ['product',
                       'person',
                       'animal',
                       'car',
                       'car_part',
                       'car_interior',
                       'transportation',
                       'graphic',
                       'other']

        # load weights
        load_args = {}
        if not cuda_enabled:
            load_args['map_location'] = 'cpu'

        path = os.path.join(model_paths, 'identifier-mobilenetv2-c9.pth.tar')

        if not os.path.exists(path):
            error_msg = 'warning! model {} does not exist!'.format(path)

            if require_models:
                raise RuntimeError(error_msg)
            else:
                print(error_msg)
        else:
            self.model.load_state_dict(torch.load(path, **load_args)['state_dict'])

        if cuda_enabled:
            self.model.cuda()
            self.model.half()

        self.model.eval()

    def __call__(self, im):

        # to tensor

        return self.identify(im)

    def to_label(self, pred):
        return self.labels[int(pred.max(0)[1])]

    def identify(self, im):

        # rescale and take crop

        im = self.aug_scale(im)['result']
        im = self.aug_crop(im)['result']
        im = self.aug_norm(im)['result']

        im = im.half()

        with torch.no_grad():
            pred = self.model(im[None])

        label = self.to_label(pred[0])

        return label

