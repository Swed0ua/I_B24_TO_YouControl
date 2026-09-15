import logging

import requests


class NotificationService:
    def __init__(self, base_url: str, api_key: str, logger: logging.Logger = None):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": api_key,
        }
        self.logger = logger

    def send(self, phone: str, message_type: str = "welcome_new_contractor", idempotency_key: str = None):
        # TODO: temporary disabled 
        # return
        if not phone:
            return None

        body = {"phone": phone, "message_type": message_type}
        if idempotency_key:
            body["idempotency_key"] = idempotency_key

        try:
            resp = requests.post(
                f"{self.base_url}/v1/notifications",
                headers=self.headers,
                json=body,
                timeout=5,
            )
            if resp.status_code in (200, 202):
                self.logger.info(f"Notification {resp.status_code} for {phone}: {resp.json()}")
            else:
                self.logger.error(f"Notification failed {resp.status_code} for {phone}: {resp.text}")
            return resp
        except Exception as e:
            self.logger.error(f"Notification request error for {phone}: {e}")
            return None

    def send_to_phones(self, phones: list, code: str = "", message_type: str = "welcome_new_contractor"):
        for phone in phones or []:
            if not phone:
                continue
            key = f"{code}:{phone}" if code else None
            self.send(phone, message_type=message_type, idempotency_key=key)
