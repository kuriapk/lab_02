# ОБЩАЯ ошибка анализатора.
class StreamStatsError(ValueError):
    pass


# Ошибка структуры СОБЫТИЯ или значения его полей.
class InvalidEventError(StreamStatsError):
    pass


# Ошибка формата или значения ДАТЫ.
class InvalidTimestampError(StreamStatsError):
    pass


# Передан формат, который программа не поддерживает.
class UnsupportedFormatError(StreamStatsError):
    pass


# Неправильно заданы параметры запуска программы.
class CLIConfigError(StreamStatsError):
    pass
