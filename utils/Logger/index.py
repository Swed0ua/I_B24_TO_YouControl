import logging
import os
from logging.handlers import TimedRotatingFileHandler

class Logger:
    def __init__(self, name: str, log_file: str = "logs/app.log", level: str = "INFO", backup_days: int = 10):
        """
        Ініціалізує логер.

        :param name: Ім'я логера.
        :param log_file: Шлях до файлу логів.
        :param level: Рівень логування.
        :param backup_days: Кількість днів для збереження логів.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self._get_log_level(level))
        self._configure_handlers(log_file, backup_days)

    def _get_log_level(self, level: str) -> int:
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return levels.get(level.upper(), logging.INFO)

    def _configure_handlers(self, log_file: str, backup_days: int):
        # Формат логів
        log_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Створення директорії для логів
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # TimedRotatingFileHandler для ротації за часом
        file_handler = TimedRotatingFileHandler(
            log_file, when="D", interval=1, backupCount=backup_days, encoding='utf-8'
        )
        file_handler.setFormatter(log_format)

        # Консольний обробник
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)

        # Додаємо обробники до логера
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        return self.logger
    
    @staticmethod
    def create_default_logger(name:str, path:str) -> logging.Logger:
        """Creates a default logger."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler(path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger