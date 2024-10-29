import requests
from src import config


class Sms:
    def __init__(self):
        self.target_url = 'http://port2sms.com/Scripts/mgrqispi.dll'
        self.AccountID = config.sms_account_id
        self.UserID = config.sms_user_id
        self.UserPass = config.sms_user_pass
        self.sender = config.sms_sender

    def send_sms(self, msg, _dist_numbers=[]):
        dist_numbers = ''
        if not _dist_numbers:
            return
        for num in _dist_numbers:
            dist_numbers += num + ';'
        post_data = {'Appname': 'Port2SMS', 'prgname': 'HTTP_SimpleSMS1', 'AccountID': self.AccountID,'UserID': self.UserID,
                     'UserPass': self.UserPass, 'Phone': dist_numbers, 'Text': msg, 'Sender': self.sender}
        return requests.post(self.target_url, data=post_data)
