import redis
import pickle
import cv2
import numpy 
from Camera_View_Get import ImgRead
import pickle



class MyRedis():
    # Redis_Host='192.168.2.229'##服务器
    Redis_Host="127.0.0.1"
    Redis_Port=8092
    Redis_DataBase=0
    redis_client=None
    def __init__(self):
        try:
            self.redis_client = redis.StrictRedis(
                host=self.Redis_Host, 
                port=self.Redis_Port, 
                db=self.Redis_DataBase)
            print("The Redis Is Readay")
        except Exception as error:
            print(f"The Redis Counnet Error:{error}")
            exit()
        

    def put_img(self,key,data):
        """
        key:键名,data:图片
        """
        try:

            frame_data = pickle.dumps(data)###序列化（dump）：将 Python 对象转换为字节流
            self.redis_client.set(key,frame_data)
            return True,key
        except Exception as error:
            return False, error
    def put_text(self,key,data):
        """
        key:键名,data:数据
        """
        try:
            self.redis_client.set(key,data)
            return True,key
        except Exception as error:
            return False, error
    def get(self,key):
        return self.redis_client.get(key)
    
    def R_Get(self,key):
        ###获取图片接口
        while  True: 
            im0=self.redis_client.get(key)
            # img=pickle.loads(im0)###转成数组
            if im0 is not None:
                # img=ImgRead().read(im0)# 
                img=pickle.loads(im0)###转成数组


                # print(type(im1))
                yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + img + b"\r\n"  
            else:
                yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" +  {} +b"\r\n"  
    def R_Yolo_Result_Get(self,key):
        return self.redis_client.get(key)
    
    def Delete(self,key):
        return self.redis_client.delete(key)
    
    def Post_List(self,key,value):
        try:
            self.redis_client.rpush(key,value)
            return True
        except Exception as error:
            print(error)
            return False
    def __del__(self):
        self.redis_client.close()
        print(f"EXIT !")


        


# if __name__=="__main__":
#     Re=MyRedis()
#     img=Re.get("sxxxImg")
#     if img is not None:
#         img=ImgRead().read(img)
#         if img is not None:
#             while True:
#                 cv2.imshow("Redis",img)
#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                         cv2.destroyAllWindows()


    