# 安装依赖的基础镜像
FROM python:3.11.3-slim AS build-env
# 确保不生成 .pyc 文件,不会在 stdout 和 stderr 缓冲 I/O
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# 设置工作目录
WORKDIR /app
# 安装依赖
COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --deploy --ignore-pipfile
# 复制应用代码
COPY . .

# 最终镜像，复制依赖+代码
FROM gcr.io/distroless/python3 AS final
# 确保不生成 .pyc 文件,不会在 stdout 和 stderr 缓冲 I/O
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --from=build-env /app /app
WORKDIR /app
# 暴露Flask应用程序的端口（通常是5000）
EXPOSE 26001
# 启动
CMD ["pipenv", "run", "gunicorn", "-c", "gunicorn.conf.py", "run:app", "--preload"]

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




