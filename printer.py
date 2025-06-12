import os
import subprocess

# Печать PDF-файла через Adobe Acrobat Reader
def print_file(path):
    if not os.path.isfile(path):
        print("Файл не найден:", path)
        return

    # Путь к Adobe Acrobat Reader — измени при необходимости!
    acrobat_path = r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe"
    if not os.path.isfile(acrobat_path):
        acrobat_path = r"C:\Program Files\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe"
        if not os.path.isfile(acrobat_path):
            print("❌ Adobe Acrobat Reader не найден. Укажи верный путь в printer.py")
            return

    try:
        # Печатаем файл и закрываем программу после печати
        subprocess.run([acrobat_path, '/N', '/T', path], check=True)
        print("✅ Печать запущена:", path)
    except subprocess.CalledProcessError as e:
        print("❌ Ошибка при печати:", e)

# Заглушка для команды /printer
def get_printer_status():
    return ["Принтер готов"]
