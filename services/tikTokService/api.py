import requests
import hashlib
import csv

class TikTokAPI:
    def __init__(self, access_token: str, advertiser_id: str):
        self.access_token = access_token
        self.advertiser_id = advertiser_id
        self.base_url = "https://business-api.tiktok.com/open_api/v1.3"

    def get_access_token(self, app_id: str, secret: str, auth_code: str):
        url = f"{self.base_url}/oauth2/access_token/"
        payload = {
            "app_id": app_id,
            "secret": secret,
            "auth_code": auth_code
        }
        response = requests.post(url, json=payload)
        return response.json()

    def hash_email_sha256(self, email: str) -> str:
        return hashlib.sha256(email.strip().lower().encode('utf-8')).hexdigest()

    def write_hashes_to_csv(self, hashes: list, filename: str):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            for h in hashes:
                writer.writerow([h])

    def md5_of_file(self, filename: str) -> str:
        hash_md5 = hashlib.md5()
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def upload_audience_file(self, custom_audience_id: str, csv_filename: str, id_type: str = "EMAIL", calculate_type: str = "EMAIL_SHA256"):
        url = f"{self.base_url}/dmp/custom_audience/file/upload/"
        file_signature = self.md5_of_file(csv_filename)
        headers = {
            "Access-Token": self.access_token,
        }
        data = {
            "advertiser_id": self.advertiser_id,
            "custom_audience_id": custom_audience_id,
            "id_type": id_type,
            "calculate_type": calculate_type,
            "file_signature": file_signature,
        }
        with open(csv_filename, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, headers=headers, data=data, files=files)
        return response

    def update_audience(self, custom_audience_id: str, file_paths: list, action: str = "APPEND"):
        url = f"{self.base_url}/dmp/custom_audience/update/"
        headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        payload = {
            "advertiser_id": self.advertiser_id,
            "custom_audience_id": custom_audience_id,
            "action": action,
            "file_paths": file_paths
        }
        response = requests.post(url, headers=headers, json=payload)
        return response

    def get_audience(self, custom_audience_ids: list):
        url = f"{self.base_url}/dmp/custom_audience/get/"
        headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        payload = {
            "advertiser_id": self.advertiser_id,
            "custom_audience_ids": custom_audience_ids
        }
        response = requests.get(url, headers=headers, params=payload)
        return response