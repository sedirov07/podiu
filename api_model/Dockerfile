# Используем образ Python
FROM python:3.11.5

# Обновляем pip до последней версии
RUN pip install --upgrade pip

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Открываем порт для доступа к API
EXPOSE 8082

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Команда, которая будет выполнена при запуске контейнера
CMD ["python", "main.py"]