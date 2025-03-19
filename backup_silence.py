import shutil
import os

def backup_silence():
    source_file = "/usr/data/prometheus/alertmanager_data/silences"    
    destination_dir = "/home/support_engineer/"  

    # Проверка исходного файла
    if not os.path.isfile(source_file):
        print(f"Ошибка: Исходный файл '{source_file}' не найден!")
        return

    # Создаем целевую директорию если не существует
    os.makedirs(destination_dir, exist_ok=True)

    # Формируем полный целевой путь
    file_name = os.path.basename(source_file)
    dest_path = os.path.join(destination_dir, file_name)
    
    try:
        shutil.copy2(source_file, dest_path)
        print(f"Файл успешно скопирован: {source_file} -> {dest_path}")

    except PermissionError as pe:
        print(f"Ошибка прав доступа: {str(pe)}")
    except Exception as e:
        print(f"Ошибка при копировании: {str(e)}")

if __name__ == "__main__":
    backup_silence()