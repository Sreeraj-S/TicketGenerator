import gspread
from oauth2client.service_account import ServiceAccountCredentials
import uuid

class Sheets:
    def __init__(self) -> None:
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name("<json>", self.scope)
        self.client = gspread.authorize(self.credentials)
        self.spreadsheet = self.client.open_by_key("<sheetid>")
        self.worksheet = self.spreadsheet.sheet1

    def qrCodeAvilable(self) -> list:
        uuids = []
        all_values = self.worksheet.get_all_values()
        for rows in all_values:
            if rows[3] == '0':
                uuids.append(rows[2])
        return uuids

    def generatedTicket(self,uuid) -> None:
        all_values = self.worksheet.get_all_values()
        for idx_,rows in enumerate(all_values):
            if rows[2] == uuid:
                cell_num = f"D{idx_+1}"
                self.worksheet.update(range_name=cell_num,values=1)

    def generateQrcode(self,no) -> bool:
        try:
            for i in range(no):
                all_values = self.worksheet.get_all_values()
                generated_uuid = str(uuid.uuid4())
                cell_num = f"B{len(all_values)+1}"
                self.worksheet.update(range_name=cell_num,values=generated_uuid)
                generated_uuid = str(uuid.uuid4())
                cell_num = f"D{len(all_values)+1}"
                self.worksheet.update(range_name=cell_num,values=0)
                cell_num = f"E{len(all_values)+1}"
                self.worksheet.update(range_name=cell_num,values=0)
            return True
        except:
            return False
        
if __name__=="__main__":
    sheet = Sheets()
    print(sheet.qrCodeAvilable())
        