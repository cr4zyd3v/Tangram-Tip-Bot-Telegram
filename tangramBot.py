from botHandler import botHandler
from pprint import pprint


#bot api
token = ''
db = 'accounts.db'
password = ''
alpha_api_token = ""

bot = botHandler(token, password, db, alpha_api_token)

#tangram api

def main():
    bot.setup()
    new_offset = bot.getUpdates()[0]['update_id']

    commands = {
            'tipTGM': '/tip',
            'balTGM': '/balance',
            'depositTGM': '/deposit',
            'withdrawTGM': '/withdraw',
            'accountReg': '/register'
        }


    
    while True:
        updates = bot.getUpdates(new_offset)
        for update in updates:
            pprint(update)
            #check commands loop
            try:
                user_text = bot.getText(update).split()

            # (3 args) param[0] == command / [1] == user_Link / [2] == ammount
            # send Tangrams to another user
                if user_text[0] == commands['tipTGM']:
                    if len(user_text) == 3:
                        bot.tipTGM(update, user_text)
                        print(user_text)
                    else:
                        pass
                        #send invalid

            # (1 arg) param[0] == command
            # request account balance
                elif user_text[0] == commands['balTGM']:
                    if len(user_text) == 1:
                        balance = bot.balTGM(update)
                        msg = "Your Balance is: %s" % balance['balance']
                        bot.sendMessage(bot.getChatID(update), msg)
                    else:
                        pass
                        #send invalid
                        
            # (1 arg) param[0] == command
            # request account deposit address (user public address)
                elif user_text[0] == commands['depositTGM']:
                    if len(user_text) == 1:
                        msg = "Your deposit address is: {}".format(bot.depositTGM(update))
                        bot.sendMessage(bot.getChatID(update), msg)
                    else:
                        pass
                        #send invalid
                        
                elif user_text[0] == commands['withdrawTGM']:
                    if len(user_text) == 3:
                        bot.withdrawTGM(update, user_text)
                        print(user_text)
                    else:
                        pass
                        #send invalid

                elif user_text[0] == commands['accountReg']:
                    if len(user_text) == 1:
                        bot.accountReg(update)
                else:
                    print('invalid command')
            except Exception as e:
                print(e)
                exit()


        new_offset += len(updates)



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        botHandler().conn.close()
        pass
        
