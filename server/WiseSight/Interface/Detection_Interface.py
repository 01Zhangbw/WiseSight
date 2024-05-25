import json
import sys
from typing import Optional
import math
import mmcv
import torch
from mmdet.apis import init_detector, inference_detector
from .Singleton import SingletonMeta
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
from database import orm

# 将项目根目录添加到环境变量中
sys.path.append("/home/cike/xyq/mmdetction")  

class mmDectionModel(metaclass=SingletonMeta):
    def __init__(self, device="cuda:2"):
        self.device = device
        # 加载检测模型配置文件和权重文件
        self.config_file = "/home/cike/xyq/mmdetction/projects/Detic_new/configs/detic_centernet2_swin-b_fpn_4x_lvis-base_in21k-lvis.py"
        self.checkpoint_file = '/home/cike/xyq/mmdetction/checkpoints/detic_centernet2_swin-b_fpn_4x_lvis-base_in21k-lvis-ec91245d.pth'
        # 初始化检测模型
        self.model = init_detector(self.config_file, self.checkpoint_file, device=self.device, palette='random')
        # 编译模型以提高性能（但注意P100 GPU可能不支持）
        self.model = torch.compile(self.model)  # P100 is too old to support this
        # 初始化场景识别模型
        self.sceneModel = SceneModel(device=device)
        print('detection load') # 模型加载成功

    def Detector(self, input, pred_score_thr=0.5, text_prompt: Optional[str] = None):
        # 基本的物体识别接口
        # input为图片(numpy.array格式)，pred_score_thr代表识别阈值，text_prompt为需要识别的物体，为空则全部都识别
        # 返回包含每个被识别物体的标签，概率，边界和颜色的列表

        # 将输入图片从字节流转换为图像格式
        input = mmcv.imfrombytes(input)
        # 使用模型进行物体检测，返回识别结果
        object_list = inference_detector(self.model, imgs=input)
        # 提取预测实例
        object_list = (vars(object_list))["_pred_instances"]
        # 初始化结果列表
        result = []
        # 根据阈值过滤识别结果
        filtered_values = [value for value in object_list["scores"] if value > pred_score_thr]
        # 遍历过滤后的识别结果
        for i in range(len(filtered_values)):
            # 如果text_prompt为空或当前标签在text_prompt中
            if text_prompt == None or (object_list['label_names'][i] in text_prompt):
                # label_name = object_list['label_names'][i]
                # 获取物体的标签名、置信度、边界框和颜色
                box = object_list['bboxes'][i] # 边界框
                color = self.get_color(input, box) # 颜色
                result.append({'label_names': object_list['label_names'][i],
                               'scores': object_list['scores'][i],
                               'box': object_list['bboxes'][i],
                               'color': color})
        print(result)
        return result # 返回识别结果
    
    def getColorList(self):
        # 定义一个颜色范围的字典，包含黑色、灰色、白色、红色、橙色、黄色、绿色、青色、蓝色和紫色
        dict = collections.defaultdict(list)
 
        # 黑色
        lower_black = np.array([0, 0, 0]) # 定义black的HSV下界
        upper_black = np.array([180, 255, 46]) # 定义black的HSV上界
        color_list = [] # 初始化颜色范围列表
        color_list.append(lower_black) # 将黑色的HSV范围下界添加到列表中
        color_list.append(upper_black) # 将黑色的HSV范围上界添加到列表中
        dict['black'] = color_list # 将黑色的HSV范围添加到字典
 
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
        # 获取物体的颜色

        # 将box坐标转换为整数类型
        box = box.to(torch.int)
        x1, y1, x2, y2 = box
        # 裁剪图片，得到box区域内的图像
        cropped_image = image[y1:y2, x1:x2, :]
        # 将裁剪后的图像从BGR颜色空间转换为HSV颜色空间
        hsv = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
        maxsum = -100 # 用于记录最大的颜色区域面积
        color = None # 用于记录识别出的颜色

        # 获取颜色范围字典
        color_dict = self.getColorList()
        # 遍历颜色范围字典
        for d in color_dict:
            # 创建一个掩码，通过颜色范围筛选指定颜色区域
            mask = cv2.inRange(hsv, color_dict[d][0], color_dict[d][1])
            # 对掩码进行二值化处理
            binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]
            # 进行膨胀操作，使颜色区域更连贯
            binary = cv2.dilate(binary, None, iterations=2)
            # 查找二值化图像中的轮廓
            img, cnts = cv2.findContours(binary.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            sum = 0 # 用于累加当前颜色的区域面积
            # 遍历所有轮廓，计算总面积
            for c in img:
                sum += cv2.contourArea(c)
            # 如果当前颜色区域面积大于最大面积，则更新最大面积和对应的颜色
            if sum > maxsum:
                maxsum = sum
                color = d
        # 返回识别的颜色
        return color

    # def Detector(self, input, pred_score_thr=0.5, text_prompt: Optional[str] = None):
    #     # 基本的物体识别接口，input为图片(numpy.array格式)，pred_score_thr代表识别阈值，text_prompt为需要识别的物体，为空则全部都识别
    #     # 返回包含每个被识别物体的标签，概率，box
    #     input = mmcv.imfrombytes(input)
    #     object_list = inference_detector(self.model, imgs=input)
    #     object_list = (vars(object_list))["_pred_instances"]
    #     result = []
    #     filtered_values = [value for value in object_list["scores"] if value > pred_score_thr]
    #     for i in range(len(filtered_values)):
    #         if text_prompt == None or (object_list['label_names'][i] in text_prompt):
    #             result.append({'label_names': object_list['label_names'][i],
    #                            'scores': object_list['scores'][i],
    #                            'box': object_list['bboxes'][i]})
                
    #     print(result)
    #     return result

    def distance_between_points(self, x1, y1, x2, y2):
        # 用于检测物体间的距离，用于重要物体位置提示中
        return int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

    def square_center(self, x, y, width, height):
        # 用于检测物体中心位置，用于重要物体位置提示中
        return (x + width) / 2, (y + height) / 2

    async def has_object(self, input, android_id, key_text):
        # 存储目标位置信息
        output = self.Detector(input=input)
        # 筛选出标签名在key_text中的对象
        label_list = [value['label_names'] for value in output if (value["label_names"] in key_text)]
        # 如果没有符合条件的对象，返回"no object"
        if len(label_list) == 0:
            return "no object"
        # 使用sceneModel检测场景
        scene = self.sceneModel.Detector(input=mmcv.imfrombytes(input))
        # 对于每个符合条件的标签名
        for word in label_list:
            # 获取该标签名的目标框（bounding box）
            key_box = [value for value in output if (value["label_names"] == word)][0]['box']
            # 获取所有其他目标框
            box_list = [value for value in output if (value["label_names"] != word)]
            # 存储距离信息
            distance = []
            # 计算关键目标的中心点
            x0, y0 = self.square_center(key_box[0], key_box[1], key_box[2], key_box[3])
            # 计算其他目标中心点与关键目标的中心点距离
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
            # 按距离升序排序
            sorted_array = sorted(distance, key=lambda x: x['distance'])
            # 去除同一物体的多种识别结果
            unique_distance = []
            distance_values = set()
            for d in sorted_array:
                distance_value = d['distance']
                if distance_value not in distance_values and distance_value != 0:
                    distance_values.add(distance_value)
                    unique_distance.append(d)
            # 去除多个同一物体，保留唯一标签
            unique_label = []
            label_values = set()
            for d in unique_distance:
                key_value = d['label']
                if key_value not in label_values:
                    label_values.add(key_value)
                    unique_label.append(d)

            # 异步创建或更新对象信息
            await orm.create_or_update_object(android_id, word, scene, int(x0), int(y0), json.dumps(unique_label))
        # 返回标签列表
        return label_list


# 定义单图像数据集类，继承自 PyTorch 的 Dataset 类
class SingleImageDataset(Dataset):
    # 初始化方法，接受一个图像和一个可选的变换
    def __init__(self, img, transform=None):
        self.img = img  # 存储传入的图像
        self.transform = transform  # 存储传入的变换操作

    # 返回数据集的长度，这里因为只有一张图片，所以返回 1
    def __len__(self):
        return 1  # 因为只有一个图片

    # 根据索引获取数据集中的元素，这里 idx 参数虽然没用上，但保留是为了符合 Dataset 类的接口
    def __getitem__(self, idx):
        # 如果定义了变换操作，则对图像进行变换后返回
        if self.transform:
            img = self.transform(self.img)  # 对图像进行变换
            return img  # 返回变换后的图像
        else:
            return self.img  # 如果没有变换操作，直接返回原始图像

# 场景检测
class SceneModel:
    def __init__(self, device):
        # 加载预训练的densenet201模型
        self.model = models.densenet201(weights=True)
        # 修改模型的最后一层，以适应具体的场景分类任务
        self.model.classifier = nn.Linear(1920, 67, bias=True)
        # 加载预训练的模型权重
        model_wts = torch.load("/home/cike/xyq/home_scene_5.pkl", map_location=device)
        self.model.load_state_dict(model_wts)
        # 设置模型为评估模式
        self.model.eval()
        # P100显卡太旧，不支持torch.compile，暂时注释
        #self.model = torch.compile(self.model)  # P100 is too old to support this
        from torch import optim
        # 定义优化器
        self.optimizer = optim.SGD(self.model.parameters(), lr=0.001)
        # 定义场景类别
        self.categories = ["bathroom", "bedroom", "dining_room", "kitchen", "living_room"]
        # 定义图像预处理流程
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])

    def Detector(self, input):
        # 将输入的numpy数组转换为PIL图像
        input = Image.fromarray(np.uint8(input))
        # 创建单张图片的数据集，并应用预处理
        single_image_dataset = SingleImageDataset(input, transform=self.transform)

        # 创建 DataLoader，设置 batch_size 为 1
        data_loader = DataLoader(single_image_dataset, batch_size=1)

        # 遍历 DataLoader 中的每个批次（实际上只有一个批次）
        for images in data_loader:
            # 在这里执行你的处理步骤，images 包含了单个图片的张量
            # images=images.cuda()
            # self.optimizer.zero_grad()
            # 禁用梯度计算，进行推理
            with torch.no_grad():
                # 将图像输入模型，获得输出
                outputs = self.model(images)
                # 取出输出中最大值的索引，即预测的类别
                _, preds = torch.max(outputs.data, 1)
                # 返回对应的场景
                return self.categories[preds]

