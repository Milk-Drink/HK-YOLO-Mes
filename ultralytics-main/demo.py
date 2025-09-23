import cv2

from ultralytics import solutions

#cap = cv2.VideoCapture("D:/LaiJin-YOLO8/ultralytics-main/views/2500-2600正面+反面+旋转.mp4")
print(solutions.__file__)

Camera_rtsp_url_6="rtsp://admin:1234567a@192.168.1.64:554/Streaming/Channels/101"
Camera_rtsp_url7="rtsp://admin:1234567a@172.19.0.80:554/Streaming/Channels/101?transportmode=unicast"
view_path= r"D:\LaijinYOLO11\2025-09-17现场生产视频.mp4"
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
while cap.isOpened():
    success, im0 = cap.read()
    if not success:
        print("Video frame is empty or video processing has been successfully completed.")
        break
    im0 = counter.count(im0)
    video_writer.write(im0)
    print(f"推理结果:{counter.classwise_counts}")
cap.release()
video_writer.release()
cv2.destroyAllWindows()