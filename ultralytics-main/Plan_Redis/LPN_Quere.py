from queue import Queue
from Celery import Celery_Read_Redis
import time
import json
import threading
from Redis import MyRedis
from MESApi import Post_LPN_MES
from collections import defaultdict
###创建队列存储代生成的LPN



class LpnQuere():
    
    MaxQuere=100  ###最大队列值100
    LPNQ=None ##队列实例
    def __init__(self):
        self.LPNQ=Queue(100)  ##创建队列，最大值=100
    
    def Get_Size(self):
        ###返回当前队列大小
        return self.LPNQ.qsize()
    def Get_LPNQ(self):
        ###取队列值
        return self.LPNQ.get()
    def Put_LPNQ(self,value):
        try:
            self.LPNQ.put(value)
            return True
        except Exception as error:
            return error
    def Clear_quere(self):
        ###清空队列
        ###2025.9.15 修改  在清空队列前  判断一下是否有其他未满足包装的图号需要生成包装
        with self.LPNQ.mutex:
            self.LPNQ.queue.clear()

class package_worker():
    ###包装队列工作
    package_data=[] ###包装数据
    QLPN=LpnQuere()###队列
    MESLPNTO=Post_LPN_MES()
    def __init__(self):
        pass
    def __package_sort(self,data):
        ###将获取到的标签数据排序  把不同物料 交叉排序
        ###主要用于一模双件时  让左右相邻
        if len(data)==0:
            return False
        else:
            for item in data:
                item['material']['description'] = str(item['material']['description'])
            
            # 2. 按name分组
            grouped = defaultdict(list)
            for item in data:
                grouped[item['material']['description']].append(item)
            
            # 3. 获取排序后的分组键（按name排序）
            sorted_keys = sorted(grouped.keys())
            
            # 4. 交叉合并各组元素
            result = []
            max_count = max(len(v) for v in grouped.values())  # 找到最大分组数量
            
            for i in range(max_count):
                for key in sorted_keys:
                    if i < len(grouped[key]):
                        result.append(grouped[key][i])
            
            # 输出结果
            # print(f"排序后的结果：{result}")
            # # for item in result:
            # #     print(item)
            return result
    
    def Update_package(self,data):
        if data:
            self.package_data=data
            print(f"包装进入{len(data)}")
            self.package_data=self.__package_sort(self.package_data)
            self.__Create_Q()
            return self.package_data
        print("No Package")
        return False
    def __Create_Q(self):
        
        for item in self.package_data:
            if item['material']['description']=='A2066372600冲压半成品': ###因为实物中图号差异问题 所以 再次把物料图号进行转换 为了和YOLO所对应
                item['material']['description']='A2066372600'
            self.QLPN.Put_LPNQ(item)
        print(f"队列装载完毕;总计装载了:{self.QLPN.Get_Size()}个")
        return self.QLPN.Get_Size()
    def StartWork(self,CreateList):
        ###开启包装和已识别的数据核对
        Yolo_Results_OBJ=Celery_Read_Redis()
        LPNOBJ=None###LPN对象
        LPNwhileCount=0
        RedisOBJ=MyRedis()##Redis对象
        # RedisOBJ.Delete('A2066372500')
        # RedisOBJ.Delete('TOA2066372500')
        Yolo_Results_OBJ.Redis_connet.put_text('MesQuereStatus','Runing')###更新队列开始标记
        while True:
            LPNwhileCount=0 ###当前LPN循环次数
            Yolo_Results=Yolo_Results_OBJ.Get_Redis_Results()###获取YOLO推理结果
            MesQuereStatus=self.Get_MesQuereStatus()###获取临时中断生产标识
            if Yolo_Results !='null':  
                Yolo_Results_Key_List=[ item['Name'] for item in json.loads(Yolo_Results)]
            else:
                if MesQuereStatus==True:##停止生产标识
                    self.QLPN.Clear_quere()
                    CreateList=[]
                    yield f"data: {json.dumps(CreateList)}\n\n"
                    break
                yield f"data: {json.dumps(CreateList)}\n\n"  # 空 SSE 消息
                time.sleep(0.3)
                continue

            if self.QLPN.Get_Size() >0 or LPNOBJ is not None: ##判断队列是否还有数据
                if LPNOBJ is None:###如果初始化 或者上一个任务已完成
                    LPNOBJ=self.QLPN.Get_LPNQ()###新取出LPN对象
                    LPN_name=LPNOBJ['name']###预制品LPN
                    LPN_material_description=LPNOBJ['material']['description']###预制品LPN物料名称
                    LPN_qty=LPNOBJ['qty']###LPN预制品需求数量
                    RedisOBJ.put_text(f"TO{LPN_material_description}",LPN_name)###Working TO Redis
                    RedisOBJ.put_text(f"{LPN_name}",int(LPN_qty)) ###LPN原始数量
                    for item in CreateList:
                        item['Working']='Y' if item['name']==LPN_name else 'F'


                if LPN_material_description in Yolo_Results_Key_List:###如果图号和识别的数据一致
                    Result=[ item for item in json.loads(Yolo_Results) if item['Name']==LPN_material_description] ###获取识别的IN 和 OUT 结果
                    Result_IN=Result[0]['IN']##出
                    Result_OUT=Result[0]['OUT']##进
                    Package_QRY=RedisOBJ.get(LPN_material_description) ###获取已生成包装的数量
                    Quantity=RedisOBJ.get(f'Quantity{LPN_material_description}')###获取不合格数量
                    if Package_QRY==None:
                        Package_QRY=0
                    else:
                        Package_QRY=int(Package_QRY)
                    if Quantity==None:
                        Quantity=0
                    else:
                        Quantity=int(Quantity)
                    ###记录本次LPN还剩多少满包装
                    RedisOBJ.put_text(f"TO{LPN_name}",int(Result_IN-Package_QRY-Quantity)-int(LPN_qty))
                    ###处理临时中断生成
                    if MesQuereStatus==True:###如果获取临时中断生产标识=True
                        ###1.把当前LPN计算出已合格数量
                        ###2.把当前中断生产时候 使用的数量增加到包装数量 2025-09-16 更新
                        ###3.发送报文=》MES
                        ###4.清空队列
                        ###5.后续LPN状态更新
                        ###6.退出循环

                        ###判断已取出队列的值 是否有数量>0
                        if (int(Result_IN)-int(Package_QRY)-int(Quantity))>0:###判断是否大于0  如果=0的话,不传报文
                            RedisOBJ.put_text(LPN_material_description,(Result_IN-Package_QRY-Quantity+Package_QRY))##2
                            self.MESLPNTO.POST(LPN_name,(Result_IN-Package_QRY-Quantity))###1+2
                        self.QLPN.Clear_quere()###3.清空队列
                        for item in CreateList:
                            if item['name']==LPN_name:
                                item['Finish']='Y' 
                                item['status']='USED'  if (item['name']==LPN_name or item['Finish']=='Y') else 'Delete'
                        sse_data = f"data: {json.dumps(CreateList)}\n\n"
                        RedisOBJ.Delete(f"{LPN_name}") ###中断生产时把LPN清空
                        RedisOBJ.Delete(f"TO{LPN_name}") ###中断生产时把TOLPN清空
                        yield  sse_data
                        break ###5

                    if int(Result_IN-Package_QRY-Quantity)>=int(LPN_qty):###大于则满包装
                        print(f"LPN:{LPN_name}已经满包装")
                        print(f"当前队列数量:{self.QLPN.Get_Size()}")
                        for item in CreateList:
                            if item['name']==LPN_name:
                                item['Finish']='Y' 
                                item['status']='USED' 

                        LPNOBJ=None###重置任务
                        RedisOBJ.Delete(f"TO{LPN_name}")
                        RedisOBJ.Delete(f"{LPN_name}")
                        RedisOBJ.Delete(f"TO{LPN_material_description}")
                        if Package_QRY==None:
                            ToReQTY=LPN_qty
                        else:
                            ToReQTY=int(Package_QRY)+int(LPN_qty)
                        RedisOBJ.put_text(LPN_material_description,ToReQTY)
                        self.MESLPNTO.POST(LPN_name,LPN_qty)
                        LPNwhileCount=0
                    else:
                        LPNwhileCount+=1
                        # print(f"\r当前LPN循环次数:{LPNwhileCount};正在进行任务LPN:{LPN_name};LPN_Name:{LPN_material_description};包装数量:{LPN_qty};Yolo推理数量:{Result_IN};YOLO推理列表:{Yolo_Results_Key_List};是否在推理结果中:{LPN_material_description in Yolo_Results_Key_List};",end=" ")
                        sse_data = f"data: {json.dumps(CreateList)}\n\n"
                        yield  sse_data
                        continue
                LPNwhileCount+=1
                if MesQuereStatus==True:###如果获取到中断生产标识
                    ###发生在如果推理的数据,或者还没有推理的数据和 LPN不匹配 则清空待生产列表
                    self.QLPN.Clear_quere()###清空队列
                    CreateList=[]###清空列表
                    sse_data = f"data: {json.dumps(CreateList)}\n\n"
                    yield  sse_data
                    break ###退出循环
                # print(f"\r当前LPN循环次数:{LPNwhileCount};正在进行任务LPN:{LPN_name};LPN_Name:{LPN_material_description};包装数量:{LPN_qty};YOLO推理列表:{Yolo_Results_Key_List};是否在推理结果中:{LPN_material_description in Yolo_Results_Key_List};",end=" ")
                time.sleep(1)
                sse_data = f"data: {json.dumps(CreateList)}\n\n"
                yield  sse_data
                
            else:
                RedisOBJ.Delete(f"TO{LPN_name}")
                RedisOBJ.Delete(f"{LPN_name}")
                RedisOBJ.Delete(f"TO{LPN_material_description}")
                # self.MESLPNTO.POST(LPN_name,LPN_qty)###MES发送报文
                for item in CreateList:
                    item['Working']='F' 
                sse_data = f"data: {json.dumps(CreateList)}\n\n"
                yield  sse_data
                print(f"所有任务已完成;队列数量{self.QLPN.Get_Size()}")
                break
                
    def Start_Threading(self,CreateList):
        threading_1=threading.Thread(target=self.StartWork,args=(CreateList,))
        threading_1.daemon=True
        threading_1.start()
    def NUllStart(self,CreateList):
        sse_data = f"data: {json.dumps(CreateList)}\n\n"
        yield  sse_data
    
    def Get_MesQuereStatus(self):
        result=self.MESLPNTO.Redis_Client.get('MesQuereStatus')
        if result:
            result=result.decode('utf-8')
            if result=='Runing':
                # print(f"MesQuereStatus:{result}")
                return False
            else:
                # print(f"MesQuereStatus:{result}")
                return True
        # print(f"MesQuereStatus:{result}")
        return True
    def __del__(self):
        self.QLPN.Clear_quere()
        print(f"队列已清空所有任务;Quere_Size:{self.QLPN.Get_Size()}")
    
    
    


# if __name__=="__main__":
#     Q=package_worker()
#     print(Q.Get_MesQuereStatus())