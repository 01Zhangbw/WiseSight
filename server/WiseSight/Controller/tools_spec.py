#自定义工具模版

tools = [
    {
        "name": "get_time",
        "description": "查询当前时间函数",
        "parameters": {
            "type": "object",
            "properties": {
            },
            "required": []
        }
    },
    {
        "name": "get_weather",
        # "description": "查询即时天气函数，根据输入的城市名称，查询对应城市的实时天气情况",
        "description": "查询指定城市的实时天气情况。例如：现在的天气如何？或佛山的天气如何？",
        "parameters": {
            "type": "object",
            "properties": {
                "cityname": {
                    "type": "string",
                    "description": "城市名称，非必须项，可以为空。例如：广州、北京、佛山等。",
                },
            },
            "required": [],
        },
    },
    {
        "name": "keyObject_LocationHint",
        "description": "帮助用户寻找某个物品，物品只能为钱包、钥匙、手机、遥控器、眼镜，例如：钥匙在哪里？",
        "parameters": {
            "type": "object",
            "properties": {
                "thing": {
                    "type": "string",
                    "description": "物品名称，是所需要查找的物品，取值只能为5种：钱包 | 钥匙 | 手机 | 遥控器 ｜ 眼镜",
                },
            },
            "required": ["thing"],
        },
    },
    {
        "name": "alarm",
        "description": "用户要求设置提醒、或给出特定时间后完成某事时调用该函数。e.g. 提醒我三十分钟后关火 ｜ 一分钟后给女儿打电话 ",
        "parameters": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "int",
                    "description": "多长时间后进行提醒。e.g. 30 ｜ 1",
                },
                "time_type": {
                    "type": "string",
                    "description": "时间的单位是什么，只能有4种类型，分别是second，minute，hour，day。e.g. second ｜ minute ｜ hour ｜ day",
                },
                "task": {
                    "type": "string",
                    "description": "要提醒的内容或操作，e.g. 关火 ｜给女儿打电话",
                },
            },
            "required": ["time", "time_type", "task"],
        },
    },
    {
        "name": "set_userInfo",
        "description": "获取并更新用户本人的基本信息。e.g. 我叫陈林林，今年五十二岁，女，患有高血压、糖尿病",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "用户的名字，非必须项，可以为空。e.g. 陈林林 ",
                },
                "age": {
                    "type": "int",
                    "description": "用户的年龄，非必须项，可以为空。e.g. 52",
                },
                "gender": {
                    "type": "string",
                    "description": "用户的性别，非必须项，可以为空。只有男、女两种情况，e.g. 男 ｜ 女",
                },
                "disease": {
                    "type": "string",
                    "description": "用户患有的所有疾病，非必须项，可以为空。e.g. 高血压、糖尿病、心脏病",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_userInfo",
        "description": "查询用户本人的基本信息，如姓名、年龄，性别，患有疾病。e.g. 我今年几岁了 ｜ 我患有什么疾病",
        "parameters": {
            "type": "object",
            "properties": {
            },
            "required": [],
        },
    },
    {
        "name": "set_emergency_contact_person",
        # "description": "设置或更新紧急联系人的信息，紧急联系人姓名，紧急联系人电话，与用户的关系。e.g. 我的紧急联系人是我的女儿，她叫陈静静，电话是15918879355",
        "description": "设置或更新紧急联系人的信息，e.g. 我的紧急联系人是我的女儿，她叫陈静静，电话是15918879355",
        "parameters": {
            "type": "object",
            "properties": {
                "emergency_name": {
                    "type": "string",
                    "description": "紧急联系人的名字，非必须项，可以为空。e.g. 陈林林 ",
                },
                "emergency_phone": {
                    "type": "string",
                    "description": "紧急联系人的电话，十一位的数字，非必须项，可以为空。e.g. 15918879355",
                },
                "relation": {
                    "type": "string",
                    "description": "与用户的关系，e.g. 女儿",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_emergency_contact_person",
        "description": "查询、获取紧急联系人的信息，如姓名、电话、与用户的关系。e.g. 请问我的紧急联系人的电话是多少 ｜ 我的紧急联系人是谁",
        "parameters": {
            "type": "object",
            "properties": {
            },
            "required": [],
        },
    },
    {
        "name": "call_help",
        "description": "用户进行呼救、要求联系紧急联系人的时候调用该函数。",
        "parameters": {
            "type": "object",
            "properties": {
                "abnormal": {
                    "type": "string",
                    "description": "用户的异常情况，e.g. 摔倒了 ｜ 喘不过气来 ｜ 心脏疼 ",
                },
            },
            "required": ["abnormal"],
        },
    },
]