from .tools_spec import tools  # 从相对模块导入'tools'
from .tools_function import functions  # 从相对模块导入'functions'
from Interface.Singleton import SingletonMeta  # 从Interface.Singleton模块导入SingletonMeta
from Interface.FunAsr_Interface import FunASR  # 从Interface.FunAsr_Interface模块导入FunASR
from Interface.ChatGLM_Interface import ChatGLM  # 从Interface.ChatGLM_Interface模块导入ChatGLM
from Interface.OCR_Interface import OCR  # 从Interface.OCR_Interface模块导入OCR
from Interface.Detection_Interface import mmDectionModel  # 从Interface.Detection_Interface模块导入mmDectionModel
import json  # 导入json模块进行JSON操作
import ast  # 导入ast模块进行抽象语法树操作

class Agent:
    funAsr = FunASR()  # 初始化FunASR实例用于语音转文本
    chatGLM = ChatGLM()  # 初始化ChatGLM实例
    ocr = OCR()  # 初始化OCR实例用于从图像中提取文本
    detection = mmDectionModel()  # 初始化mmDectionModel实例用于目标检测

    def __init__(self):
        print("agent创建成功")  # 打印代理创建成功的消息

    async def single_chat(self, input, id, latitude, longitude, history=None):
        if history is not None:  # 检查是否提供了历史记录
            history = ast.literal_eval(history)  # 将历史记录从字符串表示转换为Python对象
            print(history, type(history))  # 打印历史记录及其类型
            # history = json.loads(history)  # 将历史记录从JSON字符串转换为Python对象的替代方法
        res = await self.chatGLM.run_single_glm(input, funtions_list=functions, funtions=tools, history=history, id=id, latitude=latitude, longitude=longitude)
        # 使用提供的参数运行单次聊天，使用ChatGLM
        return res  # 返回响应

    async def chat_by_audio(self, file, id, latitude, longitude, history=None):
        if history is not None:  # 检查是否提供了历史记录
            history = ast.literal_eval(history)  # 将历史记录从字符串表示转换为Python对象
            print(history, type(history))  # 打印历史记录及其类型
            # history = json.loads(history)  # 将历史记录从JSON字符串转换为Python对象的替代方法
        input = self.funAsr.audio_to_text(file)  # 使用FunASR将音频文件转换为文本
        if input:  # 检查是否成功获取输入
            res = await self.chatGLM.run_single_glm(input, funtions_list=functions, funtions=tools, history=history, id=id, latitude=latitude, longitude=longitude)
            # 使用提供的参数运行单次聊天，使用ChatGLM
            return res  # 返回响应
        else:  # 如果未成功获取输入
            if history is not None:  # 检查是否提供了历史记录
                history = json.dumps(history, ensure_ascii=False)  # 将历史记录转换为JSON字符串
            return {'response': "没有录音", 'history': history}  # 返回指示没有录音的响应

    def ocr_data(self, file):
        text = self.ocr.img_to_text(file)  # 使用OCR从图像中提取文本
        return text  # 返回提取的文本

    async def ocr_q_a(self, audio, text, id, latitude, longitude):
        input = self.funAsr.audio_to_text(audio)  # 使用FunASR将音频文件转换为文本
        if input:  # 检查是否成功获取输入
            query = "请根据以下文本内容回答问题。\n" + text + "\n 问题：" + input  # 构造问题和答案的查询
            res = await self.chatGLM.run_single_glm(query, funtions_list=functions, funtions=tools, id=id, latitude=latitude, longitude=longitude)
            # 使用构造的查询和提供的参数运行单次聊天，使用ChatGLM
            return res  # 返回响应
        else:  # 如果未成功获取输入
            return {'response': "没有录音"}  # 返回指示没有录音的响应

    async def has_object_or_not(self, input, id, key_text=None):
        if key_text is None:  # 检查是否提供了关键文本
            key_text = ['key', 'wallet', 'cellular_telephone', 'remote', 'spectacles']  # 如果未提供，则使用默认关键文本
        text = await self.detection.has_object(input, id, key_text)  # 使用检测模型在输入中检测对象
        return text  # 返回检测结果





