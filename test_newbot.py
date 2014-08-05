# Yay tests!

import csv
import unittest
import newbot
import time
import pdb

class TestBotClass(unittest.TestCase):

    def setUp(self):
        self.bot = newbot.Bot()

    def test_csv_source(self):
        self.assertEqual(self.bot.nick_source, 'nicks.csv')

    def test_known_nicks_setup(self):
        bot = newbot.Bot('test_nicks.csv')
        self.assertEqual(bot.known_nicks, [['Alice'], ['Bob']])

    def test_wait_time(self):
        self.assertEqual(self.bot.wait_time, 60)

    def test_custom_wait_time(self):
        bot = newbot.Bot(wait_time=30)
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
        bot = newbot.Bot('test_nicks.csv')
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
        self.bot = newbot.Bot('test_nicks.csv')
        self.NewComer = newbot.NewComer('Nancy', self.bot)

    def test_newcomer_init_nick(self):
        self.assertEqual(self.NewComer.nick, 'Nancy')

    def test_newcomer_init_born(self):
        newComer = newbot.NewComer('Baby', newbot.Bot())
        time.sleep(0.01)
        self.assertAlmostEqual(newComer.born, time.time() - .01, places=2)

    def test_add_newcomer_to_bot(self):
        pass

    def test_newcomer_around_for(self):
        newComer = newbot.NewComer('Shauna', newbot.Bot())
        time.sleep(0.01)
        self.assertAlmostEqual(newComer.around_for(), .01, places=2)

class TestProcessNewcomers(unittest.TestCase):

    def setUp(self):
        self.bot = newbot.Bot('test_nicks.csv', wait_time=.1)
        newbot.NewComer('Harry', self.bot)
        newbot.NewComer('Hermione', self.bot)
        time.sleep(.15)
        newbot.NewComer('Ron', self.bot)

    def test_check_new_newcomers(self):
        newbot.process_newcomers(self.bot, [i for i in self.bot.newcomers if i.around_for() > self.bot.wait_time], welcome=0)
        self.assertEqual(len(self.bot.newcomers), 1)

    def test_check_new_known_nicks(self):
        newbot.process_newcomers(self.bot, [i for i in self.bot.newcomers if i.around_for() > self.bot.wait_time], welcome=0)
        self.assertEqual(self.bot.known_nicks,[['Alice'],['Bob'],['Harry'],['Hermione']])
        
    def test_welcome_nick(self):
        ircsock = newbot.fake_irc_start()
        newbot.process_newcomers(bot=self.bot, newcomerlist=[i for i in self.bot.newcomers if i.around_for() > self.bot.wait_time], ircsock=ircsock, welcome=1)
        self.assertEqual(newbot.ircsock.sent_message, "PRIVMSG #openhatch-bots :Welcome Hermione!  The channel is pretty quiet right now, so I though I'd say hello, and ping some people (like shauna) that you're here.  If no one responds for a while, try emailing us at hello@openhatch.org or just try coming back later.  FYI, you're now on my list of known nicknames, so I won't bother you again.\n")
        
    def tearDown(self):
        with open('test_nicks.csv', 'w') as csv_file:
            csv_file.write('Alice\nBob\n')

class TestParseMessages(unittest.TestCase):

    def test_good_string(self):
        ircmsg, actor = newbot.parse_messages(":vader!darth@darkside.org PRIVMSG #deathstar : I find your lack of faith disturbing")
        self.assertEqual([ircmsg, actor], [':vader!darth@darkside.org PRIVMSG #deathstar : I find your lack of faith disturbing', 'vader'])
    
    def test_bad_string(self):
        ircmsg, actor = newbot.parse_messages("we should probably replace this with a bad string more likely to occur")
        self.assertEqual([ircmsg, actor], [None, None])

class TestMessageResponse(unittest.TestCase):

    def setUp(self):
        self.bot = newbot.Bot('test_nicks.csv')
        newbot.NewComer('Chappe', self.bot)

    def test_newcomer_speaking(self):
        newbot.message_response(self.bot,"~q@r.m.us PRIVMSG #openhatch-bots :hah","Chappe")  # Standard message by newcomer
        nicklist = [i.nick for i in self.bot.newcomers]   # Makes a list of newcomers nicks for easy asserting
        self.assertEqual(nicklist, ['Chappe'])

    def test_oldtimer_speaking(self):
        newbot.message_response(self.bot,"~q@r.m.us PRIVMSG #openhatch-bots :hah","Alice")  # Standard message by oldtimer
        nicklist = [i.nick for i in self.bot.newcomers]   # Makes a list of newcomers nicks for easy asserting
        self.assertEqual(nicklist, [])
        
    def test_join(self):
        newbot.message_response(self.bot,"JOIN #openhatch-bots right now!","Shauna")   # Replace with actual ping message ALSO argh the channel variable might mess things up if folks change it, which they very well might :/  (Also true for tests below.)  I think maybe use the format.() style that is used for wait_change etc
        self.assertEqual(self.bot.newcomers[1].nick,'Shauna')
 
    def test_part(self):
        newbot.message_response(self.bot,"JOIN #openhatch-bots right now!","Shauna")   # Replace with actual ping message ALSO argh the channel variable might mess things up if folks change it, which they very well might :/  (Also true for tests below.)
        self.assertEqual(len(self.bot.newcomers), 2)
        newbot.message_response(self.bot,"PART #openhatch-bots","Shauna")   # Replace with actual ping message ALSO argh the channel variable might mess things up :/
        self.assertEqual(len(self.bot.newcomers), 1)  
        
    def test_hello(self):
        newbot.fake_irc_start()
        newbot.message_response(self.bot,"PRIVMSG sup WelcomeBot2","Shauna")     # The botnick may also be changed.  :(
        self.assertTrue(hasattr(newbot.ircsock, 'sent_message'))  # Fails because sent_message is never actually created
        self.assertIn(newbot.ircsock.sent_message, ["PRIVMSG #openhatch-bots :hello Shauna\n", "PRIVMSG #openhatch-bots :hi Shauna\n", "PRIVMSG #openhatch-bots :hey Shauna\n", "PRIVMSG #openhatch-bots :yo Shauna\n", "PRIVMSG #openhatch-bots :sup Shauna\n"])
        
    def test_help(self):
        newbot.fake_irc_start()
        newbot.message_response(self.bot,"PRIVMSG info WelcomeBot2","Shauna")     # The botnick may also be changed.  :(
        self.assertTrue(hasattr(newbot.ircsock, 'sent_message'))  # Fails because sent_message is never actually created
        self.assertEqual(newbot.ircsock.sent_message, "PRIVMSG #openhatch-bots :I'm a bot!  I'm from here <https://github.com/shaunagm/oh-irc-bot>.  You can change my behavior by submitting a pull request or by talking to shauna.\n")
        
    def test_wait_time_from_admin(self):
        newbot.fake_irc_start()
        newbot.message_response(self.bot,"WelcomeBot2 --wait-time 40","shauna")     # Channel-greeters may also be changed.  :(
        self.assertEqual(newbot.ircsock.sent_message, "PRIVMSG #openhatch-bots :shauna the wait time is changing to 40 seconds.\n")
 
    def test_wait_time_from_non_admin(self):     
        newbot.fake_irc_start()
        newbot.message_response(self.bot,"WelcomeBot2 --wait-time 40","Impostor")     # Channel-greeters may also be changed.  :(  
        self.assertEqual(newbot.ircsock.sent_message, "PRIVMSG #openhatch-bots :Impostor you are not authorized to make that change. Please contact one of the channel greeters, like shauna, for assistance.\n")
        
    def test_pong(self):
        newbot.fake_irc_start()
        newbot.message_response(self.bot,"PING :","Shauna")   # Replace this with actual ping message
        self.assertEqual(newbot.ircsock.sent_message,"PONG :pingis\n")
        
    def test_bad_pong(self):
        newbot.fake_irc_start()
        newbot.message_response(self.bot,"PING!!! :","Shauna")   # Replace this with actual ping message
        self.assertFalse(hasattr(newbot.ircsock, 'sent_message'))  # Fails because sent_message is never actually created

    def tearDown(self):
        with open('test_nicks.csv', 'w') as csv_file:
            csv_file.write('Alice\nBob\n')

class TestGreeterString(unittest.TestCase):     
    
    def setUp(self):
        self.bot = newbot.Bot('test_nicks.csv')
    
    def test_one_greeter(self):     
       greeterstring = newbot.greeter_string("and", ['shauna'])
       self.assertEqual(greeterstring, "shauna")
       
    def test_two_greeters(self):        
       greeters = newbot.greeter_string("and", ['shauna','sauna'])
       self.assertEqual(greeters, "shauna and sauna")

    def test_three_greeters(self):  
       greeters = newbot.greeter_string("and", ['shauna','sauna','megafauna'])
       self.assertEqual(greeters, "shauna, sauna, and megafauna")


# Runs all the unit-tests
if __name__ == '__main__':
    unittest.main()
