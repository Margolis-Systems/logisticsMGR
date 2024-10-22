# Server configs
server_port = 8000

# Mongo configs
con_str = 'mongodb://localhost:27017/'
# import os
# con_str = os.environ.get("MONGO_URI")
db = 'Logistics'
users_col = 'users'
docs_col = 'docs'
lists_col = 'lists'
user_items = ['id', 'name', 'last_name', 'phone', 'rank', 'car_plate', 'department']

#
doc_items = ['cat', 'description', 'quantity', 'notes']
# doc_items = ['num', 'cat', 'description', 'quantity', 'notes']
dictionary = {'num': "מס' דף וסד' של שורה", 'cat': "מספר קטלוגי", 'description': "שם", 'quantity': "כמות", 'notes': "הערות"}
descriptions = []