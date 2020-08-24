from pymongo import MongoClient
client = MongoClient(port=27017)
db = client.get_database('chatbot')
records = db.chat_records
print(records.count_documents({}))
new_chat = {
    'name': 'ram',
    'roll_no': 321,
    'branch': 'it'
}



