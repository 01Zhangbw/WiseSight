import json

from database.models import Users, EmergencyInfo, Objects, History, Emergencys


async def create_user(id: str):
    obj = await Users.create(android_id=id)
    emergencyInfo = await EmergencyInfo.create(user=obj)
    print(emergencyInfo)
    return obj


async def get_user(id: str):
    obj = await Users.filter(android_id=id)
    if obj:
        return obj[0]
    return None


async def update_user(id: str, name: str = None, age: int = None, disease: str = None, gender: str = None):
    obj = await Users.filter(android_id=id)
    user = obj[0]
    if name:
        user.name = name
    if age:
        user.age = age
    if disease:
        user.disease = disease
    if gender:
        user.gender = gender
    await user.save()
    return "finish"


async def update_emergencyinfo(id: str, emergency_name: str = None, emergency_phone: str = None, relation: str = None):
    obj = await EmergencyInfo.filter(user_id=id)
    enmergencyinfo = obj[0]
    if emergency_name:
        enmergencyinfo.emergency_name = emergency_name
    if emergency_phone:
        enmergencyinfo.emergency_phone = emergency_phone
    if relation:
        enmergencyinfo.relation = relation
    await enmergencyinfo.save()
    return "finish"


async def get_emergencyuser(id: str):
    obj = await EmergencyInfo.filter(user_id=id)
    if obj:
        return obj[0]
    return None


async def get_emergencyinfo(id: str):
    obj = await EmergencyInfo.filter(user_id=id)
    emergencyinfo = obj[0]
    data = ""
    if emergencyinfo.emergency_name:
        data = data + "紧急联系人的基本信息如下，紧急联系人姓名：" + emergencyinfo.emergency_name
    if emergencyinfo.emergency_phone:
        data = data + ", 紧急联系人电话：" + emergencyinfo.emergency_phone
    if emergencyinfo.relation:
        data = data+ ", 紧急联系人与用户的关系：" + emergencyinfo.relation
    if data == "":
        return "没有信息"
    return data


async def create_or_update_object(id: str, name: str, scene: str, x0: int, y0: int, objects: str):
    obj = await Objects.filter(user_id=id, name=name)
    if obj:
        object = obj[0]
        object.scene = scene
        object.x0 = x0
        object.y0 = y0
        object.objects = objects
        await object.save()
    else:
        await Objects.create(user_id=id, name=name, scene=scene, x0=x0, y0=y0, objects=objects)
    return "存储成功"


async def get_object(id: str, name: str):
    obj = await Objects.filter(user_id=id, name=name)
    if obj:
        object = obj[0]
        data = {}
        data["scene"] = object.scene
        data["x0"] = object.x0
        data["y0"] = object.y0
        data["objects"] = json.loads(object.objects)
        return data
    else:
        return None


async def update_history(id: str, history: str):
    obj = await Users.filter(android_id=id)
    user = obj[0]
    await History.create(user=user, history=history)
    print("success")


async def update_emergency_task(user: Objects, type: str, context: str):
    await Emergencys.create(user=user, type=type, context=context)
    print("success")


