import cv2
from ultralytics import YOLO



class Yolo_Read():
    model="yolo11n.pt"
    def __init__(self,camera_index) -> None:
        self.cap=cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            exit()
    def yolo_img(self):
        while True:
            succse,img=self.cap.read()
            if not succse:
                break
            result=YOLO(self.model).predict(img)[0].plot()
            yield result



if __name__=="__main__":
    Obj=Yolo_Read(int(0))
    for img in Obj.yolo_img():

        cv2.imshow('Camera',img)
        cv2.waitKey(1)
