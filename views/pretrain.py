import os

import six
from PIL import Image
import matplotlib.pyplot as plt
from transformers import DetrFeatureExtractor, DetrForObjectDetection
import torch
import torchvision.transforms as transforms
import json
torch.set_grad_enabled(False)
from PIL import Image
import requests
import io
import math
import matplotlib.pyplot as plt
import torch
from torch import nn
from torchvision.models import resnet50
import torchvision.transforms as T
import numpy
torch.set_grad_enabled(False)
import panopticapi
import itertools
import seaborn as sns
from panopticapi.utils import id2rgb, rgb2id
# classes
def pretrain_label(im,number):
    buf = six.BytesIO()  # 获取指针（地址）对象
    buf.write(im)  # 指针对象写入数据
    buf.seek(0)
    im = Image.open(buf).convert('RGB')
    print(im)
    CLASSES = [
        'N/A', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
        'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A',
        'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse',
        'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack',
        'umbrella', 'N/A', 'N/A', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis',
        'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
        'skateboard', 'surfboard', 'tennis racket', 'bottle', 'N/A', 'wine glass',
        'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich',
        'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
        'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table', 'N/A',
        'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard',
        'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A',
        'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
        'toothbrush'
    ]

    # colors for visualization
    COLORS = [[0.000, 0.447, 0.741], [0.850, 0.325, 0.098], [0.929, 0.694, 0.125],
              [0.494, 0.184, 0.556], [0.466, 0.674, 0.188], [0.301, 0.745, 0.933]]

    feature_extractor = DetrFeatureExtractor.from_pretrained('facebook/detr-resnet-50')
    # standard PyTorch mean-std input image normalization
    transform = T.Compose([
        T.Resize(800),
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # for output bounding box post-processing
    def box_cxcywh_to_xyxy(x):
        x_c, y_c, w, h = x.unbind(1)
        b = [(x_c - 0.5 * w), (y_c - 0.5 * h),
             (x_c + 0.5 * w), (y_c + 0.5 * h)]
        return torch.stack(b, dim=1)

    def rescale_bboxes(out_bbox, size):
        img_w, img_h = size
        b = box_cxcywh_to_xyxy(out_bbox)
        b = b * torch.tensor([img_w, img_h, img_w, img_h], dtype=torch.float32)
        return b


    def detect(im, model, transform):
        # mean-std normalize the input image (batch-size: 1)
        img = transform(im).unsqueeze(0)
        outputs = model(img)
        probas = outputs['logits'].softmax(-1)[0, :, :-1]
        keep = probas.max(-1).values > 0.7
        bboxes_scaled = rescale_bboxes(outputs['pred_boxes'][0, keep], im.size)
        return probas[keep], bboxes_scaled

    #url = 'http://images.cocodataset.org/val2017/000000125062.jpg'
    #im = Image.open(requests.get(url, stream=True).raw)
    #im = Image.open('image/residential/1.png')
    #im = Image.open('125062.jpg')
    pic_area=im.size[0]*im.size[1]
    #print(pic_area)

    def overlap(x1, y1, x2, y2, x3, y3, x4, y4):
        s1=[x1, y1, x2, y2]
        s2=[x3, y3, x4, y4]
        if s1[0] > s1[2]:
            s1[0], s1[2] = s1[2], s1[0]
        if s1[1] > s1[3]:
            s1[1], s1[3] = s1[3], s1[1]
        if s2[0] > s2[2]:
            s2[0], s2[2] = s2[2], s2[0]
        if s2[1] > s2[3]:
            s2[1], s2[3] = s2[3], s2[1]
        temp_x1 = max(s1[0], s2[0])
        temp_x2 = min(s1[2], s2[2])
        temp_y1 = max(s1[1], s2[1])
        temp_y2 = min(s1[3], s2[3])
        if temp_x2 - temp_x1 < 0 or temp_y2 - temp_y1 < 0:
            res = 0
        else:
            res = (temp_y2 - temp_y1) * (temp_x2 - temp_x1)
        return(res)

    def plot_results(prob, boxes,data):
        sum = 0
        for p, (xmin, ymin, xmax, ymax) in zip(prob, boxes.tolist()):
            record[sum].append(xmin)
            record[sum].append(ymin)
            record[sum].append(xmax)
            record[sum].append(ymax)
            cl = p.argmax()
            data['object_detect']['object'][str(sum)] = {}
            data['object_detect']['object'][str(sum)]['coordinate']=record[sum]
            data['object_detect']['object'][str(sum)]['name'] = CLASSES[cl]
            data['object_detect']['object'][str(sum)]['prob'] = float(p[cl])
            sum = sum + 1
        return(record,sum,data)

    record=[]
    for i in range(50):
        record.append([])
    model = DetrForObjectDetection.from_pretrained('facebook/detr-resnet-50')

    scores, boxes = detect(im, model, transform)
    data = {
        "imageId": number,
        "object_detect":{
            "object": {},
            "overlap": {}
        },
        "panoptic_segmentation":{},
    }

    def segmentation(im,data):
        # Detectron2 uses a different numbering scheme, we build a conversion table
        coco2d2 = {}
        count = 0
        for i, c in enumerate(CLASSES):
            if c != "N/A":
                coco2d2[i] = count
                count += 1

        model, postprocessor = torch.hub.load('facebookresearch/detr', 'detr_resnet101_panoptic', pretrained=True,
                                              return_postprocessor=True, num_classes=250)
        model.eval()
        img = transform(im).unsqueeze(0)
        out = model(img)
        scores = out["pred_logits"].softmax(-1)[..., :-1].max(-1)[0]
        keep = scores > 0.85
        ncols = 5
        fig, axs = plt.subplots(ncols=ncols, nrows=math.ceil(keep.sum().item() / ncols), figsize=(18, 10))
        try:
            for line in axs:
                for a in line:
                    a.axis('off')
            for i, mask in enumerate(out["pred_masks"][keep]):
                ax = axs[i // ncols, i % ncols]
                ax.imshow(mask, cmap="cividis")
                ax.axis('off')
            fig.tight_layout()
            # the post-processor expects as input the target size of the predictions (which we set here to the image size)
            result = postprocessor(out, torch.as_tensor(img.shape[-2:]).unsqueeze(0))[0]
            print("-----segmentation--------")


            import itertools
            import seaborn as sns
            palette = itertools.cycle(sns.color_palette())

            # The segmentation is stored in a special-format png
            panoptic_seg = Image.open(io.BytesIO(result['png_string']))
            panoptic_seg = numpy.array(panoptic_seg, dtype=numpy.uint8).copy()
            # We retrieve the ids corresponding to each mask
            panoptic_seg_id = rgb2id(panoptic_seg)


            from detectron2.config import get_cfg
            from detectron2.utils.visualizer import Visualizer
            from detectron2.data import MetadataCatalog
            # from google.colab.patches import cv2_imshow
            from copy import deepcopy
            import cv2
            # We extract the segments info and the panoptic result from DETR's prediction
            segments_info = deepcopy(result["segments_info"])
            meta = MetadataCatalog.get("coco_2017_val_panoptic_separated")
            stuff_classes = ['things', 'banner', 'blanket', 'bridge', 'cardboard', 'counter', 'curtain', 'door-stuff',
                             'floor-wood', 'flower', 'fruit', 'gravel', 'house', 'light', 'mirror-stuff', 'net', 'pillow',
                             'platform', 'playingfield', 'railroad', 'river', 'road', 'roof', 'sand', 'sea', 'shelf',
                             'snow',
                             'stairs', 'tent', 'towel', 'wall-brick', 'wall-stone', 'wall-tile', 'wall-wood', 'water',
                             'window-blind', 'window', 'tree', 'fence', 'ceiling', 'sky', 'cabinet', 'table', 'floor',
                             'pavement', 'mountain', 'grass', 'dirt', 'paper', 'food', 'building', 'rock', 'wall', 'rug']
            total=0
            for i in range(len(segments_info)):
                c = segments_info[i]["category_id"]
                # print(c)
                if segments_info[i]["isthing"]:
                    segments_info[i]["category_id"] = meta.thing_dataset_id_to_contiguous_id[c]
                else:
                    segments_info[i]["category_id"] = meta.stuff_dataset_id_to_contiguous_id[c]
                    data['panoptic_segmentation'][str(total)] = {}
                    data['panoptic_segmentation'][str(total)]['name'] = stuff_classes[segments_info[i]["category_id"]]
                    data['panoptic_segmentation'][str(total)]['area'] = segments_info[i]["area"]
                    total=total+1
        except:
            for line in axs:
                line.axis('off')
            for i, mask in enumerate(out["pred_masks"][keep]):
                print(axs)
                ax = axs[i]
                ax.imshow(mask, cmap="cividis")
                ax.axis('off')
            #plt.show()

            # the post-processor expects as input the target size of the predictions (which we set here to the image size)
            result = postprocessor(out, torch.as_tensor(img.shape[-2:]).unsqueeze(0))[0]
            print("-----segmentation--------")
            print(result)
            print("result")

            import itertools
            import seaborn as sns

            palette = itertools.cycle(sns.color_palette())

            # The segmentation is stored in a special-format png
            panoptic_seg = Image.open(io.BytesIO(result['png_string']))
            # print(result['png_string'])
            panoptic_seg = numpy.array(panoptic_seg, dtype=numpy.uint8).copy()
            # We retrieve the ids corresponding to each mask
            panoptic_seg_id = rgb2id(panoptic_seg)
            # print(panoptic_seg_id)
            # Finally we color each mask individually
            panoptic_seg[:, :, :] = 0
            for id in range(panoptic_seg_id.max() + 1):
                panoptic_seg[panoptic_seg_id == id] = numpy.asarray(next(palette)) * 255
            plt.figure(figsize=(15, 15))
            plt.imshow(panoptic_seg)
            plt.axis('off')
            plt.show()

            from detectron2.config import get_cfg
            from detectron2.utils.visualizer import Visualizer
            from detectron2.data import MetadataCatalog
            # from google.colab.patches import cv2_imshow
            from copy import deepcopy
            import cv2

            # We extract the segments info and the panoptic result from DETR's prediction
            segments_info = deepcopy(result["segments_info"])
            # Panoptic predictions are stored in a special format png
            panoptic_seg = Image.open(io.BytesIO(result['png_string']))
            final_w, final_h = panoptic_seg.size
            # We convert the png into an segment id map
            panoptic_seg = numpy.array(panoptic_seg, dtype=numpy.uint8)
            panoptic_seg = torch.from_numpy(rgb2id(panoptic_seg))
            # Detectron2 uses a different numbering of coco classes, here we convert the class ids accordingly
            meta = MetadataCatalog.get("coco_2017_val_panoptic_separated")
            print("1")
            stuff_classes = ['things', 'banner', 'blanket', 'bridge', 'cardboard', 'counter', 'curtain', 'door-stuff',
                             'floor-wood', 'flower', 'fruit', 'gravel', 'house', 'light', 'mirror-stuff', 'net', 'pillow',
                             'platform', 'playingfield', 'railroad', 'river', 'road', 'roof', 'sand', 'sea', 'shelf',
                             'snow',
                             'stairs', 'tent', 'towel', 'wall-brick', 'wall-stone', 'wall-tile', 'wall-wood', 'water',
                             'window-blind', 'window', 'tree', 'fence', 'ceiling', 'sky', 'cabinet', 'table', 'floor',
                             'pavement', 'mountain', 'grass', 'dirt', 'paper', 'food', 'building', 'rock', 'wall', 'rug']
            total=0
            for i in range(len(segments_info)):
                c = segments_info[i]["category_id"]
                # print(c)
                if segments_info[i]["isthing"]:
                    segments_info[i]["category_id"] = meta.thing_dataset_id_to_contiguous_id[c]
                else:
                    segments_info[i]["category_id"] = meta.stuff_dataset_id_to_contiguous_id[c]

                    data['panoptic_segmentation'][str(total)] = {}
                    data['panoptic_segmentation'][str(total)]['name'] = stuff_classes[segments_info[i]["category_id"]]
                    data['panoptic_segmentation'][str(total)]['area'] = segments_info[i]["area"]/pic_area*1000
                    total=total+1
        #print(segments_info)

        #print(meta)

        # Finally we visualize the prediction

        print(data)
        return data

    data=segmentation(im,data)
    record, sum,data=plot_results(scores, boxes,data)
    print(data)
    total=0


    for i in range(sum):
        for j in range(i+1,sum):
            size=overlap(record[i][0],record[i][1],record[i][2],record[i][3],
                         record[j][0],record[j][1],record[j][2],record[j][3])
            if(size>0):
                print(i, j, size)
                data['object_detect']['overlap'][str(total)] = {}
                data['object_detect']['overlap'][str(total)]['idA'] = i
                data['object_detect']['overlap'][str(total)]['idB'] = j
                data['object_detect']['overlap'][str(total)]['area'] = size
                total = total + 1
    print(data)
    y = []
    y.append(data)
    print(y)
    return y