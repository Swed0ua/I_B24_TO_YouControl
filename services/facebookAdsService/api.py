import requests
import hashlib
import logging
from typing import List, Dict

from utils.Customers.index import Customer
from utils.Logger.index import Logger

def hash_data(data_list):
    return [hashlib.sha256(data.strip().lower().encode()).hexdigest() for data in data_list]


class FacebookAudienceManager:
    """Клас для керування аудиторіями Facebook Ads."""

    API_URL = "https://graph.facebook.com/v19.0"

    def __init__(self, access_token: str, audience_id: str, ad_account_id:str = None, logger: logging.Logger = None):
        self.access_token = access_token
        self.audience_id = audience_id
        self.ad_account_id = ad_account_id
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        self.logger = logger if logger else self._create_default_logger()

    @staticmethod
    def _create_default_logger() -> logging.Logger:
        """Creates a default logger."""
        return Logger.create_default_logger("FacebookAds", "logs/facebookAds.log")

    def add_customers(self, customers: List[Customer]) -> Dict:
        """Додає список клієнтів в аудиторію."""
        if not customers:
            self.logger.warning("(FB Ads) Список клієнтів порожній, додавання скасовано.")
            return {}

        payload = {
            "payload": {
                "schema": ["EMAIL_SHA256", "PHONE_SHA256"],
                "data": customers,
                "is_raw": False
            }
        }

        url = f"{self.API_URL}/{self.audience_id}/users"
        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code == 200:
            self.logger.info(f"(FB Ads) Клієнти успішно додані в аудиторію {self.audience_id}")
        else:
            self.logger.error(f"(FB Ads) Помилка при додаванні клієнтів: {response.json()}")

        return response.json()
    
    def get_custom_audiences_list(self) -> List[Dict]:
        """Отримує список кастомних аудиторій."""
        url = f"{self.API_URL}/act_{self.ad_account_id}/customaudiences"
        params = {
            "access_token": self.access_token,
            "fields": "id,name"
        }

        response = requests.get(url, params=params)

        print(response)

        if response.status_code == 200:
            self.logger.info("Успішно отримано список кастомних аудиторій.")
            return response.json().get("data", [])
        else:
            self.logger.error(f"Помилка при отриманні списку кастомних аудиторій: {response.json()}")
            return []