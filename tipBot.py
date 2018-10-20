#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import sqlite3
import requests
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, RegexHandler


# config
db_name = 'accounts.db'
token = ''
alpha_api_token = ''
alpha_api_url = ""
password = ''
conn = sqlite3.connect(db_name, check_same_thread=False)
cursor = conn.cursor()


logging.basicConfig(filename='log.txt', filemode='a', level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# -- Tangram api

logging.info("Running Tip Bot")

def start(bot, update):

    button_list = [
        [KeyboardButton('💲 Balance 💲')],
        [KeyboardButton("💰 Claim 💰"),
         KeyboardButton("💸 Deposit 💸")],
        [KeyboardButton("🔴 Click 🔴"),
         KeyboardButton("📜 Help 📜")]
    ]

    reply_markup = ReplyKeyboardMarkup(button_list, resize_keyboard=True)
    bot.send_message(chat_id=update.message.from_user.id, text="Registering account..", reply_markup=reply_markup)
    accountReg(bot, update)


def balance(bot, update):
    if isRegistered(bot, update):
        username = update.message.from_user.username.lower()
        method = 'actor/wallet/balance'
        payload = {
                    "identifier": "{}".format(dbChecker('identifier', username)),
                    "password": "{}".format(password),
                    "address": "{}".format(dbChecker('address', username))
        }
        balance_resp = tangramRequest(method, payload).json()

        bot.send_message(chat_id=update.message.from_user.id, text="You have: {} Tangrams".format(balance_resp['balance']))


def claim(bot, update):
    if isRegistered(bot, update):
        username = update.message.from_user.username.lower()
        ammount = 10
        method = 'actor/wallet/reward'
        payload = {
                    "identifier": "{}".format(dbChecker('identifier', username)),
                    "password": "{}".format(password),
                    "address": "{}".format(dbChecker('address', username)),
                    "amount": ammount
                    }
        tangramRequest(method, payload)
        bot.send_message(chat_id=update.message.from_user.id, text="You won {} Tangrams!".format(ammount))


def tip(bot, update, args):
	tip_ammount = args[0]
	tip_username = args[1]

    if isRegistered(bot, update) and checkArgLen(bot, update, args):
        if getChatIDByUsername(tip_username) != 'None':
            username = update.message.from_user.username.lower()
            method = 'actor/wallet/transfer/funds'
            payload = {
                          "identifier": "{}".format(dbChecker('identifier', username)),
                          "password": "{}".format(password),
                          "account": "{}".format(dbChecker('address', username)),
                          "change": "{}".format(dbChecker('address', username)),
                          "link": "{}".format(getLinkByUsername(tip_username)),
                          "amount": "{}".format(tip_ammount)
                       }

            response = tangramRequest(method, payload)
            if response.status_code == 201:
                bot.send_message(chat_id=update.message.chat_id, text="✅ @{} sent {} Tangrams to @{}".format(update.message.from_user.username, tip_ammount, tip_username.strip('@')))
                bot.sendMessage(chat_id=getChatIDByUsername(tip_username), text="✅ User {} Sent you {} Tangs".format('@'+update.message.from_user.username, tip_ammount))
            else:
                bot.send_message(chat_id=update.message.chat_id, text="❌ {}".format(response.json()['message']))

        else:
            bot.send_message(chat_id=update.message.chat_id, text="❌ Your destinatary is not registered.. Receiving Tangram requires talking to @Tangram_TipBot First!")


def deposit(bot, update):
    if isRegistered(bot, update):
        username = update.message.from_user.username
        wallet = getLinkByUsername(username)
        bot.send_message(chat_id=update.message.from_user.id, text="Your deposit address is: {}".format(wallet))


def withdraw(bot, update, args):
	withdraw_address = args[1]
	withdraw_ammount = args[0]
	
    if isRegistered(bot, update) and checkArgLen(bot, update, args):
        username = update.message.from_user.username.lower()
        method = 'actor/wallet/transfer/funds'
        payload = {
                      "identifier": "{}".format(dbChecker('identifier', username)),
                      "password": "{}".format(password),
                      "account": "{}".format(dbChecker('address', username)),
                      "change": "{}".format(dbChecker('address', username)),
                      "link": "{}".format(withdraw_address),
                      "amount": "{}".format(withdraw_ammount)
                    }
        response = tangramRequest(method, payload)
        if response.status_code == 201:
            bot.send_message(chat_id=update.message.from_user.id, text="✔ Success!")
        else:
            bot.send_message(chat_id=update.message.from_user.id, text="❌ {}".format(response.json()['message']))


def help(bot, update):
    if isRegistered(bot, update):
        bot.send_message(chat_id=update.message.from_user.id,
                         text="""
💳 - Send Tangrams:
💳 - /tip [ammount] [@username]\n
➖ - Withdraw your Tangrams
➖ - /withdraw [ammount] [TGMadress]\n
➕ - Get your deposit address
➕ - /deposit\n
💲 - Get your balance
💲 - /balance\n
🎁 - Earn free Tangrams
🎁 - /claim\n
❓ - Show this help menu
❓ - /help\n\n

* Send /start if buttons disapear
""")


def click(bot, update):
    if isRegistered(bot, update):
        bot.send_message(chat_id=update.message.from_user.id, text="""
‼ WARNING ‼
Do not use this tipbot as your main wallet!\n
Tangram official Website:
https://tangrams.io/\n
Tangram Telegrams:
English - https://t.me/Tangrams
Brasil - https://t.me/tangrambrasil
Spanish - https://t.me/tangrames\n
Tangram Discord:
http://discord.tangrams.io\n
Tangram Manifesto:
manifesto.tangrams.io

""")


def tangramRequest(method, payload):
    url = alpha_api_url
    headers = {
                "accept": "application/json",
                "Authorization": alpha_api_token,
                "Content-Type": "application/json"
    }
    r = requests.post(url+method, headers=headers, json=payload)
    return r


def getChatIDByUsername(username):
    chat_id = dbChecker('user_chat_id', username.lower().strip('@'))
    return chat_id


def getLinkByUsername(username):
    link = dbChecker('address', username.lower().strip('@'))
    return link


def checkArgLen(bot, update, args):
    if len(args) == 2:
        return True
    else:
        bot.send_message(chat_id=update.message.from_user.id, text="❌ Internal server error")
        return False


def accountAPI():
    method = 'actor/wallet/create'
    payload = {'password': password}
    account = tangramRequest(method, payload)
    return account.json()


def walletAPI(account):
    method = 'actor/wallet/address'
    payload = {'identifier': account['id'], 'password': password}
    wallet = tangramRequest(method, payload).json()
    return wallet


# -- Database

def setup():
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

    cursor.execute(command)
    conn.commit()


def accountReg(bot, update):
    if not isRegistered(bot, update, command_check=False):
        account = accountAPI()
        account_name = update.message.from_user.username.lower()
        identifier = account['id']
        address = walletAPI(account)['address']
        user_chat_id = update.message.from_user.id
        command = """
                    INSERT INTO accounts (account_name, identifier, password, address, user_chat_id)
                    VALUES (?, ?, ?, ?, ?)
            
                """
        cursor.execute(command, (account_name, identifier, password, address, user_chat_id))
        conn.commit()
        bot.send_message(chat_id=update.message.from_user.id, text="Welcome to the Tangram tip bot!")
    else:
        bot.send_message(chat_id=update.message.from_user.id, text='User already registered.\nPress Help for more info.')



# command_check: send message if user is trying to send commands with out being registered
def isRegistered(bot, update, command_check=True):
    if update.message.from_user.username:
        user = dbChecker('account_name', update.message.from_user.username.lower())
        if user != 'None':
            return True
        elif user == 'None' and command_check == True:
            bot.send_message(chat_id=update.message.from_user.id, text="You are not registered..\nType /start")
            return False
        else:
            return False
    else:
        bot.send_message(chat_id=update.message.from_user.id, text="❌ You need to set an username before registering")



def dbChecker(select, where):
    command = """ SELECT %s FROM accounts WHERE account_name = ? """

    r = cursor.execute(command %(select), (where,))
    return ("%s" % r.fetchone())


def main():
    setup()
    update = Updater(token)
    dispatcher = update.dispatcher


    tip_handler = CommandHandler('tip', tip, pass_args=True)
    withdraw_handler = CommandHandler('withdraw', withdraw, pass_args=True)
    start_handler = RegexHandler(r'^/start$', start)
    balance_handler = RegexHandler(r'^(/balance|💲 Balance 💲)$', balance)
    claim_handler = RegexHandler(r'^(/claim|💰 Claim 💰)$', claim)
    deposit_handler = RegexHandler(r'^(/deposit|💸 Deposit 💸)$', deposit)
    click_handler = RegexHandler(r'^(/info|🔴 Click 🔴)$', click)
    help_handler = RegexHandler(r'^(/help|📜 Help 📜)$', help)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(balance_handler)
    dispatcher.add_handler(claim_handler)
    dispatcher.add_handler(deposit_handler)
    dispatcher.add_handler(tip_handler)
    dispatcher.add_handler(withdraw_handler)
    dispatcher.add_handler(click_handler)
    dispatcher.add_handler(help_handler)

    update.start_polling(timeout=30)

    update.idle()

    conn.close()


if __name__ == "__main__":
        main()
