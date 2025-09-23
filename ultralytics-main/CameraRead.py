import cv2
from datetime import datetime
from ultralytics import solutions
from ultralytics import YOLO






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
                return False,None
            yolo_img=self.counter.count(img)
            # yolo_img=self.yolo(source=img,show=False,conf=0.7,verbose=False)[0].plot()
            #cv2.putText(yolo_img, str(datetime.now().replace(microsecond=0)), self.text_position, self.font, self.font_scale, self.text_color, self.font_thickness)
            ret,codeimg=cv2.imencode(".jpg", yolo_img)
            # yield yolo_img
            if ret:

                return True,codeimg
            else:
                break
            
class ImgYolo:
    line_points = [(0, 500), (1850, 500)]
    count_img:int
    def __init__(self):
        self.counter = solutions.ObjectCounter(
        show=False,
        region=self.line_points,
        model=r"D:\LaijinYOLO11\ultralytics-main\best.pt",
        # show_in=False
        conf=0.7)
    def reasoning(self,img):
        yolo_img=self.counter.count(img)
        return yolo_img
        ret,codeing=cv2.imencode(".jpg",yolo_img)
        if ret:
            return yolo_img


    

if __name__=="__main__":
    camera=0
    cap=cv2.VideoCapture(0)
    objy=ImgYolo()
    assert cap.isOpened(),f"The Camera [{camera} Count Opened]"
    while True:
        ret,img=cap.read()
        if not ret:
            break
        yimg=objy.reasoning(img)

        cv2.imshow('camera',yimg)
        cv2.waitKey(1)
    cap.release()
    cv2.destroyAllWindows()
    

        
        


    
