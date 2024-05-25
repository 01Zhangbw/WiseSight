# 自定义工具

import datetime  # 导入datetime模块以处理日期和时间
import json  # 导入json模块进行JSON操作
import requests  # 导入requests模块以进行HTTP请求
from pathlib import Path  # 导入Path类以处理文件路径
from database import orm  # 从数据库模块导入orm

KEY = 'f0e5cfcaf749fb949c31d5afec15a729' # 高德地图API的密钥

# 定义异步函数query以发送HTTP GET请求并返回JSON响应
async def query(url, params):
    ans = json.loads(requests.get(url, params).content)  # 发送请求并解析响应内容为JSON
    return ans  # 返回解析后的JSON数据

# 定义异步函数get_adcode以根据地址获取行政区划代码
async def get_adcode(address):
    url = 'https://restapi.amap.com/v3/geocode/geo'  # 高德地图地理编码API的URL
    params = {'key': KEY, 'address': address}  # API请求参数
    ans = await query(url, params)  # 发送请求并获取响应
    return ans['geocodes'][0]['adcode']  # 返回第一个地理编码结果的adcode

# 定义异步函数get_adcode_by_location以根据经纬度获取行政区划代码
async def get_adcode_by_location(latitude, longitude):
    url = 'https://restapi.amap.com/v3/geocode/regeo'  # 高德地图逆地理编码API的URL
    location = longitude + ',' + latitude  # 组合经纬度
    params = {'key': KEY, 'location': location}  # API请求参数
    ans = await query(url, params)  # 发送请求并获取响应
    return ans['regeocode']['addressComponent']['adcode']  # 返回逆地理编码结果的adcoe

# 定义异步函数get_detail_location以根据经纬度获取详细地址
async def get_detail_location(latitude, longitude):
    url = 'https://restapi.amap.com/v3/geocode/regeo'  # 高德地图逆地理编码API的URL
    location = longitude + ',' + latitude  # 组合经纬度
    params = {'key': KEY, 'location': location}  # API请求参数
    ans = await query(url, params)  # 发送请求并获取响应
    return ans['regeocode']['formatted_address']  # 返回格式化的地址d

# 定义异步函数get_weather以获取当前天气信息
async def get_weather(android_id, cityname, latitude, longitude):
    '''
    查询现在的天气情况
    :param cityname: str 城市的名称，非必须项，可以为空
    :return:返回实时天气。
    '''
    city = None
    if cityname:
        city = await get_adcode(cityname)  # 如果提供城市名称，通过地址获取adcode
        print(city)
    if not city:
        city = await get_adcode_by_location(latitude, longitude)  # 如果未提供城市名称，通过经纬度获取adcode
        print("location")
    url = 'https://restapi.amap.com/v3/weather/weatherInfo'  # 高德地图天气API的URL
    params = {'key': KEY, 'city': city}  # API请求参数
    ans = await query(url, params)  # 发送请求并获取响应
    text = ans['lives'][0]  # 获取实时天气信息
    return "天气:" + text['weather'] + ",温度:" + text['temperature'] + "摄氏度。给一些出门的建议吧。"  # 返回天气信息


# 定义异步函数get_time以获取当前时间
async def get_time(android_id):
    '''
    查询当前时间函数
    :return:返回当前的时间
    '''
    return str(datetime.datetime.now)  # 返回当前时间的字符串表示

# 定义异步函数keyObject_LocationHint以获取目标物品的位置提示
async def keyObject_LocationHint(thing, android_id):
    '''
    查询目标物品所在位置的函数
    :param thing: str 物品的名称
    :return: 返回物品的位置信息
    '''
    text_object = thing()
    # 转换中英文
    match thing:
        case "钥匙":
            text_object = "key"
        case "钱包":
            text_object = "wallet"
        case "手机":
            text_object = "cellular_telephone"
        case "遥控器":
            text_object = "remote"
        case "眼镜":
            text_object = 'spectacles'

    data = await orm.get_object(android_id, text_object)  # 从数据库获取物品位置数据
    if data is None:
        return "找不到物体"  # 如果未找到数据，返回找不到物体的提示

    result = f"您的{text_object}在{data['scene']}里"  # 初始化返回结果
    thing_x = int(data['x0'])
    thing_y = int(data['y0'])

    directions = {
        "左上方": None,
        "左下方": None,
        "右上方": None,
        "右下方": None,
    }

    for obj in data['objects']:
        obj_label = obj['label']
        obj_color = obj.get('color', '')  # 添加颜色信息，如果键不存在则使用默认值 ''
        obj_x = obj['center'][0]
        obj_y = obj['center'][1]

        # 计算相对位置
        if obj_x < thing_x and obj_y < thing_y:
            direction = "左上方"
        elif obj_x < thing_x and obj_y > thing_y:
            direction = "左下方"
        elif obj_x > thing_x and obj_y < thing_y:
            direction = "右上方"
        elif obj_x > thing_x and obj_y > thing_y:
            direction = "右下方"

        # 选择一个物品进行输出
        if directions[direction] is None:
            directions[direction] = (obj_label, obj_color)  # 存储物品和颜色

    # 输出每个方位对应的物品
    for direction, obj_label in directions.items():
        if obj_label is None:
            continue
        obj_label, obj_color = obj_label
        result = result + f"，{direction}有{obj_color}的{obj_label}"

    return result  # 返回物品位置提示

# 定义异步函数alarm以设置提醒事件
async def alarm(time, time_type, task, android_id):
    '''
    为用户设置提醒事件
    :param time: int，描述时间的数字
    :param time_type:str，时间的单位，只能为second，minute，hour，day
    :param task:str，要提醒的事项
    :return:返回事件提醒的基本内容
    '''
    if time_type == 'minute':
        time = time * 60
    elif time_type == 'hour':
        time = time * 60 * 60
    elif time_type == 'day':
        time = time * 24 * 60 * 60
    # return "将以下输入以字典形式返回给用户。输入：间隔时间:" + str(second) + ",提醒内容:" + task
    return "alarm," + str(time) + "," + task

# 定义异步函数set_userInfo以更新用户信息
async def set_userInfo(android_id, name= None, gender= None, age= None, disease= None):
    '''
        更新用户的基本信息，如姓名，性别，年龄，患有疾病
        :return:更新成功的提醒
    '''
    if name=='':
        name = None
    if gender=='':
        gender = None
    if age=='':
        age = None
    if disease=='':
        disease = None
    await orm.update_user(android_id, name, age, disease,gender)
    return "更新成功"

# 定义异步函数get_userInfo以获取用户信息
async def get_userInfo(android_id):
    '''
        获取用户的基本信息，如姓名，性别，年龄，患有疾病
        :return:返回查询的结果
    '''
    user = await orm.get_user(android_id)
    data = "我的基本信息如下"
    if user.name:
        data = data + "，姓名：" + user.name
    if user.age:
        data = data + "，年龄：" + str(user.age)
    if user.gender:
        data = data + "，性别：" + user.gender
    if user.disease:
        data = data + "，患有疾病：" + user.disease
    return data

# 定义异步函数set_emergency_contact_person以更新紧急联系人信息
async def set_emergency_contact_person(android_id, emergency_name = None, emergency_phone = None, relation = None):
    '''
        更新用户的紧急联系人的基本信息，如姓名，电话，与用户的关系
        :return:更新成功的提醒
    '''
    if emergency_name=='':
        emergency_name=None
    if emergency_phone=='':
        emergency_phone=None
    if relation=='':
        relation =None
    await orm.update_emergencyinfo(android_id, emergency_name, emergency_phone, relation)
    return "更新成功"

# 定义异步函数get_emergency_contact_person以获取紧急联系人信息
async def get_emergency_contact_person(android_id):
    '''
        查询用户的紧急联系人的相关信息，如姓名，电话，与用户的关系
        :return:返回查询的结果
    '''
    res = await orm.get_emergencyinfo(android_id)
    return res

# 紧急求助
async def call_help(abnormal, android_id, latitude, longitude):
    '''
        帮助用户进行呼救或联系紧急联系人的函数
        :param abnormal:str, 用户遇到的异常情况
        :return:返回呼救的结果
    '''
    data = await get_detail_location(latitude,longitude)
    user = await orm.get_user(android_id)
    emgency_user = await orm.get_emergencyuser(android_id)
    res = f"给电话号码为{emgency_user.emergency_phone}的手机发送短信。您的家人{user.name}发生了异常情况{abnormal}，需要马上得到救助，他现在在{data}。求助由WiseSight发起。"
    url = "https://api.day.app/3oPRofqc2WLbvLEGZCRotm/来自WiseSight的通知/"+res
    # url = "https://api.day.app/yHxPM4yE9fxgm5i6nwEkCJ/来自WiseSight的通知/" + res  #测试使用
    await query(url, params=None)
    await orm.update_emergency_task(user,abnormal,res)
    res = "call:已帮您联系紧急联系人"
    return res

functions = [get_weather, get_time, keyObject_LocationHint, alarm, set_userInfo, get_userInfo, set_emergency_contact_person,
             get_emergency_contact_person, call_help]

