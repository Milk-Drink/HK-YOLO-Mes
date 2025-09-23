from Camera_View_Get import Camera,ImgRead
from Redis import MyRedis
from datetime import datetime
import cv2
import threading


def main():
    CA=Camera(0)
    
    RI=MyRedis()
    while True:
        img=CA.img_code()
        RI.put_img("img",img)


def readredis():
    RB=MyRedis()
    while True:
        img=RB.get("YOLO_IMG")
        if img is not None:
            img=ImgRead().read(img)
            if img is not None:
                cv2.imshow("Redis",img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                        cv2.destroyAllWindows()
                        break
        
        


if __name__=="__main__":
    # task1=threading.Thread(target=main)
    task2=threading.Thread(target=readredis)
    # task1.start()
    task2.start()
    # task1.join()
    task2.join()