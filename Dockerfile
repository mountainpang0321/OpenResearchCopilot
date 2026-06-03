# 使用 Python 3.11 的轻量级官方镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖清单并安装
COPY requirements.txt .
# 使用国内镜像源加速安装，并且不缓存下载包以减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制整个项目到工作目录 (受 .dockerignore 或 .gitignore 影响)
COPY . .

# 暴露 Streamlit 的默认端口
EXPOSE 8501

# 设置容器启动时执行的命令
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]