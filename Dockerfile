# Используем базовый образ Python
FROM python:3.9-alpine

# Установка переменной среды PYTHONUNBUFFERED для вывода в реальном времени
ENV PYTHONUNBUFFERED=1

# Устанавливаем зависимости, необходимые для установки psycopg2 (драйвер PostgreSQL)
RUN apk update \
    && apk add --no-cache postgresql-dev gcc python3-dev musl-dev

# Устанавливаем рабочую директорию в /app
WORKDIR /education

# Копируем файл зависимостей в рабочую директорию
COPY requirements.txt /education/

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
RUN pip install celery
RUN npm install -g pnpm

# Копируем все содержимое текущей директории в /app в контейнере
COPY . /education/

# Настройка записи и доступа (если нужно)
# RUN chmod -R 777 ./

# CMD указывает команду, которая будет выполнена при запуске контейнера
# В данном случае предполагается, что у вас будет entrypoint.sh или manage.py для запуска Django приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


RUN mkdir -p /education/docker/logs && touch /education/docker/logs/celery-worker.log
RUN chmod -R 777 /education/docker/logs

