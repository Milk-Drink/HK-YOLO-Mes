import uvicorn
from fastapi import FastAPI,Response,Body
from fastapi.responses import StreamingResponse
from Redis import MyRedis
import json
from fastapi.middleware.cors import CORSMiddleware
from Celery import Celery_Read_Redis
from MESApi import Get_Work_Orders
from LPN_Quere import package_worker



app=FastAPI()
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的来源
    allow_credentials=True,  # 允许携带 Cookie（如需）
    allow_methods=["*"],    # 允许的 HTTP 方法（GET, POST, PUT, DELETE 等）
    allow_headers=["*"],    # 允许的请求头（如 Authorization）
)
@app.get('/')
def homepage():
    html="""
<html>
    <head>
        <title>Laijin YoloV11</title>
        <style>
            .image-container {
                display: flex;
                justify-content: space-between;
                gap: 10px; /* 可选：增加间距 */
            }
            .image-box {
                display: flex;
                flex-direction: column; /* 垂直排列（label 在上，img 在下） */
                width: 49%;
            }
            .image-box label {
                margin-bottom: 40px; /* 可选：增加 label 和图片的间距 */
                font-weight: bold; /* 可选：加粗 label */
                text-align: center; /* 可选：居中 label */
            }
            .image-box img {
                width: 100%; /* 图片宽度填满容器 */
                height: auto; /* 保持宽高比 */
            }
        </style>
    </head>
    <body>
        <h1>RTSP Video Streaming</h1>
        <div class="image-container">
            <div class="image-box">
                <label>原始图像</label>
                <img src="/video_feed">
            </div>
            <div class="image-box">
                <label>推理后的图像</label>
                <img src="/video_feeds">
            </div>
        </div>
    </body>
    <tabel>
    <thead>
    <tr>
    <th>物料编号</th>
    <th>进入数量</th>
    <th>走出数量</th>
    </tr>
    </thead>
<tbody>
</tbody>

    </tabel>
</html>
    """
    
    return Response(content=html,media_type="text/html")
@app.get('/video_feed')
async def video_feed():
    
    view=r"D:\LaijinYOLO11\2024-11-2-25002600现场视频2.mp4"
    cap=MyRedis()
    return StreamingResponse(cap.R_Get('sxxxImg'),media_type="multipart/x-mixed-replace;boundary=frame")
@app.get("/video_feeds")
async def video_feeds():
    view=r"D:\LaiJin-YOLO8\TestViews\2024-11-2-25002600现场视频2.mp4"
    cap=MyRedis()
    return StreamingResponse(cap.R_Get('YOLO_IMG'),media_type="multipart/x-mixed-replace;boundary=frame")
@app.get("/GetData")
async def getdate():
    OBJ=Celery_Read_Redis()
    return StreamingResponse(OBJ.Streaming_Redis_Results(),media_type="text/event-stream")
@app.get('/Mes_Lot_Pre_Products')
async def Mes_Lot_Pre_Products(workorder:str):
    MES=Get_Work_Orders()
    data=MES.Get_Data(workorder)
    return Response(json.dumps(data))
@app.post('/Mes_Lot_Clock')
async def Mes_Lot_Clock(data:list=Body(...)):
    # print(data)
    ##整理任务列表,返回需要创建的LPN明细
    MainOBJ=package_worker()##创建队列
    if len(data)>0:
        CreateList=[ results for results in data if results['status']=='CREATE']
        print(f"原数据总计:{len(data)},待创建的数据:{len(CreateList)}")
        
        results=MainOBJ.Update_package(CreateList)##把预制标签存入队列
        if results !=False:
            return StreamingResponse(MainOBJ.StartWork(results),media_type="text/event-stream")
        else:
            return StreamingResponse(MainOBJ.NUllStart(CreateList),media_type="text/event-stream")
    
    return StreamingResponse(MainOBJ.NUllStart(''),media_type="text/event-stream")
@app.get('/Clear_Data')
async def Clear_Data():
    cap=Celery_Read_Redis()
    results=cap.Get_Redis_Results()
    if results:
        for item in json.loads(results):
            cap.Redis_connet.Delete(item["Name"])###把已经用于包装的Package删除
            cap.Redis_connet.Delete(f"Quantity{item["Name"]}")
    cap.Redis_connet.Delete("Yolo_Results")
    return Response(json.dumps({"msg":results}))
@app.get('/Stop_MES_LPN_Quere')
async def Stop_MES_LPN_Quere():
    ###立刻停止队列接口
    OBJ=Celery_Read_Redis()
    QuereStatus=OBJ.Redis_connet.get('MesQuereStatus')
    if QuereStatus is not None :
        if QuereStatus.decode('utf-8') =='Runing':
            try:
                OBJ.Redis_connet.put_text('MesQuereStatus','Stop')
                return Response(json.dumps({"Message":"已停止"}),status_code=200)
            except Exception as error:
                return Response(json.dumps({"Error":str(error)}),status_code=300)
        return Response(json.dumps({"Msg":f"非Runing状态时,不允许中断生产;{QuereStatus.decode('utf-8') if QuereStatus is not None else 'None'}"}),status_code=400)
    else:
        return Response(json.dumps({"Msg":f"非Runing状态时,不允许中断生产;{QuereStatus.decode('utf-8') if QuereStatus is not None else 'None'}"}),status_code=400)
@app.post('/Bad_Data_Get')
async def Bad_Date_Get(Name:str=Body(...,embed=True),Quantity:int=Body(...,embed=True)):
    if Name:
        print(f"要处理的零件是:{Name};不合格数量是:{Quantity}")
        OBJ=Celery_Read_Redis()
        result=OBJ.Redis_connet.get(f'Quantity{Name}')
        if result is not None:###如果已经存在不合格数量,则增加
            result=int(result)
            OBJ.Redis_connet.put_text(f'Quantity{Name}',result+int(Quantity))
        else:
            OBJ.Redis_connet.put_text(f'Quantity{Name}',int(Quantity))
        return Response(json.dumps({"Message":f"报废零件:{Name};不合格数量是:{Quantity}"}),status_code=200)
    return Response(json.dumps({"Message":f"未收到有效零件数据{Name}"}),status_code=200)




if __name__=="__main__":
    uvicorn.run(app=app,port=8000,host="0.0.0.0")