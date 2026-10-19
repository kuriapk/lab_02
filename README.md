# Лабораторная работа № 2 — StreamStats

Автор: Кирилл Петров  
GitHub: https://github.com/kuriapk

Потоковый анализатор событий из файлов CSV и JSONL.
Файлы обрабатываются последовательно, без загрузки всего файла в память.

## Возможности

- Чтение одного или нескольких файлов выбранного формата.
- Проверка обязательных полей событий.
- Подсчёт общего количества событий.
- Подсчёт событий по уровням и источникам.
- Определение пяти источников с наибольшим количеством ERROR и CRITICAL.
- Поиск самого раннего и самого позднего события.
- Сохранение статистики в JSON.
- Пропуск неправильных записей с флагом --skip-invalid.

## Установка

Требуются Python 3.13 или новее и Poetry.

Из папки проекта выполните:

```powershell
poetry install
```

## Запуск

Справка:

```powershell
poetry run python -m streamstats --help
```

Обработка CSV:

```powershell
poetry run python -m streamstats analyze events.csv --format csv --output report.json
```

Обработка нескольких файлов:

```powershell
poetry run python -m streamstats analyze events.csv events2.csv --format csv --output report.json --skip-invalid
```

Обработка JSONL:

```powershell
poetry run python -m streamstats analyze events.jsonl --format jsonl --output report.json --skip-invalid
```

Если --output не указан, отчёт сохраняется в report.json.
Существующий файл отчёта перезаписывается.

Пути к файлам считаются относительно текущей папки терминала.

## Формат событий

Каждое событие содержит четыре обязательных поля:

- timestamp — дата и время в формате ISO 8601.
- level — DEBUG, INFO, WARNING, ERROR или CRITICAL.
- source — непустая строка с названием источника.
- message — строка сообщения; может быть пустой.

Если часовой пояс не указан, время считается заданным в UTC.

Пример CSV:

```csv
timestamp,level,source,message
2026-10-14T12:00:00+03:00,INFO,app,Программа запущена
```

Пример JSONL — одно событие на строку:

```json
{"timestamp":"2026-10-14T12:00:00+03:00","level":"INFO","source":"app","message":"Программа запущена"}
```

Файлы читаются и сохраняются в UTF-8.

## Отчёт

Поля JSON-отчёта:

- count — количество правильных событий.
- levels — количество событий каждого уровня.
- sources — количество событий каждого источника.
- top_error_sources — до пяти пар «источник, количество ошибок».
- first_timestamp — время самого раннего события.
- last_timestamp — время самого позднего события.
- skipped_count — количество пропущенных неправильных записей.

Для пустого входа количество событий равно нулю,
а границы времени имеют значение null.

## Обработка ошибок

По умолчанию неправильная запись останавливает обработку
с кодом завершения 2. Сообщение содержит имя файла и номер строки.

С --skip-invalid программа выводит предупреждение,
пропускает неправильную запись и продолжает обработку.

При повреждённых кавычках CSV несколько физических строк
могут быть прочитаны как одна неправильная запись.

В примерах events.jsonl и events2.csv есть неправильные события
для проверки режима --skip-invalid.

Известное ограничение: ошибки открытия или записи файлов
пока выводятся стандартным traceback Python.

## Структура проекта

- src/streamstats/__main__.py — параметры запуска и обработка событий.
- src/streamstats/models.py — проверка события и преобразование даты.
- src/streamstats/parsers.py — чтение CSV и JSONL.
- src/streamstats/analysis.py — получение топа источников ошибок.
- src/streamstats/report.py — сохранение отчёта.
- src/streamstats/errors.py — собственные типы ошибок.
- tests/ — автоматические тесты.

## Проверки

```powershell
poetry run python -m pytest -q
poetry run ruff check .
poetry run ruff format --check .
```