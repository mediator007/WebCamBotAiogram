import sys
sys.path.append('../')

from loguru import logger
import gspread

from backoff import backoff
from utils.config import main_file, registration_file


class GDriveExport:

    @backoff()
    def export_registration(self) -> tuple:
        """
        Выгружаем изменения из registration file
        """
        gc = gspread.service_account(filename="../webcambot-ad6a9a73eef6.json")
        sh = gc.open(registration_file)
        worksheet = sh.sheet1
        result = worksheet.get_all_records(expected_headers=())
        return result

    
    @backoff()
    def export_main(self) -> tuple:
        """
        Выгружаем изменения из main file
        """
        gc = gspread.service_account(filename="../webcambot-ad6a9a73eef6.json")
        sh = gc.open(main_file)
        worksheet = sh.sheet1
        result = worksheet.get_all_records(expected_headers=())
        return result