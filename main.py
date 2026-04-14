import json
import os
import time

import schedule

from config.bitrix24_conf import B24_WEBHOOK_URL, C22_CLASSY_TRADERS_STAGE_ID, C22_NEW_TRADERS_STAGE_ID, FOP_STAGE_ID, TOV_STAGE_ID
from config.config import FB_ACCESS_TOKEN, FB_AD_ACCOUNT_ID, FB_CUSTOM_AUDIENCE_ID, GOOGLE_CRED_PATH, SP_ADDRESSBOOK_ID, SP_REST_API_ID, SP_REST_API_SECRET, SP_TOKEN_STORAGE, GOOGLE_SHEETS_ID_customers
from config.youControl_conf import YC_API_KEY
from constants import CLASSY_TRADERS_KVED, NEW_TRADERS_KVED
from services.SendPulseClient.api import SendPulseManager
from services.bitrix24.api import Bitrix24API
from services.facebookAdsService.api import FacebookAudienceManager
from services.googleService.googleSheetsService import GoogleSheetsService
from services.youcontrol.api import YouControlAPI
from utils.Customers.index import Customer
from utils.Logger.index import Logger
from utils.main import filter_contractors_by_kved

log_level = os.getenv("LOG_LEVEL", "INFO")

log = Logger(name="I_YC_TO_B24", log_file="logs/app.log", level=log_level).get_logger()
fb_audience_manager = FacebookAudienceManager(FB_ACCESS_TOKEN, FB_CUSTOM_AUDIENCE_ID, ad_account_id=FB_AD_ACCOUNT_ID, logger=log)
send_pulse_manager = SendPulseManager(api_id=SP_REST_API_ID, api_secret=SP_REST_API_SECRET, token_storage=SP_TOKEN_STORAGE ,logger=log)

def send_new_connector_to_crm():
    pass

def send_emails_list_to_google_sheets(email_list:list):
    """
    Перетворює список в список списків для відповідності api

    :param email_list: Список з email.
    """
    log.info(f'email_list length - {len(email_list)}')
    google_sheets_service = GoogleSheetsService(GOOGLE_CRED_PATH, GOOGLE_SHEETS_ID_customers)
    new_values = [[item] for item in email_list] 
    google_sheets_service.append_data('Sheet1', new_values)
    log.info('Sending a list with emails to Google Sheets is successful')
    
def send_data_to_meta_ads(data_list:list):
    """
    Передає дані для відправки до meta ads api
    :param data_list: Список з словниками даних користувачів (email та phone).
    """

def procc_new_contractors_data(data, b24_api, stage_id):
    for ct_id in range(len(data)):
        try:
            log.info(f'[{ct_id+1}/{len(data)}] Processing of a new application')
            ct = data[ct_id]

            ct_phone = ct.get("phones", [""])
            if len(ct_phone)>0:
                ct_phone = ct_phone[0]
            else:
                ct_phone = ""

            ct_name = ct.get("name", "")
            name_parts = [part for part in ct_name.split() if part]
            ct_last_name = name_parts[0] if len(name_parts) > 0 else ""
            ct_first_name = name_parts[1] if len(name_parts) > 1 else ct_name
            ct_middle_name = " ".join(name_parts[2:]) if len(name_parts) > 2 else ""
            ct_legalForm = ct.get("legalForm", "ФОП")
            ct_code = ct.get("code", "")

            ct_address = ct.get("address", "")

            ct_economicActivities = ct.get("economicActivities", [{"description":""}])
            ct_economicActivities_list = [(f'{activity["code"]} {activity["description"]}') for activity in ct_economicActivities]
            ct_economicActivities_text = ".\n".join(ct_economicActivities_list)
            print("ct data: ",ct)
            print("ct_economicActivities: ",ct_economicActivities)

            triggers = ["ГРОМАДСЬКА ОРГАНІЗАЦІЯ", "ОБ'ЄДНАННЯ СПІВВЛАСНИКІВ БАГАТОКВАРТИРНОГО БУДИНКУ", 
                        "РЕЛІГІЙНА ОРГАНІЗАЦІЯ", "АДВОКАТСЬКЕ БЮРО", "БЛАГОДІЙНА ОРГАНІЗАЦІЯ"]

            if not ct_legalForm in triggers:
                result_created = b24_api.add_new_contractors_deal_params(stage_id=stage_id, first_name=ct_first_name, last_name=ct_last_name, middle_name=ct_middle_name, phone_number=ct_phone, title=ct_legalForm, type_activity=ct_economicActivities_text, address=ct_address,i_code=ct_code)
                log.info(f'Result created new contractor: {result_created}')
            else:
                log.info(f'Skip this category: {ct_legalForm}')

        except Exception as e:
            log.critical(f'Error occurred while processing the contractor: {e}')

def save_list_to_json(data_list, file_path):
    """
    Зберігає список у JSON-файл.
    
    :param data_list: Список для збереження.
    :param file_path: Шлях до JSON-файлу.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data_list, file, ensure_ascii=False, indent=4)
        print(f"Список успішно збережено у файл: {file_path}")
    except Exception as e:
        print(f"Помилка при збереженні списку у JSON-файл: {e}")

def run_daily_task():
    yc_api = YouControlAPI(YC_API_KEY,log)
    b24_api = Bitrix24API(B24_WEBHOOK_URL,log)

    try:
        log.info('Start of daily check')

        legalPersons_list, naturalPersons_list = yc_api.get_new_contractors(depth=1, only_new=True)
        save_list_to_json(legalPersons_list,"legal.json")
        save_list_to_json(naturalPersons_list,"natural.json")
 
        # Відправляє нових ТОВ в гілку B24
        if (legalPersons_list and len(legalPersons_list)>0):
            log.info(f'Start Processing of a new legalPersons')
            lp_new_treders_list, remaining_legalPersons_list = filter_contractors_by_kved(legalPersons_list, NEW_TRADERS_KVED, True)
            lp_classy_treders_list, remaining_legalPersons_list = filter_contractors_by_kved(remaining_legalPersons_list, CLASSY_TRADERS_KVED, True)

            procc_new_contractors_data(remaining_legalPersons_list, b24_api, TOV_STAGE_ID)
            procc_new_contractors_data(lp_new_treders_list, b24_api, C22_NEW_TRADERS_STAGE_ID)
            procc_new_contractors_data(lp_classy_treders_list, b24_api, C22_CLASSY_TRADERS_STAGE_ID)
        else:
            log.info(f'NON found new legalPersons_list')

        # Відправляє нових ФОП в гілку B24 та надсилає список з email до google sheets
        if (naturalPersons_list and len(naturalPersons_list)>0):
            log.info(f'Start Processing of a new naturalPersons')

            # send to bitrix24
            try:
                np_new_treders_list, remaining_naturalPersons_list = filter_contractors_by_kved(naturalPersons_list, NEW_TRADERS_KVED, True)
                np_classy_treders_list, remaining_naturalPersons_list = filter_contractors_by_kved(remaining_naturalPersons_list, CLASSY_TRADERS_KVED, True)

                procc_new_contractors_data(remaining_naturalPersons_list, b24_api, FOP_STAGE_ID)
                procc_new_contractors_data(np_new_treders_list, b24_api, C22_NEW_TRADERS_STAGE_ID)
                procc_new_contractors_data(np_classy_treders_list, b24_api, C22_CLASSY_TRADERS_STAGE_ID)
            except Exception as e:
                log.critical(f'Error when adding data to B24: {e}')
            
            # send to google ads
            try:
                email_list = [item["email"].lower() for item in naturalPersons_list if item["email"]]
                send_emails_list_to_google_sheets(email_list)
            except Exception as e:
                log.critical(f'Error when adding data to Google ADS: {e}')


            # send to facebook ads
            try:
                customers = [
                    Customer(item["email"], item["phones"][0]).to_hashed_data()
                    for item in naturalPersons_list
                    if item.get("email") and item.get("phones") and item["phones"][0]
                ]
                resp_added_to_fb = fb_audience_manager.add_customers(customers)
            except Exception as e:
                log.critical(f'Error when adding data to Facebook ADS: {e}')

            # send to send pulse
            try:
                contacts = [
                    {"email": p["email"], "variables": {"phone": p["phones"][0]}}
                    for p in naturalPersons_list
                    if p.get("email") and p.get("phones") and p["phones"][0]
                ]
                send_pulse_manager.add_contacts(addressbook_id=SP_ADDRESSBOOK_ID, contacts=contacts)
            except Exception as e:
                log.critical(f'Error when adding data to SendPulse: {e}')
        else:
            log.info(f'NON found new naturalPersons_list')

        

    except Exception as e:
        log.critical(f'To program has ended with error: {e}')
    
    log.info('End of daily check')


def main():
    log.info('Program start')
    
    while True:
        schedule.run_pending() 
        time.sleep(1)

if __name__ == "__main__":
    schedule.every(3).minutes.do(run_daily_task)
    main()
    # run_daily_task()
