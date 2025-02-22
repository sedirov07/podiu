import os
import shutil


DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(DIR, '..', '..'))
DOCS_DIR = os.path.join(PROJECT_DIR, 'documents')


async def make_dir(data, name):
    destination = os.path.join(PROJECT_DIR, 'data_applyes', str(data["telegram_id"]))
    os.makedirs(destination, exist_ok=True)
    destination = os.path.join(destination, name)
    return destination


async def delete_dir(telegram_id):
    destination = os.path.join(PROJECT_DIR, 'data_applyes', str(telegram_id))
    if os.path.exists(destination):
        shutil.rmtree(destination)


async def delete_doc_file(file_path):
    # Проверяем, существует ли файл
    if os.path.exists(file_path):
        # Удаляем файл
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")
    else:
        print(f"Файл {file_path} не существует.")
