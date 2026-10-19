import argparse  # Для чтения параметров, введенных в терминале.
from .parsers import create_reader, parse_event
import csv

import logging  # Для сообщений о работе программы.
import sys  # Для взаимодействия с интерпретатором и окружением запуска.

from .errors import StreamStatsError

import json  # Для чтения событий и сохранения отчёта.
from .models import validate_event  # Проверка события и получение даты.
from .report import save_report

from .analysis import get_top_sources

# Общее кол-во событий.
count = 0

# Словарь: уровень события, его количество.
level_counts = {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}

# Источники заранее неизвестны,
# поэтому будем добавлять их в словари во время чтения файла.
source_counts = {}  # Кол-во событий каждого источника.
error_counts = {}  # Кол-во ошибок каждого источника.

# Введём границы времени.
first_timestamp = None
last_timestamp = None


# Создаём обработчик аргументов командной строки.
parser = argparse.ArgumentParser()

# Первым словом после имени программы должна быть команда analyze.
parser.add_argument("command", choices=["analyze"])

# Принимаем имена файлов.
# nargs="+" означает, что нужен хотя бы один файл, можно указать несколько.
parser.add_argument("files", nargs="+")

# Пользователь обязательно должен указать формат: csv или jsonl.
parser.add_argument("--format", choices=["csv", "jsonl"], required=True)

# Если путь отчёта не указан, используем report.json.
parser.add_argument("--output", default="report.json")

# Если пользователь написал --skip-invalid, получим True.
# Если не написал — False.
parser.add_argument("--skip-invalid", action="store_true")

# Читаем введённые параметры.
args = parser.parse_args()

# Записываем значения в переменные, которые используются дальше.
input_paths = args.files
input_format = args.format
output_path = args.output
skip_invalid = args.skip_invalid

# Кол-во пропущенных записей и номер текущей строки.
skipped_count = 0
line_number = 0


# По очереди обрабатываем каждый файл.
for input_path in input_paths:
    line_number = 0

    with open(input_path, "r", encoding="utf-8", newline="") as file:
        reader = create_reader(file, input_format)

        while True:
            try:
                # Получаем следующую запись.
                row = next(reader)

            except StopIteration:
                # Файл закончился — выходим из цикла.
                break

            except csv.Error:
                # CSV-парсер обнаружил повреждённую запись.
                line_number = reader.reader.line_num
                error_text = (
                    input_path + ", строка " + str(line_number) + ": неправильный CSV"
                )

                if skip_invalid:
                    skipped_count += 1
                    logging.warning(error_text)
                    continue

                print(error_text, file=sys.stderr)
                sys.exit(2)
            # Для csv используем номер физической строки файла.
            # DictReader учитывает заголовок и переносы внутри полей.
            if input_format == "csv":
                line_number = reader.line_num
            else:
                line_number += 1

            try:
                event = parse_event(row, input_format)

            except json.JSONDecodeError:
                error_text = (
                    input_path + ", строка " + str(line_number) + ": неправильный JSON"
                )

                if skip_invalid:
                    skipped_count += 1
                    logging.warning(error_text)
                    continue

                print(error_text, file=sys.stderr)
                sys.exit(2)

            # Если json разобран, проверяем поля до получения значений и подсчёта статистики.
            try:
                timestamp = validate_event(event)
            except StreamStatsError as error:
                error_text = (
                    input_path + ", строка " + str(line_number) + ": " + str(error)
                )

                if skip_invalid:
                    skipped_count += 1
                    logging.warning(error_text)
                    continue

                print(error_text, file=sys.stderr)
                sys.exit(2)

            # Уровень и источник текущего события.
            level = event["level"]
            source = event["source"]

            count += 1

            # Счётчик событий ДАННОГО уровня увеличиваем на 1.
            level_counts[level] += 1

            # Для нового источника создаём счётчик.
            if source not in source_counts:
                source_counts[source] = 0

            source_counts[source] += 1

            # Отдельно считаем ошибки.
            if level in ["ERROR", "CRITICAL"]:
                # Для новой ошибки(если у источника её не было) создаём счётчик.
                if source not in error_counts:
                    error_counts[source] = 0

                error_counts[source] += 1

            #
            # НАХОДИМ САМОЕ РАННЕЕ И ПОЗДНЕЕ СОБЫТИЕ.
            if first_timestamp is None or timestamp < first_timestamp:
                first_timestamp = timestamp

            if last_timestamp is None or timestamp > last_timestamp:
                last_timestamp = timestamp


# НАХОДИМ ТОП 5 ИСТОЧНИКОВ ПО КОЛ-ВУ ERROR И CRITICAL.
top_sources = get_top_sources(error_counts)


# Вернём даты в строки, чтобы работать с json.
first_time = None
last_time = None

# .isoformat() превращает объект даты обратно в строку
if first_timestamp is not None:
    first_time = first_timestamp.isoformat()

if last_timestamp is not None:
    last_time = last_timestamp.isoformat()

# Статистика.
status = {
    "count": count,
    "levels": level_counts,
    "sources": source_counts,
    "top_error_sources": top_sources,
    "first_timestamp": first_time,
    "last_timestamp": last_time,
    "skipped_count": skipped_count,
}


# Данные python-> json в файле.
# ensure_ascii=False сохраняет русские буквы в читаемом виде.
# indend=4 добавляет отступы.
save_report(status, output_path)
print("Отчёт сохранён в", output_path)
