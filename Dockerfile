FROM python:3.9

# 设置工作目录为 /app
WORKDIR /app

# 将当前目录下的文件复制到容器的 /app 目录
COPY . /app

# 安装 requirements.txt 中列出的依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir uvicorn[standard] fastapi -i https://pypi.tuna.tsinghua.edu.cn/simple

# 让容器监听80端口
EXPOSE 80

# 定义环境变量
ENV NAME World

# 运行应用
#CMD ["uvicorn", "textgen:app", "--host", "0.0.0.0", "--port", "80"]