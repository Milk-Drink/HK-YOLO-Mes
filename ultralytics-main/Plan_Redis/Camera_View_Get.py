import cv2
from datetime import datetime
import pickle
import numpy




class Camera():

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_thickness = 2
    text_color = (255, 255, 255)  # 白色
    text_position = (10, 30)  # 左上角位置
    def __init__(self,viewform) -> None:
        route=int(viewform) if isinstance(viewform,int) else viewform
        self.cap=cv2.VideoCapture(route)
    def img(self):
        while True:
            succes,img=self.cap.read()
            if not succes:
                break
            cv2.putText(img, str(datetime.now().replace(microsecond=0)), self.text_position, self.font, self.font_scale, self.text_color, self.font_thickness)
            yield img
    def img_code(self):
        while True:
            succes,img=self.cap.read()
            if not succes:
                break
            cv2.putText(img, str(datetime.now().replace(microsecond=0)), self.text_position, self.font, self.font_scale, self.text_color, self.font_thickness)
            ret,codeimg=cv2.imencode(".jpg", img)

            if ret:
                return codeimg.tobytes()
            else:
                break
    def releas(self):
        self.cap.release()


class ImgRead():
    def __init__(self):
        pass
    def read(self,rimg):
        if len(rimg) !=0:
            img=pickle.loads(rimg)
            nparr = numpy.frombuffer(img, numpy.uint8)
            # 使用 OpenCV 解码图像数据
            img_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # 使用 cv2.IMREAD_COLOR 来确保加载彩色图像（如果有的话）
            succe=cv2.imwrite('./123.jpg',img_array)
            return img_array
        


