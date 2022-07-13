import six
import torch
import torchvision.transforms as transforms
from transformers import DetrFeatureExtractor, DetrForObjectDetection

torch.set_grad_enabled(False)
from PIL import Image
import torch
import torchvision.transforms as T

torch.set_grad_enabled(False)

# classes
feature_extractor = DetrFeatureExtractor.from_pretrained('facebook/detr-resnet-50')
transforms = transforms.Compose([
    transforms.Resize(feature_extractor.size),
    transforms.ToTensor(),
    transforms.Normalize(feature_extractor.image_mean, feature_extractor.image_std)
])


def pretrain_label(im, number):
    buf = six.BytesIO()  # 获取指针（地址）对象
    buf.write(im)  # 指针对象写入数据
    buf.seek(0)
    im = Image.open(buf).convert('RGB')
    print(im)
    # url = 'http://images.cocodataset.org/val2017/000000125062.jpg'
    # im = Image.open(requests.get(url, stream=True).raw)
    #im = Image.open('image/special.jpg')
    # im = Image.open('125062.jpg')
    pic_area = im.size[0] * im.size[1]
    # print(pic_area)

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

    def overlap(x1, y1, x2, y2, x3, y3, x4, y4):
        s1 = [x1, y1, x2, y2]
        s2 = [x3, y3, x4, y4]
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
        return (res)

    def plot_results(prob, boxes, data):
        sum = 0
        for p, (xmin, ymin, xmax, ymax) in zip(prob, boxes.tolist()):
            record[sum].append(xmin)
            record[sum].append(ymin)
            record[sum].append(xmax)
            record[sum].append(ymax)
            cl = p.argmax()
            data['object_detect']['object'][str(sum)] = {}
            data['object_detect']['object'][str(sum)]['coordinate'] = record[sum]
            data['object_detect']['object'][str(sum)]['name'] = CLASSES[cl]
            data['object_detect']['object'][str(sum)]['prob'] = float(p[cl])
            sum = sum + 1
        return (record, sum, data)

    record = []
    for i in range(50):
        record.append([])
    model = DetrForObjectDetection.from_pretrained('facebook/detr-resnet-50')
    scores, boxes = detect(im, model, transforms)
    data = {
        "imageId": number,
        "object_detect": {
            "object": {},
            "overlap": {}
        },
        "panoptic_segmentation": {},
    }

    def segmentation(im,data):
        from detectron2.data import MetadataCatalog
        from copy import deepcopy
        transform = T.Compose([
            T.Resize(800),
            T.ToTensor(),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        model, postprocessor = torch.hub.load('facebookresearch/detr', 'detr_resnet101_panoptic', pretrained=True,
                                              return_postprocessor=True, num_classes=250)
        model.eval()
        img = transform(im).unsqueeze(0)
        out = model(img)
        result = postprocessor(out, torch.as_tensor(img.shape[-2:]).unsqueeze(0))[0]
        segments_info = deepcopy(result["segments_info"])
        meta = MetadataCatalog.get("coco_2017_val_panoptic_separated")
        stuff_classes = ['things', 'banner', 'blanket', 'bridge', 'cardboard', 'counter', 'curtain', 'door-stuff',
                         'floor-wood', 'flower', 'fruit', 'gravel', 'house', 'light', 'mirror-stuff', 'net',
                         'pillow',
                         'platform', 'playingfield', 'railroad', 'river', 'road', 'roof', 'sand', 'sea', 'shelf',
                         'snow',
                         'stairs', 'tent', 'towel', 'wall-brick', 'wall-stone', 'wall-tile', 'wall-wood', 'water',
                         'window-blind', 'window', 'tree', 'fence', 'ceiling', 'sky', 'cabinet', 'table', 'floor',
                         'pavement', 'mountain', 'grass', 'dirt', 'paper', 'food', 'building', 'rock', 'wall',
                         'rug']
        total = 0
        for i in range(len(segments_info)):
            c = segments_info[i]["category_id"]
            if segments_info[i]["isthing"]:
                segments_info[i]["category_id"] = meta.thing_dataset_id_to_contiguous_id[c]
            else:
                segments_info[i]["category_id"] = meta.stuff_dataset_id_to_contiguous_id[c]
                data['panoptic_segmentation'][str(total)] = {}
                data['panoptic_segmentation'][str(total)]['name'] = stuff_classes[segments_info[i]["category_id"]]
                data['panoptic_segmentation'][str(total)]['area'] = segments_info[i]["area"]
                total = total + 1
        return data

    # -----------------------sengmentation--------------------------
    data = segmentation(im, data)
    # ------------------------object_detect--------------------------
    record, sum, data = plot_results(scores, boxes, data)
    total = 0
    for i in range(sum):
        for j in range(i + 1, sum):
            size = overlap(record[i][0], record[i][1], record[i][2], record[i][3],
                           record[j][0], record[j][1], record[j][2], record[j][3])
            if (size > 0):
                #print(i, j, size)
                data['object_detect']['overlap'][str(total)] = {}
                data['object_detect']['overlap'][str(total)]['idA'] = i
                data['object_detect']['overlap'][str(total)]['idB'] = j
                data['object_detect']['overlap'][str(total)]['area'] = size
                total = total + 1
    y = []
    y.append(data)
    print(y)
    return y