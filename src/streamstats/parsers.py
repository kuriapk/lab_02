import csv
import json


def create_reader(file, input_format):
    # Для csv получаем записи в виде словарей.
    # Ключи словаря берутся из первой строки файла - заголовка.
    if input_format == "csv":
        return csv.DictReader(file, strict=True)
    return file


def parse_event(row, input_format):
    if input_format == "jsonl":
        return json.loads(row)
    return row
