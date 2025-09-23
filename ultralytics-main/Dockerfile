# 使用Python 3作为基础镜像
FROM python:3.12.4

# 设置工作目录
WORKDIR /ultralytics-main

# 复制项目文件到容器中
COPY . /ultralytics-main

# 安装项目依赖项
RUN pip install --no-cache-dir -r requirements.txt 

# 设置环境变量
ENV FLASK_APP=app.py

EXPOSE 8000 

# 定义容器启动命令
CMD [ "python","./Api.py"]