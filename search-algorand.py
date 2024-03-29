
from methods import online

import threading

import re
import conn
import con_postg
import report



class Coinbot():

    def __init__(self, select_coin, select_db):
        """set the initial variable"""
        #initialize the database
        if select_db == 'postgresql':
            self.db = con_postg.DB()
        else:
            self.db = conn.DB()
        self.db.start()
        self.report = report.Report()
        self.online = online.Online_method()
        if select_coin == "Algorand":
            from generators import algorand
            self.crypto = algorand.Algobot()





    def manager(self, iter, method):
        """The main method managed the iteration ,call other methods and save the result in the BD calling a Bd module"""
        #result = self.check_method_online()

        # vaiable for statistics
        temp_match = 0
        temp_nf = 0
        temp_error = 0
        temp_critical_error = 0
        #how much iterations

        if method == 'online':
            for i in range(0,iter):
                
                #make call to the api online
                keys = self.crypto.generate_keypair()
                if keys[0] == False:
                    print('critical error')
                    exit()

                result = self.online.check_method_online(keys)
                
                
                # the answer is ok
                if result[0] == 'ok':

                    #the answer have amount or assets > 0
                    print(result[1]['acuracy'])
                    if result[1]['acuracy'] == 'good':
                        self.db.added_match(200, result[1]['acuracy'], result[1]['direction'][0],result[1]['direction'][1],result[1]['amount'],result[1]['assets'])

                    elif result[1]['acuracy'] == 'bad':
                        self.db.added_match(200, result[1]['acuracy'], result[1]['direction'][0],result[1]['direction'][1])
                    temp_match = temp_match + 1
                elif result[0] == 'error_not_handler':
                    try:
                        self.db.added_error(result[1], result[2])
                    except Exception as err:
                        self.db.added_error('999', 'internal error when try to save error not handler: {miss}'.format(miss = err) )
                    temp_error = temp_error + 1
                elif result[0] == 'error':
                    if result[1] == 'not_content':
                        print('Critical error, not content found in the response of the api online \n Are you connected to internet?')
                        print('\n status code: ', result[2])
                        temp_critical_error = temp_critical_error + 1
                        #remove this
                        self.db.added_error(900, result[2])
                        
                    elif result[1] == 'Not Found':
                        #normal error when the account is new
                        #100 is for new address
                        # not make nothing for now
                        temp_nf = temp_nf + 1
                        # 
                        self.db.added_error(900, result[2])
                    
                    elif result[1] == 'undeterminate for now':
                        #900 for unidentified error

                        # !!Atention!! . THIS CONDITIONAL WORK WITH ERROR. MAKE THE SAME OF 'NOT FOUND' COINDITIONAL
                        

                        # disable for make less petition to the database. now dont save the not found results, only stdistics save
                        #print(self.db.added_error(900, result[2]['message']))
                        
                        temp_nf = temp_nf + 1


                    # Area for insert new logs
                    # determine if is the first 100 request (stadistics is save after 100 request)
                if i == 100:

                    self.db.added_std(False, temp_match,temp_nf,temp_error,temp_critical_error)
                    self.report.reporting(temp_nf,temp_match,temp_error,temp_critical_error)

                    #more that 100 need update the session , not create a new session
                elif i % 100 == 0 and i > 100:

                    print(self.db.added_std(True, temp_match,temp_nf,temp_error,temp_critical_error))
                    self.report.reporting(temp_nf,temp_match,temp_error,temp_critical_error)


            #send stadistics to the database when the loop is finished and iteration < 100
            if iter < 100:
                self.db.added_std(False, temp_match,temp_nf,temp_error,temp_critical_error)
                self.report.reporting(temp_nf,temp_match,temp_error,temp_critical_error)

            elif iter > 100 and (iter - 1) % 100 != 0:
                self.db.added_std(True, temp_match,temp_nf,temp_error,temp_critical_error)
                self.report.reporting(temp_nf,temp_match,temp_error,temp_critical_error)
            





if __name__ == "__main__":

    # options for get results in database or
    options = []
    print('Select your action \n 1. search \n 2. get report \n 3. get match \n 4. get_error')
    x = int(input('write: '))
    if x == 1:
        options.append(1)
    elif x == 2:
        options.append(2)

    elif x == 3:
        options.append(3)

    elif x == 4:
        options.append(4)
    else:
        print('error')
        exit()

    if options[0] == 1:
        print('Write the number of your objetive blockchain \n 1. Algorand ')
        x = int(input('number: '))
        if x == 1:
            options.append('Algorand')
        else:
            print('error')
            exit()

        print('Write the number of your database \n 1. postgresql \n 2. sqlite3')
        x = int(input('number: '))
        if x == 1:
            options.append('postgresql')
        elif x == 2:
            options.append('sqlite')
        else:
            print('error')
            exit()

        print('Write the number of your method \n 1. Online')
        x = int(input('number: '))
        if x == 1:
            options.append('online')
        else:
            print('error')
            exit()

        print("set the iter number")
        try:
            itern = int(input("max iter :  "))
        except:
            print("write only integer numbers")

        Coin = Coinbot(options[1],options[2])
        print(options)
        Coin.manager(itern, options[3])
        exit()


    Coin = Coinbot('Algorand','postgresql')


    if options[0] == 2:
        print(Coin.db.getter_report())
        exit()
    elif options[0] == 3:
        print(Coin.db.getter_match())
        exit()
    elif options[0] == 4:
        print(Coin.db.getter_error())
        exit()

