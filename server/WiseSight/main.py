import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3,4,5,6,7"
from fastapi import FastAPI, UploadFile, Request
import uvicorn
from Controller.Agent import Agent
from tortoise.contrib.fastapi import register_tortoise
from database.settings import TORTOISE_ORM
import aioredis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import orm

from typing import List, Union
# from pydantic import BaseModel
#
# class Message(BaseModel):
#     history: Union[List[dict], None] = None
#     file: UploadFile

agent = Agent()
app = FastAPI()

async def init_redis():
    return await aioredis.from_url("redis://localhost")

# 初始化 APScheduler
scheduler = AsyncIOScheduler()

# 存储数据到 Redis，并设置过期时间
async def store_data_to_redis(key, value, expires=600):
    await app.state.redis.set(key, value, ex=expires)

# 从 Redis 获取数据
async def get_data_from_redis(key):
    return await app.state.redis.get(key)

# 定时将数据从 Redis 存储到数据库，并从 Redis 中删除
async def store_data_to_database(redis):
    keys = await redis.keys('history*')
    for key in keys:
        ttl = await redis.ttl(key)
        # 如果过期时间小于等于480，表示数据已经2分钟没有更新
        if ttl <= 480:
            # 存储到数据库，并从 Redis 中删除该键
            data = await get_data_from_redis(key)
            await orm.update_history(key.decode()[7:],data.decode())
            await redis.delete(key)

# 初始化
@app.on_event("startup")
async def startup():
    app.state.redis = await init_redis()
    scheduler.start()
    # 每分钟检查一次 Redis 中的数据
    scheduler.add_job(store_data_to_database, 'interval', minutes=1, args=[app.state.redis])

# 清理
@app.on_event("shutdown")
async def shutdown():
    await app.state.redis.close()
    scheduler.shutdown()


register_tortoise(
    app,
    config=TORTOISE_ORM,
    # generate_schemas=True,  # 如果数据库为空，则自动生成对应表单，生产环境不要开
    # add_exception_handlers=True,  # 生产环境不要开，会泄露调试信息
)


@app.get("/chatglm_test", tags=["test"], summary="文字单轮")
async def test(test: str, request: Request, history: str = None):
    data = await get_data_from_redis("history"+request.headers.get("id"))
    if data:
        history = data.decode()
    else:
        history = None
    print(history)
    res = await agent.single_chat(test, request.headers.get("id"),
                                  request.headers.get("latitude"), request.headers.get("longitude"), history)
    await store_data_to_redis("history"+request.headers.get("id"), str(res['history']))
    return res


@app.post("/uploadFile_test", tags=["test"], summary="上传文件")
async def create_upload_file(file: UploadFile):
    path = os.path.join('/home/cike/WiseSight/tests', file.filename)
    print(path)
    with open(path, 'wb') as f:
        for line in file.file:
            f.write(line)
    return {"filename": file.filename}


@app.post("/send_audio", tags=["正式API"], summary="对话")
async def send_audio(audio: UploadFile, request: Request, history: str = None):
    data = await get_data_from_redis("history" + request.headers.get("id"))
    if data:
        history = data.decode()
    else:
        history = None
    res = await agent.chat_by_audio(audio.file.read(), request.headers.get("id"),
                                    request.headers.get("latitude"), request.headers.get("longitude"), history)
    await store_data_to_redis("history"+request.headers.get("id"), str(res['history']))
    return res


@app.post("/ocr_qa", tags=["正式API"], summary="OCR问答")
async def ocr_qa(audio: UploadFile, text: str, request: Request):
    res = await agent.ocr_q_a(audio.file.read(), text, request.headers.get("id"),
                              request.headers.get("latitude"), request.headers.get("longitude"))
    return res


@app.post("/test_ocr", tags=["正式API"], summary="OCR", description="OCR上传图片")
async def send_ocr(file: UploadFile, request: Request):
    text = agent.ocr_data(file)
    return text


@app.post("/object_detection", tags=["正式API"], summary="目标检测上传数据")
async def object_detection(file: UploadFile, request: Request):
    text = await agent.has_object_or_not(file.file.read(), request.headers.get("id"))
    return text

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    
    uvicorn.run("main:app", host="0.0.0.0", port=28080, reload=False)
# ssh -p 2028 cike@202.38.247.79 -L 28080:localhost:28080
