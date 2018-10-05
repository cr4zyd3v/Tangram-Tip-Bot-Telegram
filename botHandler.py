import requests
import sqlite3
import json
from pprint import pprint
from time import sleep
#from threading import Thread

class botHandler():

#-- Telegram API
    
    def __init__(self, token, password, db_name, alpha_api_token):
        self.token = token
        self.url = 'https://api.telegram.org/bot{}/'.format(self.token)
        self.alpha_api_token = alpha_api_token
        self.alpha_api_url = "http://41.185.26.184:8081/"
        self.password = password
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()


    def getUrl(self, method, payload = ""):
        request = requests.get(self.url+method, params = payload)
        return request

    def getUpdates(self, offset=None, timeout=50):
        method = 'getUpdates'
        payload = {"offset": offset, 'timeout': timeout}
        try:    
            while True:
                updates  = self.getUrl(method, payload).json()
                if updates['ok'] == True:
                    updates = updates['result']
                    pprint(updates)
                    if len(updates) > 0:
                        return updates
                else:
                    print('Service unavaible')
        except Exception as e:
            print(e)

    def getChatID(self, update):
        chat_id = update['message']['chat']['id']
        return chat_id

    #should be ID_link instead chat
    def getChatID_Link(self, username):
        chat_id = self.dbChecker('user_chat_id', username)
        return chat_id

    def isGroup(self, update):
        if update != False:
            if update['message']['chat']['type'] == 'group' or update['message']['chat']['type'] == 'supergroup':
                return True
            else:
                return False
        else:
            return False

    def sendMessage(self, chat_id, text, update = False):
        if self.isGroup(update):
            text = "@{} ".format(self.getUsername(update))+text

        params = {
               "chat_id": chat_id,
               "text": text
            }
        message = self.getUrl("sendMessage?", params).json()
        
    def getText(self, update):
        if 'text' in update['message'].keys():
            user_text = update['message']['text']
            return user_text
        else:
            return False
    def getUsername(self, update):
        username = update['message']['from']['username'].lower()
        return username

    def getLinkByUsername(self, username):
        link = self.dbChecker('address', username)
        return link

    def infoBot(self, update):
        username = self.getUsername(update)
        return "{} ==> {}".format(username, self.getText(update))
        
#-- Tangram API
        
    def tangramRequest(self, method, payload):
        url = self.alpha_api_url
        headers = {"accept":"application/json",
                   "Authorization":self.alpha_api_token,
                   "Content-Type":"application/json"}
        r = requests.post(url+method, headers=headers, json=payload)
        return r


    def accountAPI(self):
        method = 'actor/wallet/create'
        payload = {'password': self.password}
        account = self.tangramRequest(method, payload).json()
        return account

    def walletAPI(self, account):
        method = 'actor/wallet/address'
        payload = {'identifier': account['id'], 'password': self.password}
        wallet = self.tangramRequest(method, payload).json()
        return wallet


    def claimTGM(self, update):
        method = 'actor/wallet/reward'
        payload = {
                    "identifier": "{}".format(self.dbChecker('identifier', self.getUsername(update))),
                    "password": "{}".format(self.password),
                    "address": "{}".format(self.dbChecker('address', self.getUsername(update))),
                    "amount": 10
                    }
        response = self.tangramRequest(method, payload).json()
        return response

    def tipTGM(self, update, user_text):
        method = 'actor/wallet/transfer/funds'
        payload = {
                      "identifier": "{}".format(self.dbChecker('identifier', self.getUsername(update))),
                      "password": "{}".format(self.password),
                      "account": "{}".format(self.dbChecker('address', self.getUsername(update))),
                      "change": "{}".format(self.dbChecker('address', self.getUsername(update))),
                      "link": "{}".format(self.getLinkByUsername(user_text[1])),
                      "amount": "{}".format(user_text[2])
                   }
        # !! json() decode in tangramBot (checking for status code)
        response = self.tangramRequest(method, payload)
        return response

    def balTGM(self, update):
        method = 'actor/wallet/balance'
        payload = {
                      "identifier": "{}".format(self.dbChecker('identifier', self.getUsername(update))),
                      "password": "{}".format(self.password),
                      "address": "{}".format(self.dbChecker('address', self.getUsername(update)))
                  }
        balance = self.tangramRequest(method, payload).json()
        
        return balance
    
    def depositTGM(self, update):
        wallet = self.getLinkByUsername(self.getUsername(update))
        return wallet
    
    def withdrawTGM(self, update, user_text):
        method = 'actor/wallet/transfer/funds'
        payload = {
                      "identifier": "{}".format(self.dbChecker('identifier', self.getUsername(update))),
                      "password": "{}".format(self.password),
                      "account": "{}".format(self.dbChecker('address', self.getUsername(update))),
                      "change": "{}".format(self.dbChecker('address', self.getUsername(update))),
                      "link": "{}".format(user_text[2]),
                      "amount": "{}".format(user_text[1])
                    }
        # !! json() decode in tangramBot (checking for status code)
        response = self.tangramRequest(method, payload)
        return response


#-- Database
    

    def setup(self):
        command = '''
                    CREATE TABLE IF NOT EXISTS accounts(
                                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                            account_name VARCHAR(255) NOT NULL UNIQUE,
                                            identifier VARCHAR(255) NOT NULL UNIQUE,
                                            password VARCHAR(255) NOT NULL,
                                            address VARCHAR(255) NOT NULL UNIQUE,
                                            user_chat_id INTEGER NOT NULL UNIQUE
                                          )
                  '''

        self.cursor.execute(command)
        self.conn.commit()
        
    def isRegistered(self, update):
        try:
            user = self.dbChecker('account_name', self.getUsername(update))
            if self.getUsername(update) == user:
                return True
            else:
                text = "You are not registered.. Type /start"
                if self.isGroup(update):
                    text = "@{} ".format(self.getUsername(update))+text

                self.sendMessage(self.getChatID(update), text)
                return False
            
        except Exception as e:
            print('$$$$$')
            print(e)
            return False
        
    def accountReg(self, update):
        account = self.accountAPI()
        account_name = self.getUsername(update)
        identifier = account['id']
        password = self.password
        address = self.walletAPI(account)['address']
        user_chat_id = update['message']['from']['id']
        command = """
                    INSERT INTO accounts (account_name, identifier, password, address, user_chat_id)
                    VALUES (?, ?, ?, ?, ?)
        
                  """
        try:
            self.cursor.execute(command, (account_name, identifier, password, address, user_chat_id))
            self.conn.commit()
            return "Welcome to the Tangram tip bot!\nType /help to see all commands"

        except:
            return "User already registered\n/help to check all commands"
            
    def dbChecker(self, select, where):   
        command = """ SELECT %s FROM accounts WHERE account_name = ? """
        
        r = self.cursor.execute(command %(select), (where,))
        return ("%s" % r.fetchone())
    

    
