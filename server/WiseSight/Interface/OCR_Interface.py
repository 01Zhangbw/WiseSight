from paddleocr import PaddleOCR
import os
from .Singleton import SingletonMeta

class OCR(metaclass=SingletonMeta):
    def __init__(self):
        self.model = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=True)  # 使用CPU预加载，不用GPU
        print('load ocr')

    def img_to_text(self, file):
        # ocr
        path = os.path.join('/home/cike/WiseSight/Temp', file.filename)
        with open(path, 'wb') as f:
            for line in file.file:
                f.write(line)
        text = self.model.ocr(path, cls=True)
        os.remove(path)
        try:
        # 处理文本内容
            result0 = text[0]  # 获取框数
            txts = [line[1][0] for line in result0]  # 获取文本
            multi_line_str = ' '.join(txts)  # 将文本数组转为多行字符串
            output_text = "文本的内容是：" + multi_line_str
            return output_text
        except:
            return "没有文本内容"


