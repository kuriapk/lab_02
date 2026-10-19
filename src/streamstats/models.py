from datetime import datetime, timezone

from .errors import InvalidEventError, InvalidTimestampError


def validate_event(event):
    # После чтения json должен получиться словарь.
    if type(event) is not dict:
        raise InvalidEventError("Событие должно быть словарём")

    # DictReader добавляет ключ None, если в строке CSV
    # больше значений, чем названий полей в заголовке.
    if None in event:
        raise InvalidEventError("В строке CSV есть лишние значения")

    # Названия полей, которые должны быть в каждом событии.
    our_box = ["timestamp", "level", "source", "message"]

    # Проверка наличия каждого ключа в словаре.
    for box in our_box:
        if box not in event:
            raise InvalidEventError("Отсутствует поле: " + box)

    # Допустимые уровни.
    allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    if event["level"] not in allowed_levels:
        raise InvalidEventError("Неизвестный уровень события")

    # source должен быть строкой.
    if type(event["source"]) is not str:
        raise InvalidEventError("Источник должен быть строкой")

    # Источник не должен быть пустым или состоять только из пробелов.
    if event["source"].strip() == "":
        raise InvalidEventError("Источник пустой")

    # Сообщение должно быть строкой, пустое допускается.
    if type(event["message"]) is not str:
        raise InvalidEventError("Сообщение должно быть строкой")

    # Дата должна быть строкой.
    if type(event["timestamp"]) is not str:
        raise InvalidTimestampError("Временная метка должна быть строкой")

    # Пробуем преобразовать строку в дату и время.
    try:
        timestamp = datetime.fromisoformat(event["timestamp"])
    except ValueError:
        raise InvalidTimestampError("Неверная временная метка")

    #
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    return timestamp
