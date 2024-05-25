import json

# 从 Singleton 模块导入 SingletonMeta 元类，用于创建单例模式的类
from .Singleton import SingletonMeta

# 导入文件路径相关的库
from pathlib import Path
# 导入类型注解相关的库
from typing import Annotated, Union
# 导入 peft 库中的模型类
from peft import AutoPeftModelForCausalLM, PeftModelForCausalLM
# 导入 transformers 库中的模型和分词器类
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)
# 导入数据库 ORM
from database import orm

# 定义模型和分词器的类型别名
ModelType = Union[PreTrainedModel, PeftModelForCausalLM]
TokenizerType = Union[PreTrainedTokenizer, PreTrainedTokenizerFast]

# 创建 ChatGLM 模型类，使用单例模式
class ChatGLM(metaclass=SingletonMeta):
    # 对 ChatGLM 进行初始化
    def __init__(self):
        model_dir = Path('/home/cike/WiseSight/Model/finetune_model')
        # 判断是否存在适配器配置文件
        if (model_dir / 'adapter_config.json').exists():
            # 加载自适应模型
            model = AutoPeftModelForCausalLM.from_pretrained(
                model_dir, trust_remote_code=True
            ).half().cuda(1)
            tokenizer_dir = model.peft_config['default'].base_model_name_or_path
        else:
            # 加载基础模型
            model = AutoModelForCausalLM.from_pretrained(
                model_dir, trust_remote_code=True
            ).half().cuda(1)
            tokenizer_dir = model_dir
        # 加载分词器
        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_dir, trust_remote_code=True
        )
        # 设置模型为评估模式
        self.model = model.eval()
        print('chatglm load')

    # 定义单轮对话方法
    def one_chat(self, input, history=None):
        response, history = self.model.chat(self.tokenizer, input, history=history)
        return response

    # 定义异步方法，处理单次对话
    async def run_single_glm(self, input, id, latitude, longitude, funtions_list=None, funtions=None, history=None):
        # 初始化对话历史
        if history is None and funtions_list is None:
            history = [{
                "role": "system",
                "content": "你是为老年人服务的AI生活助手。请用明确简洁的中文认真回答我的问题，为我提供帮助。"
            }]
        elif history is None:
            # 获取用户信息
            user = await orm.get_user(id)
            if user is None:
                # 如果用户不存在，则创建新用户并提示登记信息
                await orm.create_user(id)
                return {'response': "您是新用户，请先登记您的基本信息。请告诉我您的姓名，性别，年龄和患有的疾病。", 'history': None}
            # 构建用户信息描述
            data = "用户的基本信息如下"
            if user.name:
                data = data + "，姓名：" + user.name
            if user.age:
                data = data + "，年龄：" + str(user.age)
            if user.gender:
                data = data + "，性别：" + user.gender
            if user.disease:
                data = data + "，患有疾病：" + user.disease
            # 初始化历史记录
            history = [{
                "role": "system",
                "content": "你是为老年用户服务的AI生活助手。" + data + "。请用明确简洁的中文认真与用户进行交流。如果无法回答用户的问题，可以使用以下工具获取相关的信息。" ,
                "tools": funtions
            }]
        # 根据是否有函数列表进行对话处理
        if funtions_list is None:
            final_response, history = self.model.chat(self.tokenizer, input, history=history)
        else:
            # 构建可用函数字典
            available_functions = {func.__name__: func for func in funtions_list}
            response_message, history = self.model.chat(self.tokenizer, input, history=history)
            print(response_message)

            if isinstance(response_message, dict):
                function_name = response_message['name']
                function_to_call = available_functions[function_name]
                function_args = response_message['parameters']
                function_args['android_id'] = id
                # 特殊处理特定函数
                if function_name == "get_weather" or function_name == "call_help":
                    function_args['latitude'] = latitude
                    function_args['longitude'] = longitude
                # 调用相应函数
                function_response = await function_to_call(**function_args)
                print(function_response)

                # 处理函数返回结果
                if function_response.startswith('alarm,'):
                    history.append({"role": "assistant", "metadata": "", "content": function_response})
                    return {'response': function_response, 'history': history}

                if function_response.startswith('call'):
                    history.append({"role": "assistant", "metadata": "", "content": function_response})
                    return {'response': function_response, 'history': history}

                # 构建查询并进行对话
                query = str({
                    'role': 'observation',
                    'name': function_name,
                    'content': function_response,
                })
                response_message, history = self.model.chat(self.tokenizer, query, history=history)
            final_response = response_message
        return {'response': final_response, 'history': json.dumps(history, ensure_ascii=False)}
