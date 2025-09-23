import logging
import requests

class Bitrix24API:
    """
    A class to integrate with the Bitrix24 REST API.

    Provides methods to interact with Bitrix24, such as sending messages to Open Lines or handling CRM records.
    """

    def __init__(self, webhook_url: str, logger: logging.Logger = None):
        """
        Initializes the Bitrix24 API client.

        :param webhook_url: Full Bitrix24 webhook URL for API access.
        :param logger: Logger instance for logging API calls.
        """
        self.webhook_url = webhook_url.rstrip("/")  # Ensure no trailing slash
        self.logger = logger if logger else self._create_default_logger()

    @staticmethod
    def _create_default_logger() -> logging.Logger:
        """Creates a default logger."""
        logger = logging.getLogger("Bitrix24API")
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler("logs/bitrix24.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger

    def _make_request(self, method: str, params: dict = None) -> dict:
        """
        Sends a request to the Bitrix24 API.

        :param method: API method endpoint (e.g., "crm.lead.add").
        :param params: Dictionary of parameters for the API call.
        :return: JSON response from the API.
        :raises Exception: If the HTTP request fails or API returns an error.
        """
        url = f"{self.webhook_url}/{method}"
        self.logger.debug(f"Making request to {url} with params: {params}")

        try:
            response = requests.post(url, json=params)
            response.raise_for_status()
            result = response.json()

            if 'error' in result:
                err_msg = f"Bitrix24 API error: {result['error_description']}"
                self.logger.error(err_msg)
                raise Exception(err_msg)

            return result

        except requests.exceptions.RequestException as e:
            err_txt = f"HTTP request to Bitrix24 API failed: {e}"
            self.logger.critical(err_txt)
            raise Exception(err_txt)

    def add_lead(self, title: str, fields: dict) -> dict:
        """
        Adds a new lead to the Bitrix24 CRM.

        :param title: Title of the lead.
        :param fields: Dictionary of lead fields (e.g., NAME, PHONE, EMAIL).
        :return: API response with the new lead ID.
        """
        params = {
            "fields": {"TITLE": title, **fields},
            "params": {"REGISTER_SONET_EVENT": "Y"}
        }
        return self._make_request("crm.lead.add", params)
    
    def add_deal(self, title: str, fields: dict) -> dict:
        """
        Adds a new deal to the Bitrix24 CRM.

        :param title: Title of the lead.
        :param fields: Dictionary of lead fields (e.g., NAME, PHONE, EMAIL).
        :return: API response with the new lead ID.
        """
        params = {
            "fields": {"TITLE": title, **fields},
            "params": {"REGISTER_SONET_EVENT": "Y"}
        }
        return self._make_request("crm.deal.add", params)

    def add_new_contractors_deal_params(self, stage_id:str ,first_name:str, last_name:str, phone_number:str, title:str, type_activity:str, address:str, i_code:str) -> dict:
        """
        Adds a new deal with params to the Bitrix24 CRM.

        :param title: Title of the lead.
        :param type_activity: Contractors type of employment.
        :param first_name: Contact First name.
        :param last_name: Contact Last name.
        :param phone_number: Contact Phone.
        :param address: Registration address.
        
        :return: API response with the new lead ID.
        """
        contact_id = self.get_contact_id(first_name=first_name, 
                                         last_name=last_name,
                                         phone=phone_number
                                         )
        
        responce = self.add_deal(title=title, fields={
            'CATEGORY_ID': 22,
            'STAGE_ID':stage_id,
            'CONTACT_ID': contact_id,
            'UF_CRM_65E989F5B627E': type_activity,
            "UF_CRM_66ACC6BAA0203" : address,
            "UF_CRM_1682949203" : i_code,
            "UF_CRM_1683118575": title 
        })

        return responce
    
    def get_lead(self, lead_id: int) -> dict:
        """
        Retrieves information about a specific lead.

        :param lead_id: ID of the lead to retrieve.
        :return: Lead details as a dictionary.
        """
        params = {"id": lead_id}
        return self._make_request("crm.lead.get", params)

    def update_lead(self, lead_id: int, fields: dict) -> dict:
        """
        Updates an existing lead in the CRM.

        :param lead_id: ID of the lead to update.
        :param fields: Fields to update as a dictionary.
        :return: API response.
        """
        params = {
            "id": lead_id,
            "fields": fields
        }
        return self._make_request("crm.lead.update", params)

    def get_contact_id(self, first_name: str = None, last_name: str = None, phone: str = None) -> int:
        """
        Retrieves the contact ID by phone number or creates a new contact if it doesn't exist.

        :param first_name: First name of the contact.
        :param last_name: Last name of the contact.
        :param phone: Phone number of the contact.
        :param email: Email address of the contact.
        :return: ID of the contact.
        """
        try:
            # Search for the contact by phone number
            search_params = {"filter": {"PHONE": phone}, "select": ["ID"]}
            search_result = self._make_request("crm.contact.list", search_params)

            if search_result.get("total", 0) > 0:
                contact_id = search_result["result"][0]["ID"]
                self.logger.info(f"Found existing contact with ID: {contact_id}")
            else:
                # Create a new contact if not found
                contact_params = {
                    "fields": {
                        "NAME": first_name,
                        "LAST_NAME": last_name,
                        "PHONE": [{"VALUE": phone, "VALUE_TYPE": "WORK"}],
                        'OPENED': 'Y',
                        'TYPE_ID': 'CLIENT',
                    }
                }
                create_result = self._make_request("crm.contact.add", contact_params)
                contact_id = create_result["result"]
                self.logger.info(f"Created new contact with ID: {contact_id}")

            return contact_id

        except Exception as e:
            self.logger.error(f"Error in get_contact_id: {e}")
            raise

# Example usage
if __name__ == "__main__":
    WEBHOOK_URL = "https://yourcompany.bitrix24.com/rest/1/your_webhook_key"
    bitrix = Bitrix24API(WEBHOOK_URL)

    try:
        # Example: Add a new lead
        new_lead = bitrix.add_lead(
            title="New Potential Client",
            fields={
                "NAME": "John",
                "PHONE": [{"VALUE": "+1234567890", "VALUE_TYPE": "WORK"}],
                "EMAIL": [{"VALUE": "john@example.com", "VALUE_TYPE": "WORK"}]
            }
        )
        print("New lead created:", new_lead)

    except Exception as e:
        print(f"Error: {e}")
