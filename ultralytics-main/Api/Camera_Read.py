import cv2
import os


class Camera():
    cap=None
    def __init__(self,cameraindex) -> None:
        self.cap=cv2.VideoCapture(cameraindex)
        if not self.cap:
            print("The Camera Not Found")
            exit()
    def img_get(self):
        succes,img=self.cap.read()
        if not succes:
            return None
        return img
    def releas(self):
        self.cap.release()

if __name__=="__main__":
    cameraindex=input("输入摄像头编号:[有多个摄像头时,从0，1，2，3开始测试]：")

    cap=Camera(int(cameraindex))
    print("程序执行过程中 按‘q’退出")
    while True:
        img=cap.img_get()
        if img is not None:
            cv2.imshow('Camera',img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                    cap.releas()
                    break
        else:
            break
    