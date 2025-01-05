import os

# Server configs
server_port = 8000

# Mongo configs
con_str = os.environ.get("MONGO_URI")
# con_str = 'mongodb://localhost:27017/'
db = 'Logistics'
users_col = 'users'
docs_col = 'docs'
storage_col = 'storage'
lists_col = 'lists'
admin_department = 'לוגיסטיקה'

# Lists
user_items = ['id', 'name', 'last_name', 'rank', 'phone', 'car_plate', 'department', 'priv']
doc_items = []
dictionary = {}

# Sms configs
sms_account_id = os.environ.get("sms_account_id")
sms_user_id = os.environ.get("sms_user_id")
sms_user_pass = os.environ.get("sms_user_pass")
sms_sender = os.environ.get("sms_sender")