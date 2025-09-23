from Redis import MyRedis
import json
import time




class Celery_Read_Redis():
    ###读取Yolo结果,并格式化
    def __init__(self):
        ###实例化Redis
        self.Redis_connet=MyRedis()
        if self.Redis_connet.redis_client is None:
            print(f"Redis connect Error")
    def Get_For_Key(self,key):
        ###传入Redis的Key取出数据
        results=self.Redis_connet.R_Yolo_Result_Get(key)
        if results:
            results=self.To_UTF(results)
            return results
        else:
            return None
    def To_UTF(self,value):
        ###Bytes转UTF-8
        return value.decode('utf-8')
    def To_Json(self,value):
        ###实例化JSON
        if value:
            return json.loads(value.replace("'",'"'))
        return None
    def Json_To_List(self,value):
        ###把Json格式化成列表格式
        if value:
            keys=value.keys()
            Result_List=[]
            for key in keys:
                temp=({'Name':key,'IN':value[key]['IN'],'OUT':value[key]['OUT']})
                Result_List.append(temp)
            return Result_List
        return None
    def Streaming_Redis_Results(self):
        ###创建Streaming流推送数据
        while True:
            time.sleep(0.2)
            results=self.Get_For_Key("Yolo_Results") ##获取存入Redis中的已识别数据
            results=self.To_Json(results)###转成Json
            Results=self.Json_To_List(results)###转成列表
            PResults=self.__Package_Redis_QTY_Get(Results)
            sse_data = f"data: {json.dumps(PResults)}\n\n"
            yield sse_data
    def __Package_Redis_QTY_Get(self,resuls):
        ###传入已识别的数据,扣减已生成包装数量
        if resuls:
            for item in resuls:
                MESQTY=None
                YoloQTY=None
                Package_QRY=self.Redis_connet.get(item['Name']) ###获取已生成包装的数量
                WorkingFor=self.Redis_connet.get(f"TO{item['Name']}")
                Quantity=self.Redis_connet.get(f'Quantity{item['Name']}')###获取不合格数量
                if Quantity==None:
                    Quantity=0
                else:
                    Quantity=int(Quantity)
                if Package_QRY==None:
                    Package_QRY=0
                else:
                    Package_QRY=int(Package_QRY)
                if WorkingFor is None:
                    WorkingFor="未找到LPN"
                else:
                    WorkingFor=WorkingFor.decode('utf-8')
                    MESQTY=self.Redis_connet.get(WorkingFor)
                if MESQTY is not None:
                    MESQTY=MESQTY.decode('utf-8')
                    YoloQTY=self.Redis_connet.get(f"TO{WorkingFor}")
                    if YoloQTY is not None:
                        YoloQTY=YoloQTY.decode('utf-8')
                else:
                    MESQTY=" "
                    YoloQTY=" "
                item['PackageQTY']=Package_QRY
                item['Working']=WorkingFor
                item['MESQTY']=MESQTY
                item['YoloQTY']=YoloQTY
                item['Quantity']=Quantity
        return resuls
    
    def Get_Redis_Results(self):
        results=self.Get_For_Key("Yolo_Results") ##获取存入Redis中的已识别数据
        results=self.To_Json(results)###转成Json
        Results=self.Json_To_List(results)###转成列表
        return json.dumps(Results)




# if __name__=="__main__":
#     OBJ=Celery_Read_Redis()
#     Results=OBJ.Get_For_Key("Yolo_Results")
#     Results=OBJ.To_Json(Results)
#     print(Results['A2066372500'])