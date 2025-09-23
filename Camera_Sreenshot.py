from File_Make import Files
import cv2
from datetime import datetime
import time


def view_read(viewpath,screenshoppath):
    cap=cv2.VideoCapture(viewpath)
    imgcount=0
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    print(f"Frame Size: {frame_width}x{frame_height}")
    while cap.isOpened():
        success, frame = cap.read()
        if success:
            cv2.imshow('Camera', frame)
            if cv2.waitKey(1) & 0xFF == ord('w'):
                cv2.imwrite(screenshoppath+"/"+str(imgcount)+".jpg", frame)
                print(f"当前画面截图成功，保存的地址：{screenshoppath+"/"+str(imgcount)+".jpg"}")
                imgcount += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break        
    cap.release()  # 释放摄像头资源
    cv2.destroyAllWindows()  # 关闭OpenCV窗口


if __name__=="__main__":
    viewpath=r"./2025-09-17现场生产视频.mp4"
    screenshoppath=r"./Camera_screenshot"
    osclass=Files(screenshoppath)
    if len(osclass.files())>0:
        inputvalue=input(f"当前截图目录下有文件{len(osclass.files())}个；是否清空历史数据:")
        if inputvalue=="Y":
            osclass.files_remove_all(osclass.files())
        if inputvalue =="U":
            while True:
                rename=input("输入批量重命名的名称：")
                if len(rename)!=0:
                    break
            osclass.files_rename_all(rename)
    view_read(viewpath,screenshoppath)
    

    