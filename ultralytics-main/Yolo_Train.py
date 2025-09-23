from ultralytics import YOLO


###YOLOV11训练

###模型训练

# Load a model
model = YOLO('yolo11n.yaml')  # build a new model from YAML
# model = YOLO('D:/YOLO8/homecheck.pt')  # load a pretrained model (recommended for training)

#model = YOLO('yolov8n.yaml').load('A2062500-2600V6.2.pt')  # build from YAML and transfer weights

# Train the model
if __name__ == '__main__':
    model.train(data=r'D:\LaijinYOLO11\ultralytics-main\data\date.yaml',
                epochs=200,
                imgsz=640,
                device=[0],
                batch=12,
                workers=24,
                amp=False,
                verbose=True,
                # degrees=100, ##训练时 指定随机旋转图像
                # crop_fraction=0.5##训练时 随机擦除其中一部分，鼓励模型对不那么明显的特征进行识别
                )
    # model.train(data='D:/YOLO8/ultralytics-main/data/NEU-DET/data.yaml', epochs=10, imgsz=640, device='0')  # device指定0号GPU执行