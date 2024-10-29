# Используем образ Python
FROM python:3.11.5

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Команда, которая будет выполнена при запуске контейнера
CMD ["python", "main_outlook.py"]
