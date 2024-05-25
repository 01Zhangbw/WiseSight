import json
import sys
from typing import Optional
import math
import mmcv
import torch
from mmdet.apis import init_detector, inference_detector
from Singleton import SingletonMeta
from pathlib import Path
import numpy as np
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
from torchvision import models
from torchvision import transforms
import cv2
import numpy as np
import collections
sys.path.append("/home/cike/xyq/mmdetction")  # 将项目根目录添加到环境变量中


class mmDectionModel(metaclass=SingletonMeta):
    def __init__(self, device="cuda:2"):
        self.device = device
        self.config_file = "/home/cike/xyq/mmdetction/projects/Detic_new/configs/detic_centernet2_swin-b_fpn_4x_lvis-base_in21k-lvis.py"
        self.checkpoint_file = '/home/cike/xyq/mmdetction/checkpoints/detic_centernet2_swin-b_fpn_4x_lvis-base_in21k-lvis-ec91245d.pth'
        self.model = init_detector(self.config_file, self.checkpoint_file, device=self.device, palette='random')
        self.model = torch.compile(self.model)  # P100 is too old to support this
        self.sceneModel = SceneModel(device=device)
        print('detection load')

    def Detector(self, input, pred_score_thr=0.5, text_prompt: Optional[str] = None):
        # 基本的物体识别接口，input为图片(numpy.array格式)，pred_score_thr代表识别阈值，text_prompt为需要识别的物体，为空则全部都识别
        # 返回包含每个被识别物体的标签，概率，box
        input = mmcv.imfrombytes(input)
        object_list = inference_detector(self.model, imgs=input)
        object_list = (vars(object_list))["_pred_instances"]
        result = []
        filtered_values = [value for value in object_list["scores"] if value > pred_score_thr]
        for i in range(len(filtered_values)):
            if text_prompt == None or (object_list['label_names'][i] in text_prompt):
                # label_name = object_list['label_names'][i]
                box = object_list['bboxes'][i]
                color = self.get_color(input, box)
                result.append({'label_names': object_list['label_names'][i],
                               'scores': object_list['scores'][i],
                               'box': object_list['bboxes'][i],
                               'color': color})
        print(result)
        return result

    def getColorList(self):
        dict = collections.defaultdict(list)
 
        # 黑色
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 46])
        color_list = []
        color_list.append(lower_black)
        color_list.append(upper_black)
        dict['black'] = color_list
 
        # 灰色
        lower_gray = np.array([0, 0, 46])
        upper_gray = np.array([180, 43, 220])
        color_list = []
        color_list.append(lower_gray)
        color_list.append(upper_gray)
        dict['grey'] = color_list
 
        # 白色
        lower_white = np.array([0, 0, 221])
        upper_white = np.array([180, 30, 255])
        color_list = []
        color_list.append(lower_white)
        color_list.append(upper_white)
        dict['white'] = color_list
 
        # 红色
        lower_red = np.array([156, 43, 46])
        upper_red = np.array([180, 255, 255])
        color_list = []
        color_list.append(lower_red)
        color_list.append(upper_red)
        dict['red'] = color_list
 
        # 红色2
        lower_red = np.array([0, 43, 46])
        upper_red = np.array([10, 255, 255])
        color_list = []
        color_list.append(lower_red)
        color_list.append(upper_red)
        dict['red'] = color_list
 
        # 橙色
        lower_orange = np.array([11, 43, 46])
        upper_orange = np.array([25, 255, 255])
        color_list = []
        color_list.append(lower_orange)
        color_list.append(upper_orange)
        dict['orange'] = color_list
 
        # 黄色
        lower_yellow = np.array([26, 43, 46])
        upper_yellow = np.array([34, 255, 255])
        color_list = []
        color_list.append(lower_yellow)
        color_list.append(upper_yellow)
        dict['yellow'] = color_list
 
        # 绿色
        lower_green = np.array([35, 43, 46])
        upper_green = np.array([77, 255, 255])
        color_list = []
        color_list.append(lower_green)
        color_list.append(upper_green)
        dict['green'] = color_list
 
        # 青色
        lower_cyan = np.array([78, 43, 46])
        upper_cyan = np.array([99, 255, 255])
        color_list = []
        color_list.append(lower_cyan)
        color_list.append(upper_cyan)
        dict['cyan'] = color_list
 
        # 蓝色
        lower_blue = np.array([100, 43, 46])
        upper_blue = np.array([124, 255, 255])
        color_list = []
        color_list.append(lower_blue)
        color_list.append(upper_blue)
        dict['blue'] = color_list
 
        # 紫色
        lower_purple = np.array([125, 43, 46])
        upper_purple = np.array([155, 255, 255])
        color_list = []
        color_list.append(lower_purple)
        color_list.append(upper_purple)
        dict['purple'] = color_list
 
        return dict

    def get_color(self, image, box):
        box = box.to(torch.int)
        x1, y1, x2, y2 = box
        cropped_image = image[y1:y2, x1:x2, :]

        hsv = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
        maxsum = -100
        color = None
        color_dict = self.getColorList()
        for d in color_dict:
            mask = cv2.inRange(hsv, color_dict[d][0], color_dict[d][1])
            binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]
            binary = cv2.dilate(binary, None, iterations=2)
            img, cnts = cv2.findContours(binary.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            sum = 0
            for c in img:
                sum += cv2.contourArea(c)
            if sum > maxsum:
                maxsum = sum
                color = d
        return color

    def distance_between_points(self, x1, y1, x2, y2):
        # 用于检测物体间的距离，用于重要物体位置提示中
        return int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

    def square_center(self, x, y, width, height):
        # 用于检测物体中心位置，用于重要物体位置提示中
        return (x + width) / 2, (y + height) / 2

    def has_object(self, input, key_text, output_dir):
        #存储目标位置信息
        output = self.Detector(input=input)
        label_list = [value['label_names'] for value in output if (value["label_names"] in key_text)]
        if len(label_list) == 0:
            return "no object"

        print('***************')
        print(label_list)
        print('***************')

        scene = self.sceneModel.Detector(input=mmcv.imfrombytes(input))
        print(scene)

        json_data = []
        for word in label_list:
            key_box = [value for value in output if (value["label_names"] == word)][0]['box']
            box_list = [value for value in output if (value["label_names"] != word)]
            distance = []
            x0, y0 = self.square_center(key_box[0], key_box[1], key_box[2], key_box[3])
            for i in range(len(box_list)):
                x1, y1 = self.square_center(box_list[i]['box'][0], box_list[i]['box'][1], box_list[i]['box'][2],
                                            box_list[i]['box'][3])
                distance.append({
                    'distance': self.distance_between_points(
                        x0, y0, x1, y1
                    ),
                    "center": [int(x1), int(y1)],
                    'label': box_list[i]['label_names'],
                    'color': box_list[i]['color']
                })
            sorted_array = sorted(distance, key=lambda x: x['distance'])
            # 去除同一物体的多种识别结果
            unique_distance = []
            distance_values = set()
            for d in sorted_array:
                distance_value = d['distance']
                if distance_value not in distance_values and distance_value != 0:
                    distance_values.add(distance_value)
                    unique_distance.append(d)
            # 去除多个同一物体
            unique_label = []
            label_values = set()
            for d in unique_distance:
                key_value = d['label']
                if key_value not in label_values:
                    label_values.add(key_value)
                    unique_label.append(d)
            # round保存了每个物体距离关键物体的距离和坐标
            json_data.append({"name": word, 'scene': scene, "x0": int(x0), "y0": int(y0), "objects": unique_label})
            print("------------------")
            print(json_data)
            print("------------------")

            try:
                with open(output_dir + 'data2.json', encoding="utf-8") as f:
                    old_data = json.load(f)
                    for one in old_data:
                        if one['name'] not in label_list:
                            json_data.append(one)
            except Exception as e:
                print(f'An unexpected error occurred: {e}')
            with open(output_dir + 'data2.json', 'w', encoding="utf-8") as f:
                json.dump(json_data, f)
        return label_list



class SingleImageDataset(Dataset):
    def __init__(self, img, transform=None):
        self.img = img
        self.transform = transform

    def __len__(self):
        return 1  # 因为只有一个图片

    def __getitem__(self, idx):
        if self.transform:
            img = self.transform(self.img)
            return img
        else:
            return self.img


class SceneModel:
    def __init__(self, device):
        self.model = models.densenet201(weights=True)
        self.model.classifier = nn.Linear(1920, 67, bias=True)
        model_wts = torch.load("/home/cike/xyq/home_scene_5.pkl", map_location=device)
        self.model.load_state_dict(model_wts)
        self.model.eval()
        #self.model = torch.compile(self.model)  # P100 is too old to support this
        from torch import optim
        self.optimizer = optim.SGD(self.model.parameters(), lr=0.001)
        self.categories = ["bathroom", "bedroom", "dining_room", "kitchen", "living_room"]
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])

    def Detector(self, input):
        input = Image.fromarray(np.uint8(input))
        single_image_dataset = SingleImageDataset(input, transform=self.transform)

        # 创建 DataLoader，设置 batch_size 为 1
        data_loader = DataLoader(single_image_dataset, batch_size=1)

        # 遍历 DataLoader 中的每个批次（实际上只有一个批次）
        for images in data_loader:
            # 在这里执行你的处理步骤，images 包含了单个图片的张量
            # images=images.cuda()
            # self.optimizer.zero_grad()
            with torch.no_grad():
                outputs = self.model(images)
                _, preds = torch.max(outputs.data, 1)
                return self.categories[preds]

if __name__ == '__main__':
    model = mmDectionModel()
    key_text = ['key', 'wallet', 'cellular_telephone', 'remote', 'spectacles']
    output_dir='/home/cike/WiseSight/Temp/'
    input_image = ["/home/cike/WiseSight/tests/WechatIMG333.jpg"]  # 加载您的输入图像
    image_path = input_image[0]  # 获取图像文件路径
    with open(image_path, 'rb') as f:
        input_data = f.read()  # 读取图像文件的字节数据
    objects = model.Detector(input=input_data, pred_score_thr=0.5, text_prompt=None)
    text = model.has_object(input=input_data, key_text=key_text, output_dir=output_dir)
    print("Detected labels:", text)

    # 遍历每个被识别的物体，并打印相关信息
    for obj in objects:
        label_name = obj['label_names']
        score = obj['scores']
        box = obj['box']
        color = obj['color']
        
        print("物体标签：", label_name)
        print("置信度：", score)
        print("边界框：", box)
        print("颜色：", color)
        print("--------------------")