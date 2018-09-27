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
            'accountReg': '/start',
            'helpTGM':  '/help'
        }

    messages = {
                       'help': 'Send someone Tangrams:\n'
                       '/tip @username ammount\neg. /tip @marciksz 10\n'
                       '\n'
                       'Send your Tangrams to a public address:\n'
                       '/withdraw Tangram_address ammount\neg. /withdraw tgm_vJmytwoDtvMpNAD2bWuerY1LSxdobNejMbbrFeNbdMpHkQyLFb88n1CVBK6WJaM5v5u9cnLtoYwop6Avu12EAu1V6T2KUGi9kJpa8E 37\n'
                       '\n'
                       'Return your balance:\n'
                       '/balance\n'
                       '\n'
                       'Return address to add Tangrams to the bot:\n'
                       '/deposit\n'       
               }


    
    while True:
        updates = bot.getUpdates(new_offset)
        for update in updates:
            pprint(update)
            #check commands loop
            try:
                user_text = bot.getText(update).split()

             # (1 arg) param[0] == command
             # request account registration
                if user_text[0] == commands['accountReg']:
                    if len(user_text) == 1:
                        msg = bot.accountReg(update)
                        bot.sendMessage(bot.getChatID(update), msg)
                    else:
                        bot.sendMessage(bot.getChatID(update), "Internal server error")

                if bot.isRegistered(update):
                # (3 args) param[0] == command / [1] == user_Link / [2] == ammount
                # send Tangrams to another user
                    if user_text[0] == commands['tipTGM']:
                        if len(user_text) == 3:
                            user_text[1] = user_text[1].strip('@')
                            response = bot.tipTGM(update, user_text)
                            if response.status_code == 201:
                                bot.sendMessage(bot.getChatID(update), "You sent {} Tangrams to {}".format(user_text[2], user_text[1]))
                                bot.sendMessage(bot.getChatID_Link(update), "User {} Sent you {} Tangs".format('@'+bot.getUsername(update), user_text[2]))
                            else:
                                bot.sendMessage(bot.getChatID(update), response.json()['message'])
                        else:
                            bot.sendMessage(bot.getChatID(update), "Internal server error")

                # (1 arg) param[0] == command
                # request account balance
                    elif user_text[0] == commands['balTGM']:
                        if len(user_text) == 1:
                            balance = bot.balTGM(update)
                            msg = "Your Balance is: %s" % balance['balance']
                            bot.sendMessage(bot.getChatID(update), msg)
                        else:
                            bot.sendMessage(bot.getChatID(update), "Internal server error")
                            
                # (1 arg) param[0] == command
                # request account deposit address (user public address)
                    elif user_text[0] == commands['depositTGM']:
                        if len(user_text) == 1:
                            msg = "Your deposit address is: {}".format(bot.depositTGM(update))
                            bot.sendMessage(bot.getChatID(update), msg)
                        else:
                            bot.sendMessage(bot.getChatID(update), "Internal server error")

                 # (3 arg) param[0] == command / param[1] == link / param[2] == ammount
                 # request withdraw to a Tangram public address
                    elif user_text[0] == commands['withdrawTGM']:
                        if len(user_text) == 3:
                            response = bot.withdrawTGM(update, user_text)
                            print(response)
                            bot.sendMessage(bot.getChatID(update), response['message'])
                        else:
                            bot.sendMessage(bot.getChatID(update), "Internal server error")

                 # (1 arg) param[0] == command
                 # request bot help
                    elif user_text[0] == commands['helpTGM']:
                        if len(user_text) == 1:
                            msg = messages['help']
                            bot.sendMessage(bot.getChatID(update), msg)
                        else:
                            bot.sendMessage(bot.getChatID(update), "Internal server error")
                    else:
                        print('invalid command')
                        
            except Exception as e:
                print("\n##############################")
                print(e)
                print("################################\n")
                pass
                


        new_offset += len(updates)



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        bot.conn.close()
        exit()     
