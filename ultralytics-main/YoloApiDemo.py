import cv2
from fastapi import FastAPI,Response
from fastapi.responses import StreamingResponse
from ultralytics import solutions
import uvicorn

#cap = cv2.VideoCapture("D:/LaiJin-YOLO8/ultralytics-main/views/2500-2600正面+反面+旋转.mp4")
app=FastAPI()
Camera_rtsp_url_6="rtsp://admin:1234567a@192.168.1.64:554/Streaming/Channels/101"
view_path= r"D:\LaiJin-YOLO8\TestViews\2024-11-2-25002600现场视频2.mp4"
cap = cv2.VideoCapture(view_path)
assert cap.isOpened(), "Error reading video file"
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

# Define region points
region_points = [(0, 400),(1480, 400), (0, 500),(1480, 500) ]

# line or region points
line_points = [(0, 500), (1850, 500)]


# Define region points
region_points_x = [(20, 400), (1080, 404), (1080, 460), (20, 460),]
# Video writer
video_writer = cv2.VideoWriter("object_counting_output.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

# Init Object Counter
counter = solutions.ObjectCounter(
    show=True,
    region=line_points,
    model=r"D:\LaijinYOLO11\ultralytics-main\best.pt",
    # show_in=False
    conf=0.7
)

# Process video
def imgget():
    while cap.isOpened():
        success, im0 = cap.read()
        if not success:
            print("Video frame is empty or video processing has been successfully completed.")
            break
        im0 = counter.count(im0)
        video_writer.write(im0)
        ret, buffer = cv2.imencode(".jpg", im0)
        yield (b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")

    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()
@app.get("/video_feed")
async def video_feed():
    """将视频流作为流响应返回。"""
    return StreamingResponse(imgget(), media_type="multipart/x-mixed-replace;boundary=frame")

# if __name__=="__main__":
#     View=Camera(0)
    
#     while True:
#         img=View.img_get()
#         if img is not None:
#             cv2.imshow('Camera',img)
#             cv2.waitKey(1)

#         else:
#             break
@app.get("/")
async def root():
    """呈现网站页面。"""
    html = """
    <html>
        <head>
            <title>Laijin YoloV11</title>
        </head>
        <body>
            <h1>RTSP Video Streaming</h1>
            <img src="/video_feed">
        </body>
    </html>
    """
    return Response(content=html, media_type="text/html")
if __name__=="__main__":
    uvicorn.run(app=app,host='0.0.0.0',port=8000)
