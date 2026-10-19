import subprocess
import sys
import json


# Интеграционное тестирование CLI.
def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "streamstats", "--help"], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()


# Полноценное интеграционное тестирование CLI.
def test_cli_csv_report(tmp_path):
    input_file = tmp_path / "events.csv"
    output_file = tmp_path / "report.json"

    input_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-18T12:00:00+03:00,INFO,app,Start\n"
        "2026-10-18T12:01:00+03:00,ERROR,api,Failure\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "streamstats",
            "analyze",
            str(input_file),
            "--format",
            "csv",
            "--output",
            str(output_file),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert output_file.exists()

    report = json.loads(output_file.read_text(encoding="utf-8"))

    assert report["count"] == 2


# Пропуск некорректных событий.
def test_cli_skip_invalid(tmp_path):
    input_file = tmp_path / "events.csv"
    output_file = tmp_path / "report.json"

    input_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-18T12:00:00+03:00,INFO,app,Start\n"
        "2026-10-18T12:01:00+03:00,UNKNOWN,api,Error\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "streamstats",
            "analyze",
            str(input_file),
            "--format",
            "csv",
            "--output",
            str(output_file),
            "--skip-invalid",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert output_file.exists()

    report = json.loads(output_file.read_text(encoding="utf-8"))

    assert report["count"] == 1
    assert report["skipped_count"] == 1


# Ошибка в skip_invalid.
def test_cli_invalid_without_skip(tmp_path):
    input_file = tmp_path / "events.csv"
    output_file = tmp_path / "report.json"

    input_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-18T12:00:00+03:00,INFO,app,Start\n"
        "2026-10-18T12:01:00+03:00,UNKNOWN,api,Error\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "streamstats",
            "analyze",
            str(input_file),
            "--format",
            "csv",
            "--output",
            str(output_file),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert str(input_file) in result.stderr
    assert "строка 3" in result.stderr
    assert "Traceback" not in result.stderr


# Проверка пустого файла.
def test_cli_empty_file(tmp_path):
    input_file = tmp_path / "empty.csv"
    output_file = tmp_path / "report.json"

    input_file.write_text("timestamp,level,source,message\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "streamstats",
            "analyze",
            str(input_file),
            "--format",
            "csv",
            "--output",
            str(output_file),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert output_file.exists()

    report = json.loads(output_file.read_text(encoding="utf-8"))

    assert report["count"] == 0


# обработка нескольких CSV-файлов.
def test_cli_multiple_files(tmp_path):
    file1 = tmp_path / "events1.csv"
    file2 = tmp_path / "events2.csv"
    output_file = tmp_path / "report.json"

    file1.write_text(
        "timestamp,level,source,message\n"
        "2026-10-18T12:00:00+03:00,INFO,app,Start\n"
        "2026-10-18T12:01:00+03:00,ERROR,api,Failure\n",
        encoding="utf-8",
    )

    file2.write_text(
        "timestamp,level,source,message\n"
        "2026-10-18T12:02:00+03:00,WARNING,app,Warning\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "streamstats",
            "analyze",
            str(file1),
            str(file2),
            "--format",
            "csv",
            "--output",
            str(output_file),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert output_file.exists()

    report = json.loads(output_file.read_text(encoding="utf-8"))

    assert report["count"] == 3
