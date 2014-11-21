# Yay tests!

import csv
import unittest
import bot as botcode
import time
import pdb

#########################
### FAKE IRCSOCK  ### 
#########################

class fake_ircsock(object):

    def __init__(self):
        self.sent_messages = []
    
    def send(self, msg):
        self.sent_messages.append(msg)

    def sent_message(self):
        return self.sent_messages[-1]
        
    def has_sent_message(self):
        if self.sent_messages:
            return True
        else:
            return False

def fake_irc_start():
    ircsock = fake_ircsock()
    return ircsock   


class TestBotClass(unittest.TestCase):

    def setUp(self):
        self.bot = botcode.Bot()

    def test_csv_source(self):
        self.assertEqual(self.bot.nick_source, 'nicks.csv')

    def test_known_nicks_setup(self):
        bot = botcode.Bot('test_nicks.csv')
        self.assertEqual(bot.known_nicks, [['Alice'], ['Bob']])

    def test_wait_time(self):
        self.assertEqual(self.bot.wait_time, botcode.wait_time)

    def test_custom_wait_time(self):
        bot = botcode.Bot(wait_time=30)
        self.assertEqual(bot.wait_time, 30)

    def test_newcomers_setup(self):
        self.assertEqual(self.bot.newcomers, [])

    def test_add_nick_to_list(self):
        self.bot.known_nicks = [['Fluffy'], ['Spot']]
        self.bot.add_known_nick('Roger')
        self.assertEqual(self.bot.known_nicks,[['Fluffy'], ['Spot'], ['Roger']])

    def test_add_nick_underscore_removal(self):
        self.bot.known_nicks = [['Fluffy'], ['Spot']]
        self.bot.add_known_nick('Roger__')
        self.assertEqual(self.bot.known_nicks,[['Fluffy'], ['Spot'], ['Roger']])

    def test_add_nick_to_csv(self):
        bot = botcode.Bot('test_nicks.csv')
        bot.add_known_nick('Roger__')
        with open('test_nicks.csv', 'rb') as csv_file:
            known_nicks = []
            csv_file_data = csv.reader(csv_file, delimiter=',', quotechar='|')
            for row in csv_file_data:
                known_nicks.append(row)
            self.assertEqual(known_nicks, [['Alice'], ['Bob'], ['Roger']])

    def tearDown(self):
        with open('test_nicks.csv', 'w') as csv_file:
            csv_file.write('Alice\nBob\n')

class TestNewComerClass(unittest.TestCase):

    def setUp(self):
        self.bot = botcode.Bot('test_nicks.csv')
        self.NewComer = botcode.NewComer('Nancy', self.bot)

    def test_newcomer_init_nick(self):
        self.assertEqual(self.NewComer.nick, 'Nancy')

    def test_newcomer_init_born(self):
        newComer = botcode.NewComer('Baby', botcode.Bot())
        time.sleep(0.01)
        self.assertAlmostEqual(newComer.born, time.time() - .01, places=2)

    def test_newcomer_around_for(self):
        newComer = botcode.NewComer('Shauna', botcode.Bot())
        time.sleep(0.01)
        self.assertAlmostEqual(newComer.around_for(), .01, places=2)

class TestJoinIRC(unittest.TestCase):

    def setUp(self):
        self.ircsock = fake_irc_start()
        self.bot = botcode.Bot()
        
    def test_sent_messages(self):
        botcode.join_irc(self.ircsock)
        expected = ["USER {} {} {} :This is http://openhatch.org/'s greeter bot.\n".format(botcode.botnick, botcode.botnick, botcode.botnick), 'NICK {}\n'.format(botcode.botnick), 'JOIN {} \n'.format(botcode.channel)]
        self.assertEqual(self.ircsock.sent_messages,expected)

class TestProcessNewcomers(unittest.TestCase):

    def setUp(self):
        self.bot = botcode.Bot('test_nicks.csv', wait_time=.1)
        botcode.NewComer('Harry', self.bot)
        botcode.NewComer('Hermione', self.bot)
        time.sleep(.15)
        botcode.NewComer('Ron', self.bot)
        self.ircsock = fake_irc_start()

    def test_check_new_newcomers(self):
        botcode.process_newcomers(self.bot, [i for i in self.bot.newcomers if i.around_for() > self.bot.wait_time], ircsock=self.ircsock, welcome=0)
        self.assertEqual(len(self.bot.newcomers), 1)

    def test_check_new_known_nicks(self):
        botcode.process_newcomers(self.bot, [i for i in self.bot.newcomers if i.around_for() > self.bot.wait_time], ircsock=self.ircsock, welcome=0)
        self.assertEqual(self.bot.known_nicks,[['Alice'],['Bob'],['Harry'],['Hermione']])
        
    def test_welcome_nick(self):
        botcode.process_newcomers(bot=self.bot, newcomerlist=[i for i in self.bot.newcomers if i.around_for() > self.bot.wait_time], ircsock=self.ircsock, welcome=1)
        self.assertEqual(self.ircsock.sent_message(), "PRIVMSG {0} :Welcome Hermione!  The channel is pretty quiet right now, so I thought I'd say hello, and ping some people (like {1}) that you're here.  If no one responds for a while, try emailing us at hello@openhatch.org or just try coming back later.  FYI, you're now on my list of known nicknames, so I won't bother you again.\n".format(botcode.channel,botcode.greeter_string(botcode.channel_greeters)))
        
    def tearDown(self):
        with open('test_nicks.csv', 'w') as csv_file:
            csv_file.write('Alice\nBob\n')

class TestParseMessages(unittest.TestCase):

    def test_good_string(self):
        ircmsg, actor = botcode.parse_messages(":vader!darth@darkside.org PRIVMSG #deathstar : I find your lack of faith disturbing")
        self.assertEqual([ircmsg, actor], [':vader!darth@darkside.org PRIVMSG #deathstar : I find your lack of faith disturbing', 'vader'])
    
    def test_bad_string(self):
        ircmsg, actor = botcode.parse_messages("we should probably replace this with a bad string more likely to occur")
        self.assertEqual([ircmsg, actor], [None, None])

class TestMessageResponse(unittest.TestCase):

    def setUp(self):
        self.bot = botcode.Bot('test_nicks.csv')
        botcode.NewComer('Chappe', self.bot)
        self.ircsock = fake_irc_start()

    def test_newcomer_speaking(self):
        botcode.message_response(self.bot,"~q@r.m.us PRIVMSG {} :hah".format(botcode.channel),"Chappe", ircsock=self.ircsock)  # Standard message by newcomer
        nicklist = [i.nick for i in self.bot.newcomers]   # Makes a list of newcomers nicks for easy asserting
        self.assertEqual(nicklist, ['Chappe'])

    def test_oldtimer_speaking(self):
        botcode.message_response(self.bot,"~q@r.m.us PRIVMSG {} :hah".format(botcode.channel),"Alice", ircsock=self.ircsock)  # Standard message by oldtimer
        nicklist = [i.nick for i in self.bot.newcomers]   # Makes a list of newcomers nicks for easy asserting
        self.assertEqual(nicklist, [])
        
    def test_join(self):
        botcode.message_response(self.bot,"JOIN {} right now!".format(botcode.channel),"Shauna", ircsock=self.ircsock)   # Replace with actual ping message 
        self.assertEqual(self.bot.newcomers[1].nick,'Shauna')
 
    def test_part(self):
        botcode.message_response(self.bot,"JOIN {} right now!".format(botcode.channel),"Shauna", ircsock=self.ircsock)   # Replace with actual ping message
        self.assertEqual(len(self.bot.newcomers), 2)
        botcode.message_response(self.bot,"PART {}".format(botcode.channel),"Shauna", ircsock=self.ircsock)   # Replace with actual ping message
        self.assertEqual(len(self.bot.newcomers), 1)  
        
    def test_hello(self):
        botcode.message_response(self.bot,"PRIVMSG sup {}".format(botcode.botnick),"Shauna", ircsock=self.ircsock)
        self.assertTrue(self.ircsock.has_sent_message())
        self.assertIn(self.ircsock.sent_message(), ["PRIVMSG {} :hello Shauna\n".format(botcode.channel), "PRIVMSG {} :hi Shauna\n".format(botcode.channel), "PRIVMSG {} :hey Shauna\n".format(botcode.channel), "PRIVMSG {} :yo Shauna\n".format(botcode.channel), "PRIVMSG {} :sup Shauna\n".format(botcode.channel)])
        
    def test_help(self):
        botcode.message_response(self.bot,"PRIVMSG info {}".format(botcode.botnick),"Shauna", ircsock=self.ircsock)
        self.assertTrue(self.ircsock.has_sent_message())
        self.assertEqual(self.ircsock.sent_message(), "PRIVMSG {} :I'm a bot!  I'm from here <https://github.com/shaunagm/oh-irc-bot>.  You can change my behavior by submitting a pull request or by talking to shauna.\n".format(botcode.channel))
        
    def test_wait_time_from_admin(self):
        botcode.message_response(self.bot,"{} --wait-time 40".format(botcode.botnick),"shauna",ircsock=self.ircsock)     # Channel-greeters may also be changed.  :(
        self.assertEqual(self.ircsock.sent_message(), "PRIVMSG {} :shauna the wait time is changing to 40 seconds.\n".format(botcode.channel))
 
    def test_wait_time_from_non_admin(self):  
        botcode.message_response(self.bot,"{} --wait-time 40".format(botcode.botnick),"Impostor",ircsock=self.ircsock)     # Channel-greeters may also be changed.  :(  
        self.assertEqual(self.ircsock.sent_message(), "PRIVMSG {0} :Impostor you are not authorized to make that change. Please contact one of the channel greeters, like {1}, for assistance.\n".format(botcode.channel,botcode.greeter_string(botcode.channel_greeters)))
        
    def test_pong(self):
        botcode.message_response(self.bot,"PING :","Shauna",ircsock=self.ircsock)   # Replace this with actual ping message
        self.assertEqual(self.ircsock.sent_message(),"PONG :pingis\n")
        
    def test_bad_pong(self):
        botcode.message_response(self.bot,"PING!!! :","Shauna",ircsock=self.ircsock)   # Replace this with actual ping message
        self.assertFalse(self.ircsock.has_sent_message())   

    def tearDown(self):
        with open('test_nicks.csv', 'w') as csv_file:
            csv_file.write('Alice\nBob\n')

class TestGreeterString(unittest.TestCase):     
    
    def setUp(self):
        self.bot = botcode.Bot('test_nicks.csv')
    
    def test_one_greeter(self):     
       greeterstring = botcode.greeter_string(['shauna'])
       self.assertEqual(greeterstring, "shauna")
       
    def test_two_greeters(self):        
       greeters = botcode.greeter_string(['shauna','sauna'])
       self.assertEqual(greeters, "shauna and sauna")

    def test_three_greeters(self):  
       greeters = botcode.greeter_string(['shauna','sauna','megafauna'])
       self.assertEqual(greeters, "shauna, sauna, and megafauna")


# Runs all the unit-tests
if __name__ == '__main__':
    unittest.main()
