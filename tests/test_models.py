import pytest
from streamstats.errors import InvalidEventError

from datetime import datetime, timezone

from streamstats.models import validate_event


def test_valid_event():
    # Подготавливаем событие со всеми обязательными полями.
    event = {
        "timestamp": "2026-10-14T12:00:00+00:00",
        "level": "INFO",
        "source": "app",
        "message": "Программа запущена",
    }

    # Проверяем событие и получаем дату, которую вернула функция.
    result = validate_event(event)

    # Создаём ожидаемую дату: 14 октября 2026 года, 12:00 по UTC.
    expected = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)

    # Тест пройдёт, если полученная дата совпадает с ожидаемой.
    assert result == expected


def test_unknown_level():
    # Все поля заполнены, но уровень UNKNOWN не разрешён.
    event = {
        "timestamp": "2026-10-14T12:00:00+00:00",
        "level": "UNKNOWN",
        "source": "app",
        "message": "Проверка неправильного уровня",
    }

    # Ожидаем, что проверка события вызовет InvalidEventError.
    # Если ошибка не возникнет, pytest отметит тест как проваленный.
    with pytest.raises(InvalidEventError):
        validate_event(event)


def test_missing_source():
    event = {
        "timestamp": "2026-10-14T12:00:00+00:00",
        "level": "INFO",
        "message": "Проверка неправильного уровня",
    }

    with pytest.raises(InvalidEventError):
        validate_event(event)
