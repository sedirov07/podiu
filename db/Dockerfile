# Используем официальный образ PostgreSQL
FROM postgres:13

# Устанавливаем переменные окружения для базы данных
ENV POSTGRES_DB=podiu
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

# Копируем файл инициализации в директорию Docker образа
COPY init.sql /docker-entrypoint-initdb.d/

# Слеш после директории обязателен
VOLUME ["/var/lib/postgresql/data"]

# Открываем порт для доступа к PostgreSQL
EXPOSE 5432
