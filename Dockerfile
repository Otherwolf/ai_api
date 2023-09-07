FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install --no-install-recommends -y build-essential software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install --no-install-recommends -y python3.9 python3-pip python3-setuptools python3-distutils && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Копирование файлов проекта в контейнер
COPY . /app
WORKDIR /app

# Установка зависимостей Python
RUN python3.9 -m pip install --upgrade pip &&  \
    python3.9 -m pip install --no-cache-dir -r ./req.txt

# Запуск вашего приложения
CMD ["python3.9", "web_server.py"]
EXPOSE 8080
