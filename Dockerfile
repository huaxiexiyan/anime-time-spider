# 将 pipenv 构建为单独的步骤
FROM python:3.11.3 AS build
WORKDIR /myapp
#COPY Pipfile Pipfile.lock ./
COPY Pipfile ./
RUN pip install --no-cache-dir pipenv && \
    mkdir .venv && \
    pipenv install --deploy --ignore-pipfile
RUN pwd
RUN ls -a
RUN pipenv --version

# 将 pipenv 复制到最终镜像
# FROM gcr.io/distroless/python3-debian11
FROM python:3.11.3
COPY --from=build /myapp /myapp
RUN ls -a
WORKDIR /myapp
COPY . ./
# 暴露Flask应用程序的端口（通常是5000）
# 确保不生成 .pyc 文件,不会在 stdout 和 stderr 缓冲 I/O
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN pwd
RUN ls -a
EXPOSE 26001
#ENTRYPOINT ["/venv/bin/python3", "psutil_example.py"]
# 启动
CMD ["./.venv/bin/gunicorn", "-c", "gunicorn.conf.py", "run:myapp", "--preload"]



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




