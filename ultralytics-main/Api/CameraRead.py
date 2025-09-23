import cv2
from datetime import datetime
from ultralytics import solutions
from ultralytics import YOLO
import redis
import json
import numpy as np
import pickle





class Camera():
    """
    视频处理类
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_thickness = 2
    text_color = (255, 255, 255)  # 白色
    text_position = (10, 30)  # 左上角位置
    modelpt=r"D:\LaijinYOLO11\ultralytics-main\best.pt"
    line_points = [(0, 500), (1850, 500)]
    
    def __init__(self,viewform) -> None:
        print(solutions.__file__)
        route=int(viewform) if isinstance(viewform,int) else viewform
        self.cap=cv2.VideoCapture(route)

        self.counter = solutions.ObjectCounter(
        show=False,
        region=self.line_points,
        model=r"D:\LaijinYOLO11\ultralytics-main\best.pt",
        # show_in=False
        conf=0.7
    )

        self.yolo=YOLO(model=self.modelpt)
        if not self.checkroote():
            print(f"The Route {viewform} Is Not Found EXIT!")
            self.cap.release()
            exit()
        print(f"The Camera {viewform} Is Reading")
    def checkroote(self):
        return self.cap.isOpened()
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
            smoimg=cv2.resize(img,(0, 0), fx=0.5, fy=0.5)
            ret,codeimg=cv2.imencode(".jpg", smoimg)
            if ret:
                yield (b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + codeimg.tobytes() + b"\r\n")
            else:
                break
    def yolo_img(self):
        while True:
            succes,img=self.cap.read()
            if not succes:
                break
            yolo_img=self.counter.count(img)
            # yolo_img=self.yolo(source=img,show=False,conf=0.7,verbose=False)[0].plot()
            #cv2.putText(yolo_img, str(datetime.now().replace(microsecond=0)), self.text_position, self.font, self.font_scale, self.text_color, self.font_thickness)
            ret,codeimg=cv2.imencode(".jpg", yolo_img)
            # yield yolo_img
            if ret:
                yield (b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + codeimg.tobytes() + b"\r\n")
                # return codeimg
            else:
                break
        self.cap.release()
        cv2.destroyAllWindows()
    def release(self):
        return self.cap.release()
    def version(self):
        data={"solutions":solutions.__file__}
        return data
    def socket_img(self):
        while True:
            succes,img=self.cap.read()
            if not succes:
                break
            yolo_img=self.counter.count(img)
            # yolo_img=self.yolo(source=img,show=False,conf=0.7,verbose=False)[0].plot()
            #cv2.putText(yolo_img, str(datetime.now().replace(microsecond=0)), self.text_position, self.font, self.font_scale, self.text_color, self.font_thickness)
            ret,codeimg=cv2.imencode(".jpg", yolo_img)
            # yield yolo_img
            if ret:

                return codeimg
            else:
                break
            

class Redis_Img_Read():
    # redis_client = redis.StrictRedis(host='192.168.2.229', port=8092, db=0)
    DictKey="img"
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='192.168.2.229', port=8092, db=1)
        if not self.redis_client:
            print("Redis Is Error")
            exit()
    def get(self):
        return self.redis_client.get(self.DictKey)


if __name__=="__main__":
    Rd=Redis_Img_Read()
    while True:
        img=Rd.get()
        img=pickle.loads(img)
        # frame_bytes = json.loads(img)
                
        #         # 将字节数组转换为numpy数组
        # frame = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
        nparr = np.frombuffer(img, np.uint8)
        
        # 使用 OpenCV 解码图像数据
        img_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # 使用 cv2.IMREAD_COLOR 来确保加载彩色图像（如果有的话）
        cv2.imshow('Rediss',img_array)
        if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
   
cv2.destroyAllWindows()
# if __name__=="__main__":
#     Cameraroote=r"D:\LaijinYOLO11\2024-11-2-25002600现场视频2.mp4"
#     Cameraid=0
#     img=Camera(Cameraroote)
#     counter = solutions.ObjectCounter(
#             show=True,
#             region=img.line_points,
#             model=r"D:\LaijinYOLO11\ultralytics-main\best.pt",
#             # show_in=False
#             conf=0.7
            
#         )
#     while True:
#         pg=next(img.img())

#         im0=counter.count(pg)        
#         # cv2.imshow('cc',im0)
#         # cv2.waitKey(1)

        


    
