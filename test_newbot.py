# Yay tests!

import unittest
import newbot
import time

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
        self.assertEqual(bot.known_nicks, [['Alice'], ['Bob'], ['Roger']])

    def tearDown(self):
        with open('test_nicks.csv', 'w') as csv_file:
            csv_file.write('Alice\nBob')

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

#
# Not sure how to test irc_start, thread_start or msg_handler yet.
#

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

    ## Should be a test of the welcome=1/welcome=0 functionality here, but not sure how to do that yet since welcome() calls ircsock.

    def tearDown(self):
        with open('test_nicks.csv', 'w') as csv_file:
            csv_file.write('Alice\nBob')

#
# Not sure how to test check_messages.
#

class TestMessageResponse(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

class TestProcessNewcomers(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
