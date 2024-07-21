# 构建 python 环境
FROM debian:11-slim AS build
# 更新并安装构建Python所需的依赖
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes \
    gcc \
    make \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 下载并编译安装Python 3.11
RUN wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz && \
    tar -xf Python-3.11.0.tgz && \
    cd Python-3.11.0 && \
    ./configure --enable-optimizations && \
    make -j $(nproc) && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.11.0 Python-3.11.0.tgz

# 安装pipenv及其他依赖
RUN python3.11 -m ensurepip && \
    python3.11 -m pip install --upgrade pip setuptools wheel && \
    python3.11 -m pip install pipenv

# 将 pipenv 构建为单独的步骤：仅当 Pipfile 更改时才重新执行此步骤
FROM build AS build-venv
COPY Pipfile Pipfile.lock ./
WORKDIR /myapp
RUN pipenv install --deploy --ignore-pipfile

# 将 pipenv 复制到最终镜像
FROM gcr.io/distroless/python3-debian11
COPY --from=build-venv /myapp /myapp
COPY . /myapp/pipenv
WORKDIR /myapp
# 暴露Flask应用程序的端口（通常是5000）
# 确保不生成 .pyc 文件,不会在 stdout 和 stderr 缓冲 I/O
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
EXPOSE 26001
#ENTRYPOINT ["/venv/bin/python3", "psutil_example.py"]
# 启动
CMD ["pip", "run", "gunicorn", "-c", "gunicorn.conf.py", "run:myapp", "--preload"]



## 使用一个基础镜像，可以根据你的需求选择不同的Python版本
#FROM python:3.11.3
#
## 确保不生成 .pyc 文件
#ENV PYTHONDONTWRITEBYTECODE=1
## 确保 Python 不会在 stdout 和 stderr 缓冲 I/O
#ENV PYTHONUNBUFFERED=1
#
## 设置工作目录
#WORKDIR /app
#
## 安装依赖
#COPY Pipfile Pipfile.lock ./
#RUN pip install pipenv && pipenv install --deploy --ignore-pipfile
#
## 复制应用代码
#COPY . .
#
## 暴露Flask应用程序的端口（通常是5000）
#EXPOSE 26001
#
## 启动Flask应用程序
#CMD ["pipenv", "run", "gunicorn", "-c", "gunicorn.conf.py", "run:app", "--preload"]




