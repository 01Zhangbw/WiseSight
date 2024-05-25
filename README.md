# README

Server文件结构：

> Controller
> data
> database
> Interface
> Model
> Temp
> tests
> log.out
> main.py
> test.py

## Controller

#### Agent.py

> 作为chatglm模型基座，AI Agent作为控制中枢，结合function calling技术实现功能调用

#### tools_function.py

> 存放chatglm的自定义工具函数的具体实现，比如获取天气，获取时间，获取位置函数，以及一些调用接口的函数（在interface文件夹的内容）

#### tools_spec.py

> 每个工具函数的具体描述，根据官网的toolfunction设计的，模拟对话部分

## data

> 

## database

> 这部分是数据库，存放用户的个人信息，具体的表结构文件里面可以看到。

## Interface（重点功能实现）

#### ChatGLM Interface.py

> 链接：https://github.com/THUDM/ChatGLM3
>
> chatglm就是实现语音交互基础，所有其他模型生成结果都会经过大模型处理后返回给用户，
>
> 这里主要是用到**chatglm3-6b的基本模型**（model文件夹里面的ZhipuAI）再加上**lora微调**（微调后的模型是model文件夹里的finetune_model)，模型没有合并，所有两个都需要
>
> 数据集是5000条医生和患者的对话
>
> 方法是官网上提供的微调套件
>
> 目的是增强模型对健康知识的问答
>
> ChatGLM接口：
>
> ```
> ├── ChatGLM_Interface
> │   ├── ChatGLM # 模型类，使用单例模式
> │   │   ├── __init__ # 初始化，加载自适应模型、基础模型、分词器，设置模型为评估模式。
> │   │   ├── one_chat # 定义单轮对话方法
> │   │   ├── run_single_glm # 定义async方法，处理单次对话
> ```
>
> 缺点：数据集小了，需要进行扩充。

#### common2.py

> 一个测试文件，无关正常运行。

#### Detection Interface.py

> 目标检测和场景识别的接口。
>
> 目标检测和场景识别的接口。
>
> ```
> ├── Detection_Interface
> │   ├── mmDectionModel
> │   │   ├── __init__ # 初始化，加载模型。
> │   │   ├── Detector # 基本物体识别接口，输入为图片，输出被识别物体的标签、概率、边界、颜色的列表。
> │   │   ├── getColorList # 定义一个颜色范围的字典，返回字典。
> │   │   ├── get_color # 获取物体的颜色。
> │   │   ├── distance_between_points # 用于检测物体之间的距离
> │   │   └── square_center # 用于检测物体的中心位置
> │   │   ├── has_object # 存储目标位置信息
> │   └── SingleImageDataset # 单图像数据集类 继承Pytorch数据集类
> │   │   ├── __init__ # 输入为图像和可选的变换
> │   │   ├── __len__ # 返回数据集长度，但是此处只有一个图片，返回1
> │   │   ├── __getitem__ # 根据索引获取数据集的元素
> │   └── SceneModel # 场景检测
> │       ├── __init__ # 初始化，定义
> │       ├── Detector # 输入图像，返回所在的场景
> ```
>

#### FunAsr Interface.py

> 链接：
>
> - 语音识别：https://www.modelscope.cn/models/damo/speech_UniASR_asr_2pass-zh-cn-16k-common-vocab8358-tensorflow1-offline/summary
> - 标点恢复：https://modelscope.cn/models/damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch/summary
>
> 语音转文字接口。
>
> 模型是魔塔社区的，分为语音识别模型和标点恢复模型两个部分。
>
> 使用方法是安装环境，下载模型，然后推理。
>
> 
>
> ```
> ├── FunAsr_Interface
> │   ├── FunASR # 语音转文字接口，单例模式
> │   │   ├── __init__ # 初始化，加载模型。
> │   │   ├── convert_format # 生成一个临时文件名，扩展名为.amr
> │   │   ├── audio_to_text # 语音转文本
> ```
>

#### OCR Interface.py

> 链接：https://gitee.com/paddlepaddle/PaddleOCR/blob/release/2.6/doc/doc_ch/quickstart.md
>
> 图片转文字接口
>
> 模型是paddleOCR，具体分为文本检测、文本矫正、文本识别三个部分，每个部分的模型是默认的
>
> 使用方法是安装环境，下载模型，然后调用
>
> 
>
> ```
> ├── OCR_Interface
> │   ├── OCR # 从图片提取出文字，单例模式
> │   │   ├── __init__ # 初始化，加载模型。
> │   │   ├── img_to_text # 图片转文本
> ```
>

#### Singleton.py

> 这个是单例模式的实现。
>
> 单例模式
>
> ```
> ├── Singleton
> │   ├── SingletonMeta # 单例模式
> │   │   ├── __call__ # 进行调用
> ```
>

## Model

#### finetune_model

> 微调后的模型存放地址，这个是云服务器训练完下载下来的，数据集不在这里，里面有adapter_config.json文件规定里基本模型地址是/home/cike/WiseSight/Model/ZhipuAI/chatglm3-6b

#### ZhipuAl

> chatglm3-6b模型存放处，由于文件过大没有放在仓库中。

## Temp

> 存放临时文件的地方，比如一些图片、音频、识别数据

## tests

> 就是测试文件，图片啥的，进行修改的地方，无关实际运行

## main.py

> 整个项目入口

