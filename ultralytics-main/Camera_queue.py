from queue import Queue
import cv2
import threading
import time



class ImgQueue:
    """
    图片队列
    """
    frame_queue=None #队列
    frame_look=None #队列锁
    frame_check=False ###初始化校验是否通过

    def __init__(self,size:int):
        assert isinstance(size,int),f"The Queue_Size Must INT Not{size}"
        self.frame_queue=Queue(maxsize=size)
        self.frame_look=threading.Lock()
        print("Queue Look Is Ready")
    def queue_check(self): 
        """
        队列初始化校验
        """
        if self.frame_queue!=None and self.frame_look !=None:
            self.frame_check=True#更新初始化后状态啊
            return True
        print("The Queue Not Make,Reload Created Queue Object")
        return False
    def queue_size_get(self):
        if not self.frame_check:
            return self.queue_check()
        return self.frame_queue.qsize()
    def queue_get(self):
        try:
            if not self.frame_check:
                return self.queue_check()
            if self.queue_size_get()==0:
                print("The Queue`s Not Data Wait....")
                return 0

            return self.frame_queue.get()

        except Exception as error:
            print(error)
            
    def queue_obj_get(self):
        return self.frame_queue
    def queue_put(self,data):
        if not self.frame_check:
            return self.queue_check()
        try:
            self.frame_queue.put(data)
            return True
        except Exception as error:
            print(f"Queue_Put Has Error:{error}")
            return False
        # finally:
        #     print("The Queue is Puting Data")

def put(obj):
    while True:
        obj.queue_put(2)
        time.sleep(2)
        print(f"The Queue NSize {obj.queue_size_get()}")
def get(obj):
    while True:
        result = obj.queue_get()
        print(f"The Queue NGet {result}")
        time.sleep(3)

if __name__=="__main__":
    qusize=10
    Rqueue=ImgQueue(qusize)

    print(Rqueue.queue_check())#初始化校验，检查构造器
    taska=threading.Thread(target=put,args=(Rqueue,))
    taskb=threading.Thread(target=get,args=(Rqueue,))
    taska.start()
    taskb.start()
    # Rqueue.queue_put(3333)
    # print(Rqueue.queue_get())
    # print(Rqueue.frame_queue.qsize())

            
            