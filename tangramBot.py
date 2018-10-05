from botHandler import botHandler
from pprint import pprint


#bot api
token = ''
db = 'accounts.db'
password = ''
alpha_api_token = ''

bot = botHandler(token, password, db, alpha_api_token)

#tangram api

def main():
    bot.setup()
    new_offset = bot.getUpdates()[0]['update_id']
    print(new_offset)

    commands = {
            'tipTGM': '/tip',
            'balTGM': '/balance',
            'depositTGM': '/deposit',
            'withdrawTGM': '/withdraw',
            'accountReg': '/start',
            'helpTGM':  '/help',
            'claimTGM': '/claim'
        }

    messages = {
                       'help': 'Send someone Tangrams:\n'
                       '/tip @username ammount\neg. /tip @marciksz 10\n'
                       '\n'
                       'Send your Tangrams to a public address:\n'
                       '/withdraw ammount Tangram_address\neg. /withdraw 37 tgm_vJmytwoDtvMpNAD2...\n'
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
            #check commands loop
            try:
                user_text = bot.getText(update)
                if user_text != False:
                    user_text= user_text.split()

                 # (1 arg) param[0] == command
                 # request account registration
                    if user_text[0] == commands['accountReg']:
                        if len(user_text) == 1:
                            msg = bot.accountReg(update)
                            bot.sendMessage(bot.getChatID(update), msg, update)
                            print(bot.infoBot(update))
                        else:
                            bot.sendMessage(bot.getChatID(update), "Internal server error\n/help for bot usage help", update)

                    elif bot.isRegistered(update):
                    # (3 args) param[0] == command / [1] == user_Link / [2] == ammount
                    # send Tangrams to another user
                        if user_text[0] == commands['tipTGM']:
                            if len(user_text) == 3:
                                user_text[1] = user_text[1].strip('@')
                                user_text[1] = user_text[1].lower()
                                if bot.getLinkByUsername(user_text[1]) != 'None':
                                    response = bot.tipTGM(update, user_text)
                                    if response.status_code == 201:
                                        bot.sendMessage(bot.getChatID(update), "You sent {} Tangrams to {}".format(user_text[2], user_text[1]), update)
                                        bot.sendMessage(bot.getChatID_Link(user_text[1]), "User {} Sent you {} Tangs".format('@'+bot.getUsername(update), user_text[2]), update)
                                        print(bot.infoBot(update))
                                    else:
                                        bot.sendMessage(bot.getChatID(update), response.json()['message'], update)
                                        print(bot.infoBot(update))
                                else:
                                    bot.sendMessage(bot.getChatID(update), "Your destinatary is not registered.. Receiving Tangram requires talking to @Tangram_Bot First!", update)
                            else:
                                bot.sendMessage(bot.getChatID(update), "Internal server error\n/help for bot usage help", update)

                    # (1 arg) param[0] == command
                    # request account balance
                        elif user_text[0] == commands['balTGM']:
                            if len(user_text) == 1:
                                balance = bot.balTGM(update)
                                msg = "Your Balance is: %s" % balance['balance']
                                bot.sendMessage(bot.getChatID(update), msg, update)
                                print(bot.infoBot(update))
                            else:
                                bot.sendMessage(bot.getChatID(update), "Internal server error\n/help for bot usage help", update)

                        elif user_text[0] == commands['claimTGM']:
                            if len(user_text) == 1:
                                bot.claimTGM(update)
                                msg = 'You claimed 10 Tangrams'
                                bot.sendMessage(bot.getChatID(update), msg, update)
                                print(bot.infoBot(update))
                            else:
                                bot.sendMessage(bot.getChatID(update), "Internal server error\n/help for bot usage help", update)

                                
                    # (1 arg) param[0] == command
                    # request account deposit address (user public address)
                        elif user_text[0] == commands['depositTGM']:
                            if len(user_text) == 1:
                                msg = "Your deposit address is: {}".format(bot.depositTGM(update))
                                bot.sendMessage(bot.getChatID(update), msg, update)
                                print(bot.infoBot(update))
                            else:
                                bot.sendMessage(bot.getChatID(update), "Internal server error\n/help for bot usage help", update)

                     # (3 arg) param[0] == command / param[1] == ammount / param[2] == link
                     # request withdraw to a Tangram public address
                        elif user_text[0] == commands['withdrawTGM']:
                            if len(user_text) == 3:
                                response = bot.withdrawTGM(update, user_text)
                                if response.status_code == 201:
                                    bot.sendMessage(bot.getChatID(update), "Success!", update)
                                    print(bot.infoBot(update))
                                else:
                                    bot.sendMessage(bot.getChatID(update), response.json()['message'], update)
                                    print(bot.infoBot(update))
                            else:
                                bot.sendMessage(bot.getChatID(update), "Internal server error\n/help for bot usage help", update)

                     # (1 arg) param[0] == command
                     # request bot help
                        elif user_text[0] == commands['helpTGM']:
                            if len(user_text) == 1:
                                msg = messages['help']
                                bot.sendMessage(bot.getChatID(update), msg)
                                print(bot.infoBot(update))
                            else:
                                bot.sendMessage(bot.getChatID(update), "Internal server error\n/help for bot usage help")
                        else:
                            bot.sendMessage(bot.getChatID(update), "Invalid Command\n/help to check the commands", update)
                        
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
