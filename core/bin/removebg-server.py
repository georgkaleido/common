#!/usr/bin/env python

import pika
import time
import os
import math
import msgpack
import multiprocessing
import numpy as np
import traceback

from kaleido.tensor.utils import to_numpy, to_tensor
from removebg.image import SmartAlphaImage, CouldNotReadImage
from removebg.removebg import UnknownForegroundException

workers = multiprocessing.cpu_count()
queue_in = multiprocessing.Queue(workers)
shared_data_manager = multiprocessing.Manager()
initializing = multiprocessing.Value('i', 1)


class ExtractorError(Exception):
    """Raised when the extractor class returns an error"""
    pass


def callback(ch, method, props, body):
    # try to read the body

    def rep(obj):
        body = msgpack.packb(obj)

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id, delivery_mode=2),
                         body=body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    obj_in = msgpack.unpackb(body)
    obj_out = {b'status': 'ok',
               b'description': '',
               b'data': bytes(),
               b'width': 0,
               b'height': 0,
               b'maxwidth': 0,
               b'maxheight': 0,
               b'width_hd': 0,
               b'height_hd': 0,
               b'width_medium': 0,
               b'height_medium': 0,
               b'version': 1.0,
               b'format': 'png'}

    # parse command
    command = obj_in[b'command']
    if command == b'health':
        obj_out['status'] = 'initializing' if initializing.value == 1 else 'ok'
        rep(obj_out)

        return

    # continue with removebg

    im_bytes = obj_in[b'data']
    megapixels = obj_in[b'megapixels']
    only_alpha = obj_in.get(b'channels', b'rgba') == b'alpha'
    api_type = obj_in.get(b'type', b'auto')
    format = obj_in.get(b'format', b'auto').decode('utf-8')
    bg_color = obj_in.get(b'bg_color', [255, 255, 255, 0])
    im_bytes_bg = obj_in.get(b'bg_image', None)
    scale_param = obj_in.get(b'scale', None)
    position_param = obj_in.get(b'position', None)
    crop = obj_in.get(b'crop', False)
    crop_margin = obj_in.get(b'crop_margin', None)
    roi = obj_in.get(b'roi', None)
    shadow = obj_in.get(b'shadow', False)
    semitransparency = obj_in.get(b'semitransparency', True)

    times = []
    t = time.time()

    try:
        image = SmartAlphaImage(im_bytes, megapixel_limit=megapixels)
        image_bg = None

        if im_bytes_bg is not None:
            image_bg = SmartAlphaImage(im_bytes_bg, megapixel_limit=megapixels)

        if image.signal_beacon():
            print('[{}] {}'.format(props.correlation_id, 'SIGNAL BEACON DETECTED'))

        times.append(time.time() - t)
        print('[{}] {:10} ({:.2f}s) | megapixels: {}, mode: {}, dpi: {}, icc: {}, has alpha: {}, exif: {}'.format(
            props.correlation_id, 'decoding', times[-1], megapixels, image.mode_original, image.dpi,
            'yes' if image.icc else 'no', 'yes' if image.im_alpha is not None is not None else 'no',
            'none' if image.exif_rot is None else image.exif_rot))
        t = time.time()

        # crop to roi

        crop_roi = None

        if roi:
            x0 = min(roi[0], roi[2])
            x1 = max(roi[0], roi[2])
            y0 = min(roi[1], roi[3])
            y1 = max(roi[1], roi[3])

            w = int((x1 - x0 + 1) * image.scale_pre_mplimit)
            h = int((y1 - y0 + 1) * image.scale_pre_mplimit)
            x0 = int(x0 * image.scale_pre_mplimit)
            y0 = int(y0 * image.scale_pre_mplimit)

            crop_roi = [x0, y0, w, h]

        im_cv = image.get('bgr', crop=crop_roi)

        # check min size

        s = 224. / max(im_cv.shape[0], im_cv.shape[1])
        if s * im_cv.shape[0] < 5 or s * im_cv.shape[1] < 5:
            raise UnknownForegroundException('image size too small: {}'.format(im_cv.shape))

        times.append(time.time() - t)
        print('[{}] {:10} ({:.2f}s) | {}x{} -> {}x{} (crop: {})'.format(props.correlation_id, 'preproc', times[-1],
                                                                        image.width, image.height, im_cv.shape[1],
                                                                        im_cv.shape[0], crop))

        shared_data = shared_data_manager.dict()
        shared_data['finished'] = False
        shared_data['data'] = None
        shared_data['error'] = None
        shared_data['error_fg'] = None
        shared_data['api'] = None
        shared_data['time'] = None
        queue_in.put((im_cv, shared_data, api_type.decode('utf-8'), shadow, props.correlation_id))

        while not shared_data['finished']:
            time.sleep(0.01)

        im_res = shared_data['data']

        if shared_data['error']:
            raise ExtractorError(shared_data['error'])

        if shared_data['error_fg']:
            raise UnknownForegroundException()

        times.append(shared_data['time'])
        print('[{}] {:10} ({:.2f}s) | class: {}'.format(props.correlation_id, 'processing', times[-1],
                                                        shared_data['api']))

        # postprocessing

        t = time.time()

        # uncrop and set result

        im_rgb_precolorcorr = image.get('rgb')
        image.set(im_res, 'bgra', limit_alpha=True, crop=crop_roi)

        # car windows

        if shared_data['api'] == 'car':
            image.fill_holes(200 if semitransparency else 255, mode='car', average=semitransparency,
                             im_rgb_precolorcorr=im_rgb_precolorcorr)

        elif shared_data['api'] == 'car_interior':
            image.fill_holes(200 if semitransparency else 0, mode='all', average=True,
                             im_rgb_precolorcorr=im_rgb_precolorcorr)

        # crop to subject

        if crop:

            kwargs = {}
            if crop_margin:
                kwargs['margins'] = [crop_margin[b'top'], crop_margin[b'right'], crop_margin[b'bottom'],
                                     crop_margin[b'left']]
                kwargs['absolutes'] = [not crop_margin[b'top_relative'], not crop_margin[b'right_relative'],
                                       not crop_margin[b'bottom_relative'], not crop_margin[b'left_relative']]
                kwargs['clamp'] = 500

            image.postproc_fn('crop_subject', **kwargs)

        # scale

        if scale_param:
            image.postproc_fn('scale_subject', scale_new=scale_param / 100.)

        # position

        if position_param:
            image.postproc_fn('position_subject', dx=position_param[b'x'] / 100., dy=position_param[b'y'] / 100.)

        # fill bg color or background

        if format == 'jpg':
            bg_color[3] = 255

        if image_bg is not None:
            image.underlay_background(image_bg)
        elif bg_color[3] > 0:
            image.underlay_background(bg_color)

        times.append(time.time() - t)
        print('[{}] {:10} ({:.2f}s) | bg_color: {}, shadow: {}'.format(props.correlation_id, 'postproc', times[-1],
                                                                       bg_color, 'yes' if shadow else 'no'))
        t = time.time()

        # encoding

        if format == 'zip':
            res = image.encode('zip')
            obj_out['format'] = 'zip'

        else:
            if only_alpha:
                if format == 'jpg' or format == 'auto':
                    res = image.encode('jpg_alpha')
                    obj_out['format'] = 'jpg'

                else:
                    res = image.encode('png_alpha')
                    obj_out['format'] = 'png'
            else:
                if format == 'png' or (format == 'auto' and image.has_transparency()):
                    res = image.encode('png')
                    obj_out['format'] = 'png'

                else:
                    res = image.encode('jpg')
                    obj_out['format'] = 'jpg'

        obj_out['type'] = shared_data['api']

        obj_out['data'] = res
        obj_out['width'] = image.width
        obj_out['height'] = image.height
        obj_out['width_uncropped'] = image.width_original
        obj_out['height_uncropped'] = image.height_original

        scale = math.sqrt(1500000.0 / (image.width_pre_mplimit * image.height_pre_mplimit))
        obj_out['width_medium'] = min(int(scale * image.width_pre_mplimit), image.width_pre_mplimit)
        obj_out['height_medium'] = min(int(scale * image.height_pre_mplimit), image.height_pre_mplimit)

        scale = math.sqrt(4000000.0 / (image.width_pre_mplimit * image.height_pre_mplimit))
        obj_out['width_hd'] = min(int(scale * image.width_pre_mplimit), image.width_pre_mplimit)
        obj_out['height_hd'] = min(int(scale * image.height_pre_mplimit), image.height_pre_mplimit)

        scale = math.sqrt(25000000.0 / (image.width_pre_mplimit * image.height_pre_mplimit))
        obj_out['maxwidth'] = min(int(scale * image.width_pre_mplimit), image.width_pre_mplimit)
        obj_out['maxheight'] = min(int(scale * image.height_pre_mplimit), image.height_pre_mplimit)

        times.append(time.time() - t)
        print('[{}] {:10} ({:.2f}s) | format: {}, overall {:.2f}s'.format(props.correlation_id, 'encoding', times[-1],
                                                                          str(obj_out['format']), sum(times)))
    except CouldNotReadImage as e:
        print('[{}] error: could not read image: {}'.format(props.correlation_id, e))

        obj_out['status'] = 'error'
        obj_out['description'] = 'failed_to_read_image'

    except UnknownForegroundException:
        print('[{}] error: could not identify foreground'.format(props.correlation_id))

        obj_out['status'] = 'error'
        obj_out['description'] = 'unknown_foreground'

    except ExtractorError as e:
        print('[{}] error:  got error from extractor: {}'.format(props.correlation_id, e))

        obj_out['status'] = 'error'
        obj_out['description'] = 'unknown_error'

    except Exception as e:
        print('[{}] error: got unknown exception: {}'.format(props.correlation_id, e))
        traceback.print_exc()

        obj_out['status'] = 'error'
        obj_out['description'] = 'unknown_error'

    rep(obj_out)


def worker():
    print('Initializing rabbitmq connection. host "{}", port "{}", queue "{}"'.format(os.environ['RABBITMQ_HOST'],
                                                                                      os.environ['RABBITMQ_PORT'],
                                                                                      os.environ['REQUEST_QUEUE']))

    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(os.environ['RABBITMQ_HOST'], os.environ['RABBITMQ_PORT'], '/',
                                      pika.PlainCredentials(os.environ['RABBITMQ_USER'],
                                                            os.environ['RABBITMQ_PASSWORD'])))
        channel = connection.channel()
        channel.queue_declare(queue=os.environ['REQUEST_QUEUE'], durable=True)
        channel.basic_qos(prefetch_count=1)  # fair dispatch

        channel.basic_consume(queue=os.environ['REQUEST_QUEUE'], on_message_callback=callback)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except Exception as e:
        print('got an error creating rabbitmq connection: {}'.format(e))
        traceback.print_exc()


def main():

    assert('REQUEST_QUEUE' in os.environ)
    assert('RABBITMQ_HOST' in os.environ)
    assert('RABBITMQ_PORT' in os.environ)
    assert('RABBITMQ_USER' in os.environ)
    assert('RABBITMQ_PASSWORD' in os.environ)

    print('Starting up...')

    if os.environ.get('MOCK_RESPONSE', '0') == '0':
        print('initializing extractor...')

        from removebg.removebg import Removebg, Identifier

        require_models = os.environ.get('REQUIRE_MODELS', '1') == '1'

        removebg = Removebg('networks-trained/', require_models=require_models, trimap_flip_mean=True)
        identifier = Identifier('networks-trained/', require_models=require_models)

    print('starting workers...')

    time.sleep(5)
    pool = multiprocessing.Pool(processes=workers)
    for i in range(workers):
        pool.apply_async(worker)

    print('finished startup')

    # create startup completed file
    with open('startup-completed', 'w+') as f:
        pass

    initializing.value = 0
    error_count = 0

    fname_processing = 'currently_processing'

    while True:
        im, d, api, shadow, correlation_id = queue_in.get()

        # create processing file
        with open(fname_processing, 'w+') as f:
            pass

        t = time.time()

        try:
            d['data'] = None
            d['api'] = api

            if os.environ.get('MOCK_RESPONSE', '0') != '0':
                d['data'] = np.dstack((im,  np.ones_like(im[:, :, 0]) * 128))
                d['api'] = 'mock'
            else:
                # transfer to gpu

                im_tr = to_tensor(im, bgr2rgb=True)

                # overwrite if auto
                if d['api'] == 'auto':
                    d['api'] = identifier(im_tr)

                # be stricter with previews. this way (hopefully) no preview gets accepted while the highres gets rejected.
                trimap_confidence_thresh = 0.25 if im_tr.shape[-1] * im_tr.shape[-2] < 250000 else 0.15

                # extract background
                im_tr_rgb, im_tr_alpha = removebg(im_tr, color_enabled=(d['api'] == 'person' or d['api'] == 'animal'), shadow_enabled=(d['api'] == 'car' and shadow), trimap_confidence_thresh=trimap_confidence_thresh)

                im_rgb = to_numpy(im_tr_rgb, rgb2bgr=True)
                im_alpha = to_numpy(im_tr_alpha)

                d['data'] = np.dstack((im_rgb, np.expand_dims(im_alpha, axis=2)))

                # reset cuda errors
                error_count = 0

        except UnknownForegroundException as e:
            print('[{}] could not detect foreground: {}'.format(correlation_id, e))
            d['error_fg'] = True

        except Exception as e:
            print('[{}] there occured an error during the extraction: {}'.format(correlation_id, e))
            traceback.print_exc()

            d['error'] = str(e)

            # count errors to detect unhealty state
            error_count += 1

            # more than 10 errors in a row - kill application
            if error_count >= 10:
                exit('close due to unhealthy state')

        # remove processing file (if there is any)
        try:
            os.remove(fname_processing)
        except Exception as e:
            print('[{}] could not remove processing file! {}'.format(correlation_id, e))
            traceback.print_exc()

        d['time'] = time.time() - t
        d['finished'] = True


if __name__ == "__main__":
    # execute only if run as a script
    main()
