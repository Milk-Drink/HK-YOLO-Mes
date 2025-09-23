import cv2
import time
import multiprocessing as mp


def image_put(q, name, pwd, ip, channel=101):
    cap = cv2.VideoCapture("rtsp://%s:%s@%s//Streaming/Channels/%d" \
                           % (name, pwd, ip, channel))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print('fps: ', fps)
    if cap.isOpened():
        print('HIKVISION1')
    else:
        cap = cv2.VideoCapture("rtsp://%s:%s@%s//Streaming/Channels/%d" \
                               % (name, pwd, ip, channel))
        fps = cap.get(cv2.CAP_PROP_FPS)
        print('fps: ', fps)
        print('HIKVISION2')

    while cap.isOpened():
        # print('cap.read()[0]:', cap.read()[0])
        ret, frame = cap.read()
        # print('ret:', ret)
        frame = cv2.resize(frame, (1920, 1080))
        if not ret:
            cap = cv2.VideoCapture("rtsp://%s:%s@%s//Streaming/Channels/%d" \
                                   % (name, pwd, ip, channel))
            print('HIKVISION2')
            ret, frame = cap.read()
            frame = cv2.resize(frame, (1920,1080))
        q.put(frame)
        # print('q.qsize():', q.qsize())
        q.get() if q.qsize() > 1 else time.sleep(0.01)


def image_get(q, window_name):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    path = "D:/test/" + window_name + ".avi"
    out = cv2.VideoWriter(path, fourcc, 20.0, (1920, 1080), True)
    while True:
        frame = q.get()
        out.write(frame)
        cv2.imshow(window_name, frame)
        cv2.waitKey(1)


def run_multi_camera():
    # user_name, user_pwd = "admin", "password"
    user_name, user_pwd = "admin", "1234567a"
    camera_ip_l = [
        "172.19.0.80"  # ipv4（改成自己的）
        # "192.168.1.64",  # ipv4（改成自己的）
        # 把你的摄像头的地址放到这里，如果是ipv6，那么需要加一个中括号。
    ]

    mp.set_start_method(method='spawn')  # init
    queues = [mp.Queue(maxsize=2) for _ in camera_ip_l]

    processes = []
    for queue, camera_ip in zip(queues, camera_ip_l):
        processes.append(mp.Process(target=image_put, args=(queue, user_name, user_pwd, camera_ip)))
        processes.append(mp.Process(target=image_get, args=(queue, camera_ip)))

    for process in processes:
        process.daemon = True
        process.start()
    for process in processes:
        process.join()


if __name__ == '__main__':
    run_multi_camera()
