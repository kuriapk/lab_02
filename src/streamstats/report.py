import json


def save_report(status, output_path):
    # status — словарь с уже подсчитанной статистикой.
    # output_path — путь к файлу, куда нужно сохранить отчёт.

    # Открываем файл для записи. Если его нет, он будет создан.
    # Если файл существует, его содержимое будет заменено.
    with open(output_path, "w", encoding="utf-8") as output:
        # Записываем словарь в формате JSON.
        # Русские буквы сохраняем читаемыми, отступы — четыре пробела.
        json.dump(status, output, ensure_ascii=False, indent=4)
