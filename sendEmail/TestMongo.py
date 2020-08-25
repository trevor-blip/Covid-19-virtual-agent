import requests
from firebase import  firebase


firebase = firebase.FirebaseApplication("https://covid19chatbot-840f8.firebaseio.com/", None)
data = {
    'Name': 'Blessing Mwale',
    'Email': 'blessingmwalein@outlook.com',
    'Phone': '0772440088'
}
result = firebase.post('covid19chatbot-840f8/Customer', data)

print(result)
