import cv2
import redis
import pickle
import json
import time

# 连接到Redis服务器
redis_client = redis.StrictRedis(host='192.168.2.229', port=8092, db=0)

# 打开摄像头（0表示默认摄像头）
cap = cv2.VideoCapture(0)
count=0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 将帧数据转换为字节数组
    frame_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
    
    # 使用pickle序列化帧数据（你也可以使用其他序列化方法）
    frame_data = pickle.dumps(frame_bytes)
    
    # 将帧数据保存到Redis中
    redis_client.set('camera_frame', frame_data)
    
    # 延迟以减少帧率（可选）
    # time.sleep(0.1)
    count+=1
    print("\r" ,f"{ count }Img To Redis Is Ok",end='',flush=True)
    # count+=1

cap.release()