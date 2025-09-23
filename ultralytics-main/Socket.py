import asyncio  
import cv2  
import websockets  
from CameraRead import Camera


view=r"D:\LaijinYOLO11\2024-11-2-25002600现场视频2.mp4"
async def camera_stream(websocket):  
    # cap = cv2.VideoCapture(view) 
    cap=Camera(view)
  
    try:  
        while True:  
            # ret, frame = cap.read()  
            # if not ret:  
            #     break  
            ret,img=cap.socket_img()
            if ret:

            # buffer = cv2.imencode('.jpg', frame)[1]  
            # await websocket.send(buffer.tobytes())  
            # websocket.send(b'123')
                await websocket.send(img.tobytes())  
            
            # await asyncio.sleep(0.05)  
    finally:  
        cap.release()  


async def main():
    async with websockets.serve(camera_stream, "172.21.2.84", 8765):
        await asyncio.Future()  # run forever
# start_server = websockets.serve(camera_stream, "172.21.2.84", 8765)  
  
# asyncio.get_event_loop().run_until_complete(start_server)  
# asyncio.get_event_loop().run_forever()
if __name__=="__main__":
    asyncio.run(main())
    print("Waite For Connet Port 8765")
