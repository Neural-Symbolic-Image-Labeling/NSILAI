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


def pretrain_label(x,imageId):
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
        #print(im)
        img = transform(im).unsqueeze(0)
        # assert img.shape[-2] <= 1600 and img.shape[-1] <= 1600, 'model only supports images up to 1600 pixels on each side'
        # propagate through the model
        outputs = model(img)
        # keep only predictions with 0.7+ confidence
        probas = outputs['logits'].softmax(-1)[0, :, :-1]
        keep = probas.max(-1).values > 0.7
        # convert boxes from [0; 1] to image scales
        bboxes_scaled = rescale_bboxes(outputs['pred_boxes'][0, keep], im.size)
        return probas[keep], bboxes_scaled

    # with open('./pics.png', mode='w+b') as fi:
    #     fi.write(x)
    # # url = 'http://images.cocodataset.org/val2017/000000125062.jpg'
    # # im = Image.open(requests.get(url, stream=True).raw)
    # im = Image.open('pics.png').convert('RGB')

    buf = six.BytesIO()  # 获取指针（地址）对象
    buf.write(x)  # 指针对象写入数据
    buf.seek(0)
    im = Image.open(buf).convert('RGB')

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
            #text = f'{CLASSES[cl]}: {p[cl]:0.2f}'
            #print(sum, record[sum], text)
            data['object'][sum] = {}
            data['object'][sum]['coordinate'] = record[sum]
            data['object'][sum]['name'] = CLASSES[cl]
            data['object'][sum]['prob'] = float(p[cl])
            sum = sum + 1
        return (record, sum, data)

    record = []
    for i in range(50):
        record.append([])
    model = DetrForObjectDetection.from_pretrained('facebook/detr-resnet-50')
    scores, boxes = detect(im, model, transforms)
    data = {
        "imageId": imageId,
        "object": {},
        "overlap": {},
    }
    record, sum, data = plot_results(scores, boxes, data)
    total = 0
    for i in range(sum):
        for j in range(i + 1, sum):
            size = overlap(record[i][0], record[i][1], record[i][2], record[i][3],
                           record[j][0], record[j][1], record[j][2], record[j][3])
            if (size > 0):
                print(i, j, size)
                data['overlap'][str(total)] = {}
                data['overlap'][str(total)]['idA'] = i
                data['overlap'][str(total)]['idB'] = j
                data['overlap'][str(total)]['area'] = size
                total = total + 1
    y=[]
    y.append(data)
    print(y)
    # y = json.dumps(y)
    # print(y)
    return y

# if __name__ == '__main__':
#     x = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x01\xd6IDAT8\x8d\x8d\x93MHTQ\x14\xc7\x7f\xe7\xf2\xfcz\xe3\x84\xd1\x17\xd8\xa4F\x8b"\x17\x83\xcc`IDn\xa2E\xcb\xc4U\xb4\xa84\xdaI\x0b\xa9\x90x\xab\xb6\x12\xb4\xa8]\x16A\x04\x11\xd1@\x9b\xc0$2\xc3\xc2\x82\x886\xd2\x84F\x0b%\x07f\xa6\xc97\xf3\xdei\xe1\xa4\xaf\xf7f\xac\xb3\xba\\~\xff\xf3?\xe7\xdcs\x85:\x91r\x9e\xda\x94\xd8\xde\xd8\xd2Px\xed\x9cX\x01\xd1Z\x9c\x84/\xd2c\xcf\xf6\xf7t\xb6\xdd\xff\xbaTH\xfd(\xac\x02\xa0\xf0\xcd \x97f\xaf\x9f|\x18\xe6M$\xa3VN\';\xb6\xa6\xf6\xedl\r\xba\xec\x06\xbdU\xab\x02+|\xe1\xfb&315?_\xb5N"\x8cT\xab\xd8R7A\xbf3\xd9\\,\x17\xcf(rX\xd0`U\x89 \xac\x8a0\xd3\xd5I39\xe9\xc9\xe6\xd6\x13\xe4\xdd\x9f\xd7\x04\xae\x80RsRU=/\xba\x9a\x88y_(\xe3\xeb\x9b\xc4\x80\x1cZ|l\xd6z\xd4\xe1\xfa\xba\xf5xO\xdc\xfd3\x18\x83\xc8e\x00\xeb\xc8\xe8\x93\xf8*l\x0b\x80\x9e*\x0fD\xc8nX\x93\x07\xeb.\x9e9\x1bx\xb7\xa4*\xc6ze\xcf\x15\xd3n\xda\x05\x1a\x01Duhv\xe0\xe2K*f\x18Q\xbb\n\xb7\x01\x13 \xc7\x03FM|\xdaa\x0b@\xfajf\x1a\xe8\x03p\xdd\x86\xd6\x0f\x83\xe7\xde\x82\x1c\xf8GK\xdf\xa5w\xa1\xdd\x00\xf8\xc6\x8c\x01y\x80\xf3\x1d\x99\xca\x7f\x88A\xe4\x1e\x047\xd1qL7\x07\xed\x8f\xc7\x06\x7f\x11\xdbS\x0e\x90\x8f@\xb3!\xf52\xb1\xd2M\xe9^*DVY\'\xb1\xfeJ\xa0\xdc\xc6\xc8\xe7\xb5\xb3?\'\xbd\x8bSA>\xb2\xca\xf4\xe3!\xacl\x98q\x81\xf6\x91q\xe2}\xe3 G\xc3x\xf4/\x08\x8a\xe7\x9fBx\x07\xf8\x00\xe4\x9e\x17q\x17\xee\xe0\x96nD\x0c7\x0b\x9dN\xb4\xe8\xcc\xde]\x9b1\xbf\x01\xaf\x97\x97\n\xc4\xff\xc3\xf1\x00\x00\x00\x00IEND\xaeB`\x82'
#     pretrain_label(x,2)

