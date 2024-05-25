import os
import tempfile
import ffmpeg
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from .Singleton import SingletonMeta


class FunASR(metaclass=SingletonMeta):
    def __init__(self, device="cuda:0"):  # 好像只能用cuda 0
        self.inference_16k_pipline = pipeline(
            task=Tasks.auto_speech_recognition,
            model='/home/cike/LJJ/FunASR/model/speech_UniASR-large_asr_2pass-zh-cn-16k-common-vocab8358-tensorflow1-offline',
            device=device)
        self.inference_pipline = pipeline(
            task=Tasks.punctuation,
            model='/home/cike/LJJ/FunASR/model/punc_ct-transformer_zh-cn-common-vocab272727-pytorch',
            model_revision="v1.1.7",
            device=device)
        print('load funasr')


    def convert_format(self, input):
        # 生成一个临时文件名，扩展名为 .amr
        with tempfile.NamedTemporaryFile(suffix='.amr') as f:
            f.write(input)
            ffmpeg.input(f.name).output('/home/cike/WiseSight/Temp/temp.wav').run()
        # 读取所有二进制数据
        with open('/home/cike/WiseSight/Temp/temp.wav', 'rb') as file:
            data = file.read()
        os.remove('/home/cike/WiseSight/Temp/temp.wav')
        return data


    def audio_to_text(self, input):
        #
        try:
            data = self.convert_format(input)
            rec_result = self.inference_16k_pipline(data)
            result = self.inference_pipline(text_in=rec_result['text'])
            return result['text']
        except:
            return None



