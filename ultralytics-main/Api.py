import uvicorn
from fastapi import FastAPI,Response
from fastapi.responses import StreamingResponse
from CameraRead import Camera


app=FastAPI()

@app.get('/')
def homepage():
    html="""
    <html>
        <head>
            <title>Laijin YoloV11</title>
        </head>
        <body>
            <h1>RTSP Video Streaming</h1>
            <div    style='display: flex;justify-content: space-between;'>
            <img src="/video_feed" style='width:49%'>
            <img src="/video_feeds" style='width:49%'>

            </div>
        </body>
    </html>
    """
    
    return Response(content=html,media_type="text/html")
@app.get('/video_feed')
async def video_feed():
    
    view=r"D:\LaijinYOLO11\2024-11-2-25002600现场视频2.mp4"
    cap=Camera(view)
    return StreamingResponse(cap.yolo_img(),media_type="multipart/x-mixed-replace;boundary=frame")
@app.get("/video_feeds")
async def video_feeds():
    view=r"D:\LaiJin-YOLO8\TestViews\2024-11-2-25002600现场视频2.mp4"
    cap=Camera(view)
    return StreamingResponse(cap.img_code(),media_type="multipart/x-mixed-replace;boundary=frame")
if __name__=="__main__":
    uvicorn.run(app=app,port=8000,host="0.0.0.0")