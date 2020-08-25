from datetime import datetime
class Log:
    def __init__(self):
        pass

    def saveConversations(self, sessionID, usermessage,botmessage,intent,dbConn):

        self.now = datetime.now()
        self.date = self.now.date()
        self.current_time = self.now.strftime("%H:%M:%S")

        mydict = {"sessionID":sessionID,"User Intent" : intent ,"User": usermessage, "Bot": botmessage, "Date": str(self.date) + "/" + str(self.current_time)}

        dbConn.post('covid19chatbot-840f8/conversations', mydict)
    def saveCases(self, search,botmessage,dbConn):
        myquery = {"search": search}
        cases_dict = {"search":search,"cases": botmessage}
        newvalues = {"$set": cases_dict}
        dbConn.post('covid19chatbot-840f8/Cases', cases_dict)

#still working on this one function

    def getcasesForEmail(self, search,botmessage,dbConn):
        records = dbConn.get('covid19chatbot-840f8/cases', '')
        # return records.find_one({'search': search})

