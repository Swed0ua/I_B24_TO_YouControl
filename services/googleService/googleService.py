from google.oauth2.service_account import Credentials
import gspread

class GoogleService:
    def __init__(self, credentials_file: str):
        """Google Basic Service for Authentication and API Customers."""
        self.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.creds = Credentials.from_service_account_file(credentials_file, scopes=self.scope)
        self.client = gspread.authorize(self.creds)
