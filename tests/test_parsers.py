import io
import json
import pytest

from streamstats.parsers import create_reader, parse_event


# Проверяем чтение CSV.
def test_create_reader_csv():
    file = io.StringIO(
        "timestamp,level,source,message\n2026-10-18T12:00:00,INFO,app,Test\n"
    )

    reader = create_reader(file, "csv")
    events = list(reader)

    assert len(events) == 1
    assert events[0]["level"] == "INFO"
    assert events[0]["source"] == "app"


# Тест JSONL.
def test_create_reader_jsonl():
    file = io.StringIO(
        '{"timestamp": "2026-10-18T12:00:00", '
        '"level": "INFO", '
        '"source": "app", '
        '"message": "Test"}\n'
    )

    reader = create_reader(file, "jsonl")
    events = [json.loads(line) for line in reader]

    assert len(events) == 1
    assert events[0]["level"] == "INFO"
    assert events[0]["source"] == "app"


# Тест parse_event.
def test_parse_event_jsonl():
    row = '{"timestamp": "2026-10-18T12:00:00", "level": "INFO", "source": "app", "message": "Test"}'

    event = parse_event(row, "jsonl")

    assert isinstance(event, dict)
    assert event["level"] == "INFO"
    assert event["source"] == "app"


# Некорректный JSON.
def test_parse_event_invalid_jsonl():
    row = '{"level": "INFO", "source": "app"'

    with pytest.raises(json.JSONDecodeError):
        parse_event(row, "jsonl")
