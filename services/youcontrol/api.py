import logging
import requests


class YouControlAPI:
    """
    A class to integration with YouControl API

    Supports methods for obtaining data about new counterparties.
    """

    def __init__(self, api_key: str, logger:logging.Logger=None):
        """
        Initializes the API client object.
        
        :param api_key: API-key for auth (Bearer).
        :param logger: Logger instance for logging API calls.
        """
        self.base_url = "https://integration.youcontrol.market/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }

        self.logger = logger if logger else self._create_default_logger()

    @staticmethod
    def _create_default_logger() -> logging.Logger:
        """Creates a default logger."""
        logger = logging.getLogger("I_B24")
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler("youcontrol.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger

    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """
        Виконує HTTP GET-запит до API.

        :param endpoint: Кінцева точка (endpoint) API.
        :param params: Параметри запиту.
        :return: Дані у форматі JSON.
        :raises Exception: У випадку помилки HTTP-запиту.
        """
        url = f"{self.base_url}/{endpoint}"
        self.logger.debug(f"Making request to {url} with params: {params}")
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            err_txt = f"Error requesting the YouControl API: {e}"
            self.logger.debug(err_txt)
            raise Exception(err_txt)
    
    def get_new_legalPersons(self, depth: int = 0, only_new: bool = False) -> dict:
        """
        Отримує дані про новостворені компанії.

        :param depth: Рівень деталізації (0 - базовий, більше 0 - розширений).
        :param only_new: Чи отримувати лише нових контрагентів.
        :return: Словник із даними про контрагентів.
        """
        params = {
            "depth": depth,
            "onlyNew": str(only_new).lower(),  # API is waiting boolean value
        }
        return self._make_request("newContractors/legalPersons", params)
    
    def get_new_naturalPersons(self, depth: int = 0, only_new: bool = False) -> dict:
        """
        Отримує дані про нових ФОПів.

        :param depth: Рівень деталізації (0 - базовий, більше 0 - розширений).
        :param only_new: Чи отримувати лише нових контрагентів.
        :return: Словник із даними про контрагентів.
        """
        params = {
            "depth": depth,
            "onlyNew": str(only_new).lower(),  # API is waiting boolean value
        }
        return self._make_request("newContractors/naturalPersons", params)

    def get_new_contractors(self, depth: int = 0, only_new: bool = False) -> dict:
        """
        Отримує дані про нових контрагентів 
        з методів get_new_legalPersons і get_new_naturalPersons
        і обєднує їх.

        :param depth: Рівень деталізації (0 - базовий, більше 0 - розширений).
        :param only_new: Чи отримувати лише нових контрагентів.
        :return: Словник із даними про контрагентів.
        """
        legalPersons_list = self.get_new_legalPersons(depth, only_new)
        naturalPersons_list = self.get_new_naturalPersons(depth, only_new)
        return legalPersons_list , naturalPersons_list