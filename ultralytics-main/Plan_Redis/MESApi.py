import requests
from Celery import  Celery_Read_Redis
import json
from Redis import MyRedis
from datetime import datetime



class Get_Work_Orders():
    ###获取工单列表
    url="http://192.168.2.50:9020/rest/lot_pre_products/get_lot_pre_list_by_wo?workOrderNo={}&refWoFlag={}"
    Cookie={"SESSION":"6a8418fa-1982-44c8-a7de-1c611c601908"}
    # sort_field='name' ##LPN
    # ascending='true'##true=从小到大  false=从大到小
    refWoFlag=True ###获取一模双件数据
    
    def __init__(self):
        pass

    def Get(self,WorkOrder):
        ###传入工单返回预制品标签列表
        if WorkOrder:
            Results=requests.get(url=self.url.format(WorkOrder,self.refWoFlag),cookies=self.Cookie)
            print("URL:",self.url.format(WorkOrder,self.refWoFlag))
            if int(Results.status_code)==200:
                return Results.json()
            return None
        print("未输入有效工单数据")
        return False
    def To_Json(self,GetData):
        if GetData is None:
            return '未找到预制品LPN'
        if GetData==False:
            return '工单不正确'
        else:
            return GetData
    def Get_Data(self,WorkOrder):
        res=self.Get(WorkOrder)
        return self.To_Json(res)



class Post_LPN_MES():
    url="http://192.168.2.50:9020/rest/mes/common_interface"
    Redis_Client=MyRedis()
    def __init__(self):
        pass
    
    def POST(self,lpn,qty):
        data=json.dumps({
        "messageId":"C0A8F8115ACF399C9A07762ACDBD153F",
        "tag":"auto_label_print",
        "content":{
            "lpn":f"{lpn}",
            "from_type":"88",
            "qty":f"{qty}"
        }
    })
        Re=requests.post(url=self.url,data=data)
        if Re.status_code==200:
            Re=Re.json()
            if Re.get('ResultType')==True:
                results={"MesResult":"True","CreateTime":str(datetime.now().replace(microsecond=0)),"ForData":data,"URL":self.url,"Method":"POST","STATE":True,"ResultType":Re.get('ResultType'),"ResultMessage":Re.get('ResultMessage')}
                self.Redis_Client.Post_List("MES_auto_label_print",json.dumps(results))
                print(f"报文发送成功;LPN:{lpn};QTY:{qty};MES接口返回:{Re.get('ResultType')};MES消息:{Re.get('ResultMessage')}")
            else:
                results={"MesResult":"False","CreateTime":str(datetime.now().replace(microsecond=0)),"ForData":data,"URL":self.url,"Method":"POST","STATE":True,"ResultType":Re.get('ResultType'),"ResultMessage":Re.get('ResultMessage')}
                self.Redis_Client.Post_List("MES_auto_label_print",json.dumps(results))
                print(f"报文发送失败;LPN:{lpn};QTY:{qty};MES接口返回:{Re.get('ResultType')};MES消息:{Re.get('ResultMessage')}")
        return Re
    


# if __name__=="__main__":
#     PO=Post_LPN_MES()
#     print(PO.POST('P225090300003',2))
    




# if __name__=="__main__":
#     work_orders='WORK297400-003'
#     MES=Get_Work_Orders()
#     print(MES.Get_Data(work_orders))