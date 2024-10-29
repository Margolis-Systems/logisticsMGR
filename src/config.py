import os

# Server configs
server_port = 8000

# Mongo configs
# con_str = 'mongodb://localhost:27017/'
con_str = os.environ.get("MONGO_URI")
db = 'Logistics'
users_col = 'users'
docs_col = 'docs'
lists_col = 'lists'
user_items = ['id', 'name', 'last_name', 'phone', 'rank', 'car_plate', 'department']

# Lists
doc_items = ['cat', 'description', 'quantity', 'notes']
dictionary = {'num': "מס' דף וסד' של שורה", 'cat': "מספר קטלוגי", 'description': "שם", 'quantity': "כמות", 'notes': "הערות", 'to_ret':"כמות להחזרה"}
descriptions = []

# Sms configs
sms_account_id = os.environ.get("sms_account_id")
sms_user_id = os.environ.get("sms_user_id")
sms_user_pass = os.environ.get("sms_user_pass")
sms_sender = os.environ.get("sms_sender")