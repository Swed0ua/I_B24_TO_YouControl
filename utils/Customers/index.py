import hashlib
import logging
from typing import List, Dict

class Customer:
    """Клас, що представляє клієнта з email та номером телефону."""
    
    def __init__(self, email: str, phone: str):
        self.email = self._validate_email(email)
        self.phone = self._validate_phone(phone)

    @staticmethod
    def _validate_email(email: str) -> str:
        """Валідує та повертає email у нижньому регістрі."""
        if "@" not in email:
            raise ValueError(f"Некоректний email: {email}")
        return email.strip().lower()

    @staticmethod
    def _validate_phone(phone: str) -> str:
        """Очищує телефонний номер від зайвих символів."""
        return "".join(filter(str.isdigit, phone))  # Видаляємо все, крім цифр

    @staticmethod
    def hash_value(value: str) -> str:
        """Хешує значення у SHA256."""
        return hashlib.sha256(value.strip().lower().encode()).hexdigest()

    def to_hashed_data(self) -> List[str]:
        """Повертає хешовані email і телефон."""
        return [self.hash_value(self.email), self.hash_value(self.phone)]