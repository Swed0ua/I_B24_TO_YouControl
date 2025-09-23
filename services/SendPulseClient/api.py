import logging
from pysendpulse.pysendpulse import PySendPulse
from utils.Logger.index import Logger

class SendPulseManager:
    def __init__(self, api_id, api_secret, token_storage, logger: logging.Logger = None):
        """Ініціалізуємо SendPulse API."""
        self.api = PySendPulse(api_id, api_secret, token_storage)
        self.logger = logger if logger else self._create_default_logger()

    @staticmethod
    def _create_default_logger() -> logging.Logger:
        """Creates a default logger."""
        return Logger.create_default_logger("SendPulse", "logs/sendpulse.log")

    def add_contacts(self, addressbook_id, contacts):
        """Додає список контактів до вказаної адресної книги."""
        if not contacts:
            self.logger.warning("SendPulse Список контактів порожній. Нічого не додано.")
            return

        response = self.api.add_emails_to_addressbook(addressbook_id, contacts)
        
        if response:
            self.logger.info(f"SendPulse Контакти успішно додані в книгу {addressbook_id}.")
        else:
            self.logger.error(f"SendPulse Помилка додавання контактів у {addressbook_id}.")
        
        return response

    