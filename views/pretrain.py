from PIL import Image
from transformers import DetrFeatureExtractor, DetrForObjectDetection
import torch
import six
import torchvision.transforms as transforms
torch.set_grad_enabled(False)
# classes
feature_extractor = DetrFeatureExtractor.from_pretrained('facebook/detr-resnet-50')
transforms = transforms.Compose([
    transforms.Resize(feature_extractor.size),
    transforms.ToTensor(),
    transforms.Normalize(feature_extractor.image_mean, feature_extractor.image_std)
])

def pretrain_label(im,number):
    buf = six.BytesIO()  # 获取指针（地址）对象
    buf.write(x)  # 指针对象写入数据
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
        print(im)
        img = transform(im).unsqueeze(0)
        #assert img.shape[-2] <= 1600 and img.shape[-1] <= 1600, 'model only supports images up to 1600 pixels on each side'
        # propagate through the model
        outputs = model(img)
        # keep only predictions with 0.7+ confidence
        probas = outputs['logits'].softmax(-1)[0, :, :-1]
        keep = probas.max(-1).values > 0.7
        # convert boxes from [0; 1] to image scales
        bboxes_scaled = rescale_bboxes(outputs['pred_boxes'][0, keep], im.size)
        return probas[keep], bboxes_scaled

    #url = 'http://images.cocodataset.org/val2017/000000125062.jpg'
    #im = Image.open(requests.get(url, stream=True).raw)
    #im = Image.open('image/residential/8.png')
    #im = Image.open('125062.jpg')
    pic_area=im.size[0]*im.size[1]
    print(pic_area)



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

    def plot_results(pil_img, prob, boxes,data):
        plt.figure(figsize=(16, 10))
        plt.imshow(pil_img)
        ax = plt.gca()
        sum = 0
        for p, (xmin, ymin, xmax, ymax), c in zip(prob, boxes.tolist(), COLORS * 100):
            ax.add_patch(plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin,
                                       fill=False, color=c, linewidth=3))

            record[sum].append(xmin)
            record[sum].append(ymin)
            record[sum].append(xmax)
            record[sum].append(ymax)
            cl = p.argmax()
            text = f'{CLASSES[cl]}: {p[cl]:0.2f}'
            ax.text(xmin, ymin, text, fontsize=15,
                    bbox=dict(facecolor='yellow', alpha=0.5))
            print(sum,record[sum],text)
            data['object_detect']['object'][str(sum)] = {}
            data['object_detect']['object'][str(sum)]['coordinate']=record[sum]
            data['object_detect']['object'][str(sum)]['name'] = CLASSES[cl]
            data['object_detect']['object'][str(sum)]['prob'] = float(p[cl])

            sum = sum + 1
        plt.axis('off')
        plt.show()
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
    transform = T.Compose([
        T.Resize(800),
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    def segmentation(im,data):
        # These are the COCO classes
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

        # Detectron2 uses a different numbering scheme, we build a conversion table
        coco2d2 = {}
        count = 0
        for i, c in enumerate(CLASSES):
            if c != "N/A":
                coco2d2[i] = count
                count += 1

        # standard PyTorch mean-std input image normalization


        model, postprocessor = torch.hub.load('facebookresearch/detr', 'detr_resnet101_panoptic', pretrained=True,
                                              return_postprocessor=True, num_classes=250)
        model.eval()

        # url = "http://images.cocodataset.org/val2017/000000125062.jpg"
        # im = Image.open(requests.get(url, stream=True).raw)
        #im = Image.open('image/campus/3.png')
        # mean-std normalize the input image (batch-size: 1)
        img = transform(im).unsqueeze(0)
        out = model(img)
        # print("---------outputs--------")
        # print(out)
        # compute the scores, excluding the "no-object" class (the last one)
        scores = out["pred_logits"].softmax(-1)[..., :-1].max(-1)[0]
        # print("----------scores--------")
        # print(scores)
        # threshold the confidence
        keep = scores > 0.85
        # print("--‘True’ means prob >0.85 and it is a mask--")
        # print(keep)

        # Plot all the remaining masks
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
            # print(result)
            import itertools
            import seaborn as sns

            palette = itertools.cycle(sns.color_palette())

            # The segmentation is stored in a special-format png
            panoptic_seg = Image.open(io.BytesIO(result['png_string']))
            panoptic_seg = numpy.array(panoptic_seg, dtype=numpy.uint8).copy()
            # We retrieve the ids corresponding to each mask
            panoptic_seg_id = rgb2id(panoptic_seg)

            # Finally we color each mask individually
            panoptic_seg[:, :, :] = 0
            for id in range(panoptic_seg_id.max() + 1):
                panoptic_seg[panoptic_seg_id == id] = numpy.asarray(next(palette)) * 255
            # plt.figure(figsize=(15, 15))
            # plt.imshow(panoptic_seg)
            # plt.axis('off')
            # plt.show()

            # -------------better looking------------
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
            # print("1")
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
                    # print(stuff_classes[segments_info[i]["category_id"]])
                    # print(segments_info[i]["category_id"])
                    total=total+1
            print(segments_info)

            print(meta)
        except:
            print("Picture has only two parts")
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
                    data['panoptic_segmentation'][str(total)]['area'] = segments_info[i]["area"]
                    total=total+1
        #print(segments_info)

        #print(meta)

        # Finally we visualize the prediction

        print(data)
        return data

    data=segmentation(im,data)


    record, sum,data=plot_results(im, scores, boxes,data)
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
    y=[]
    y.append(data)
    print(y)
    # y = json.dumps(y)
    # print(y)
    return y


# if __name__ == '__main__':
#     x = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x01\xd6IDAT8\x8d\x8d\x93MHTQ\x14\xc7\x7f\xe7\xf2\xfcz\xe3\x84\xd1\x17\xd8\xa4F\x8b"\x17\x83\xcc`IDn\xa2E\xcb\xc4U\xb4\xa84\xdaI\x0b\xa9\x90x\xab\xb6\x12\xb4\xa8]\x16A\x04\x11\xd1@\x9b\xc0$2\xc3\xc2\x82\x886\xd2\x84F\x0b%\x07f\xa6\xc97\xf3\xdei\xe1\xa4\xaf\xf7f\xac\xb3\xba\\~\xff\xf3?\xe7\xdcs\x85:\x91r\x9e\xda\x94\xd8\xde\xd8\xd2Px\xed\x9cX\x01\xd1Z\x9c\x84/\xd2c\xcf\xf6\xf7t\xb6\xdd\xff\xbaTH\xfd(\xac\x02\xa0\xf0\xcd \x97f\xaf\x9f|\x18\xe6M$\xa3VN\';\xb6\xa6\xf6\xedl\r\xba\xec\x06\xbdU\xab\x02+|\xe1\xfb&315?_\xb5N"\x8cT\xab\xd8R7A\xbf3\xd9\\,\x17\xcf(rX\xd0`U\x89 \xac\x8a0\xd3\xd5I39\xe9\xc9\xe6\xd6\x13\xe4\xdd\x9f\xd7\x04\xae\x80RsRU=/\xba\x9a\x88y_(\xe3\xeb\x9b\xc4\x80\x1cZ|l\xd6z\xd4\xe1\xfa\xba\xf5xO\xdc\xfd3\x18\x83\xc8e\x00\xeb\xc8\xe8\x93\xf8*l\x0b\x80\x9e*\x0fD\xc8nX\x93\x07\xeb.\x9e9\x1bx\xb7\xa4*\xc6ze\xcf\x15\xd3n\xda\x05\x1a\x01Duhv\xe0\xe2K*f\x18Q\xbb\n\xb7\x01\x13 \xc7\x03FM|\xdaa\x0b@\xfajf\x1a\xe8\x03p\xdd\x86\xd6\x0f\x83\xe7\xde\x82\x1c\xf8GK\xdf\xa5w\xa1\xdd\x00\xf8\xc6\x8c\x01y\x80\xf3\x1d\x99\xca\x7f\x88A\xe4\x1e\x047\xd1qL7\x07\xed\x8f\xc7\x06\x7f\x11\xdbS\x0e\x90\x8f@\xb3!\xf52\xb1\xd2M\xe9^*DVY\'\xb1\xfeJ\xa0\xdc\xc6\xc8\xe7\xb5\xb3?\'\xbd\x8bSA>\xb2\xca\xf4\xe3!\xacl\x98q\x81\xf6\x91q\xe2}\xe3 G\xc3x\xf4/\x08\x8a\xe7\x9fBx\x07\xf8\x00\xe4\x9e\x17q\x17\xee\xe0\x96nD\x0c7\x0b\x9dN\xb4\xe8\xcc\xde]\x9b1\xbf\x01\xaf\x97\x97\n\xc4\xff\xc3\xf1\x00\x00\x00\x00IEND\xaeB`\x82'
#     pretrain_label(x,2)

