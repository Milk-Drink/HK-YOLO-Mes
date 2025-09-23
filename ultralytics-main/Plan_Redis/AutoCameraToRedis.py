import cv2
import threading
import pickle
from queue import Queue
from datetime import datetime
import redis
import time
from HKCamera import HKCam
import multiprocessing


##读取视频流并保存到Redis数据库中

class ViewPath:
    """
    构造时 传参\n
    1.队列大小，默认=10,int\n
    2.视频流地址/摄像头索引\n
    3.Redis数据库实例\n
    4.Redis数据库地址\n
    5.Redis数据库端口\n
    6.Redis存入的数据Key值\n
    
    """
    def __init__(self,queue:int,viewpath:any,redis_db:int,redis_host:str,redis_port:int,redis_put_key:str,HKIP:str,HKUSER:str,HKPW:str):
        ####队列配置####
        self.queue=multiprocessing.Queue(queue)###创建队列  最大值=100

        ####视频流配置####  RTSP 2025-09-17 使用海康官方SDK后 弃用
        self.viewpath=viewpath
        self.cap=self.__create_camera_client()##读取视频校验
        
        ###海康SDK方法

        self.HKIP=HKIP  ###海康摄像头IP
        self.HKUSER=HKUSER ###海康摄像头用户
        self.HKPW=HKPW  ###海康摄像头密码
        if viewpath=="HK":###如果使用海康SDK进行获取图像数据
            self.HIK=self.__Create_HK_Camera() ###摄像头对象

        #####Redis配置#####
        self.redis_db=redis_db
        self.redis_host=redis_host
        self.redis_port=redis_port
        self.redis_put_key=redis_put_key##Redis数据库的值
        #初始化校验
        self.redis_client=self.__create_redis_client()
        ####计数器####
        self.redis_Put_data_count=0
    def __Create_HK_Camera(self):
        self.HIK= HKCam(self.HKIP,self.HKUSER,self.HKPW)
        return self.HIK
    def __create_redis_client(self):
        """
        初始化创建Redis链接
        """
        try:
            self.redis_client = redis.StrictRedis(
                host=self.redis_host, 
                port=self.redis_port, 
                db=self.redis_db)##创建Redis链接
            self.redis_client.ping()
            self.redis_client_Is_Ready=True
            print("The Redis Is Ready")
            return self.redis_client
        except redis.ConnectionError as error:
            print(f"The Redis NetWork Link Connect Error:{error}")
            raise
        except Exception as error:
            print(f"The Redis Connect Error:{error}")
            raise
    def __create_camera_client(self):
        try:
            self.cap=cv2.VideoCapture(int(self.viewpath) if isinstance(self.viewpath,int) else self.viewpath)##创建读取视频流
            if self.cap.isOpened():
                self.cap_Is_Ready=True
                print(f"The ViewPath {self.viewpath}  Is Ready")
                return self.cap
            raise self.cap_Is_Ready
        except Exception as error:
            print(f"The ViewPath {self.viewpath} Cannot Read Error:{error}")
            # self.cap_Is_Ready
            return False
    def __queue_size_get(self):
        """
        类内部使用\n
        返回当前队列已存在数据大小
        """
        while True:
            print("\r",f"Queue : Now Size :{ self.queue.qsize() }",end='',flush=True)
            time.sleep(1)
        # return self.queue.qsize()
    def __queue_put(self,data):
        """
        类内部使用\n
        往队列里放入值
        """
        try:
            self.queue.put(data)
            return True
        except Exception as error:
            print(f"Queue Put Error:[{error}]")
            return False
    def __queue_get(self):
        """
        类内部使用\n
        从队列中获取值
        """
        return self.queue.get()
    def __redis_put(self,data):
        """
        类内部使用\n
        数据放入Redis
        """
        try:
            self.redis_client.set(self.redis_put_key,pickle.dumps(data))
            print("\r",f"Redis_ Count:{self.redis_Put_data_count}  fps:{cv2.CAP_PROP_FPS} The Data Is Put Redis:Now:{datetime.now().replace(microsecond=0)}",end='',flush=True)
            # print("Redis _Data Put Is OK")
            self.redis_Put_data_count+=1
        except Exception as e:
            print(f"Error {e}")
    def _cap_img_get(self):
        """
        构造器函数，获取视频流每一帧数据
        通过摄像头获取图像
        放到队列里
        """
        ###2025-09-17 修改
        ###根据传入的viewpath判断  
        # 如果开头是rtsp  则使用CV2进行解析  
        # 如果传入的是视频 则用 CV2进行解析 
        # 如果传入的是HK  则启用 海康SDK解析
        
            
        while True: 
            if self.viewpath!='HK':
                ret,CImg=self.cap.read()
            else:
                ret,CImg=self.HIK.read()
            target_size = (1920, 1080)
            CImg = cv2.resize(CImg, target_size)
            # self.redis_put_key=str(datetime.now().replace(microsecond=0))
            if not ret:
                break
            if int(self.queue.qsize())>1:
                
                self.__queue_get()
            else:
                self.__queue_put(CImg)
            # break
    def _Cimg_TO_Code(self):
        """
        从队列中获取图像 编码 并呼叫存储函数
        """
        while True:
            Img=self.__queue_get()
            DImg=cv2.imencode(".jpg", Img)[1]
            self._DImg_To_B(DImg)

    def _DImg_To_B(self,Dimg):
        self.__redis_put(Dimg.tobytes())
    
    def Main(self):
        """
        启动函数
        线程1:读取视频流 帧 并放在队列中
        线程2:从队列中读取 帧 并发送到Redis
        线程3:跟踪队列
        """
        self.task1=threading.Thread(target=self._cap_img_get)
        self.task2=threading.Thread(target=self._Cimg_TO_Code)
        self.task3=threading.Thread(target=self.__queue_size_get)
        ###
        self.task1.start()
        self.task2.start()
        self.task3.start()

    def __del__(self):
        """
        无论何时退出时 都执行以下操作
        """
        if self.cap_Is_Ready:
            self.cap.release()##关闭CV2
        if self.redis_client_Is_Ready:
            self.redis_client.close()##关闭Redis
        if self.HIK:
            self.HIK.release()###释放摄像头资源

        



if __name__=="__main__":
    queuesize=2

    Camera_rtsp_url7="rtsp://admin:a1234567@192.168.1.64:554/Streaming/Channels/101?transportmode=unicast"
    # # viewpath=0
    # viewpath=Camera_rtsp_url7
    # viewpath=0
    viewpath= r"D:\LaijinYOLO11\2024-11-2-25002600现场视频2.mp4"
    viewpath="HK"
    Redisdb=0
    # redis_host="192.168.2.229" ##服务器
    redis_host="127.0.0.1"
    redis_port=8092
    redis_put_key="sxxxImg"

    HKIP="192.168.1.64"
    HKUSER="admin"
    HKPW="a1234567"



    OBj=ViewPath(queuesize,viewpath,Redisdb,redis_host,redis_port,redis_put_key,HKIP,HKUSER,HKPW)
    OBj.Main()
