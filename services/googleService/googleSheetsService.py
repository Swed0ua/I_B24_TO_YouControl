from .googleService import GoogleService
from typing import List, Dict

class GoogleSheetsService(GoogleService):
    def __init__(self, credentials_file: str, sheet_id: str):
        """Service to work with Google Sheets."""
        super().__init__(credentials_file)

        self.sheet = self.client.open_by_key(sheet_id)


    def get_data(self, sheet_name: str) -> List[Dict]:
        worksheet = self.sheet.worksheet(sheet_name)
        return worksheet.get_all_records()

    def append_data(self, sheet_name: str, data: List[List]):
        worksheet = self.sheet.worksheet(sheet_name)
        worksheet.append_rows(data)

    def update_cell(self, sheet_name: str, row: int, col: int, value):
        worksheet = self.sheet.worksheet(sheet_name)
        worksheet.update_cell(row, col, value)

    def clear_sheet(self, sheet_name: str):
        worksheet = self.sheet.worksheet(sheet_name)
        worksheet.clear()
