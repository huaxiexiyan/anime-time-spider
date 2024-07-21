# 将 pipenv 构建为单独的步骤
FROM python:3.11.3 AS build
WORKDIR /app
COPY Pipfile Pipfile.lock ./
# PYTHONDONTWRITEBYTECODE=1 确保在运行 Python 应用时不会生成 .pyc 文件，保持文件系统清洁。
ENV PYTHONDONTWRITEBYTECODE=1
RUN pip install --no-cache-dir pipenv && \
    mkdir .venv && \
    pipenv install --deploy --ignore-pipfile

# 将 pipenv 复制到最终镜像
#FROM gcr.io/distroless/python3-debian11
FROM python:3.11.3-slim
COPY --from=build /app /app
WORKDIR /app
COPY . ./
# PYTHONUNBUFFERED=1 确保 Python 的输出能够立即显示在日志中，便于实时监控和调试
#ENV PYTHONUNBUFFERED=1
# 暴露Flask应用程序的端口（通常是5000）
EXPOSE 26001
# 启动
CMD ["/app/.venv/bin/gunicorn", "-c", "gunicorn.conf.py", "run:app", "--preload"]
