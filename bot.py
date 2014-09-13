# Welcome to WelcomeBot.  Find source, documentation, etc here: https://github.com/shaunagm/WelcomeBot/  Licensed https://creativecommons.org/licenses/by-sa/2.0/

# Import some necessary libraries.
import socket, sys, time, csv, Queue, random, re, pdb, select
from threading import Thread

# Some basic variables used to configure the bot.
server = "irc.freenode.net"
channel = "#openhatch-bots"
botnick = "WelcomeBot2"
channel_greeters = ['shauna'] #'paulproteus', 'marktraceur']
hello_list = [r'hello', r'hi', r'hey', r'yo', r'sup'] 
help_list = [r'help', r'info', r'faq', r'explain yourself']


#########################
### Class Definitions ###
#########################

# Defines a bot
class Bot(object):

    def __init__(self, nick_source='nicks.csv', wait_time=60):
        self.nick_source = nick_source
        self.wait_time = wait_time
        self.known_nicks = []
        with open(self.nick_source, 'rb') as csv_file:
            csv_file_data = csv.reader(csv_file, delimiter=',', quotechar='|')
            for row in csv_file_data:
                self.known_nicks.append(row)
        self.newcomers = []
        self.hello_regex = re.compile(get_regex(hello_list), re.I)  # Regexed version of hello list
        self.help_regex = re.compile(get_regex(help_list), re.I)  # Regexed version of help list

    # Adds the current newcomer's nick to nicks.csv and known_nicks.
    def add_known_nick(self,new_known_nick):
        new_known_nick = new_known_nick.replace("_", "")
        self.known_nicks.append([new_known_nick])
        with open(self.nick_source, 'a') as csvfile:
            nickwriter = csv.writer(csvfile, delimiter=',', quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)
            nickwriter.writerow([new_known_nick])

# Defines a newcomer object    
class NewComer(object):

    def __init__(self, nick, bot):
        self.nick = nick
        self.born = time.time()
        bot.newcomers.append(self)

    def around_for(self):
        return time.time() - self.born


#########################
### Startup Functions ### 
#########################

# Creates a socket that will be used to send and receive messages,
# then connects the socket to an IRC server and joins the channel.
def irc_start(): # pragma: no cover  (this excludes this function from testing)
    ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ircsock.connect((server, 6667))  # Here we connect to server using port 6667.
    return ircsock
    
def join_irc(ircsock):
    ircsock.send("USER {0} {0} {0} :This is http://openhatch.org/'s greeter bot"
             ".\n".format(botnick))  # bot authentication
    ircsock.send("NICK {}\n".format(botnick))  # Assign the nick to the bot.
    ircsock.send("JOIN {} \n".format(channel)) # Joins channel

# Reads the messages from the server and adds them to the Queue and prints
# them to the console. This function will be run in a thread, see below.
def msg_handler(ircsock):  # pragma: no cover  (this excludes this function from testing)
    new_msg = ircsock.recv(2048)  # receive data from the server
    new_msg = new_msg.strip('\n\r')  # removing any unnecessary linebreaks
    print(new_msg) #### Potentially make this a log instead?
    return new_msg

# Called by bot on startup.  Builds a regex that matches one of the options + (space) botnick.
def get_regex(options):
    pattern = "("
    for s in options:
        pattern += s
        pattern += "|"
    pattern = pattern[:-1]
    pattern += ").({})".format(botnick)
    return pattern


#########################
### General Functions ###
#########################

# Welcomes the "person" passed to it.
def welcome_nick(newcomer, ircsock):
    ircsock.send("PRIVMSG {0} :Welcome {1}!  The channel is pretty quiet "
                 "right now, so I thought I'd say hello, and ping some people "
                 "(like {2}) that you're here.  If no one responds for a "
                 "while, try emailing us at hello@openhatch.org or just try "
                 "coming back later.  FYI, you're now on my list of known "
                 "nicknames, so I won't bother you again."
                 "\n".format(channel, newcomer, greeter_string("and", channel_greeters)))

# Checks and manages the status of newcomers.
def process_newcomers(bot, newcomerlist, ircsock, welcome=1):
    for person in newcomerlist:
        if welcome == 1:
            welcome_nick(person.nick, ircsock)
        bot.add_known_nick(person.nick)
        bot.newcomers.remove(person) 

# Checks for messages.
def parse_messages(ircmsg):
    try:
        actor = ircmsg.split(":")[1].split("!")[0] # and get the nick of the msg sender
        return ircmsg, actor
    except:
        return None, None

# Parses messages and responds to them appropriately.
def message_response(bot, ircmsg, actor, ircsock):

    # if someone other than a newcomer speaks into the channel
    if ircmsg.find("PRIVMSG " + channel) != -1 and actor not in [i.nick for i in bot.newcomers]:
        process_newcomers(bot,bot.newcomers, ircsock, welcome=0)   # Process/check newcomers without welcoming them

    # if someone (other than the bot) joins the channel
    if ircmsg.find("JOIN " + channel) != -1 and actor != botnick:
        if actor.replace("_", "") not in bot.known_nicks and (i.nick for i in bot.newcomers):  # And they're new
            NewComer(actor, bot)

    # If someone parts or quits the #channel...
    if ircmsg.find("PART " + channel) != -1 or ircmsg.find("QUIT") != -1:
        for i in bot.newcomers:  # and that person is on the newlist
            if actor == i.nick:
                bot.newcomers.remove(i)   # remove them from the list

    # If someone talks to (or refers to) the bot.
    if botnick.lower() and "PRIVMSG".lower() in ircmsg.lower():
        if bot.hello_regex.search(ircmsg):
            bot_hello(random.choice(hello_list), actor, ircsock)
        if bot.help_regex.search(ircmsg):
            bot_help(ircsock)

    # If someone tries to change the wait time...
    if ircmsg.find(botnick + " --wait-time ") != -1:
        bot.wait_time = wait_time_change(actor, ircmsg, ircsock)  # call this to check and change it

    # If the server pings us then we've got to respond!
    if ircmsg.find("PING :") != -1:
        pong(ircsock)


#############################################################
### Bot Response Functions (called by message_response()) ###
#############################################################

# Responds to a user that inputs "Hello Mybot".
def bot_hello(greeting, actor, ircsock):
    ircsock.send("PRIVMSG {0} :{1} {2}\n".format(channel, greeting, actor))

# Explains what the bot is when queried.
def bot_help(ircsock):
    ircsock.send("PRIVMSG {} :I'm a bot!  I'm from here <https://github"
                 ".com/shaunagm/oh-irc-bot>.  You can change my behavior by "
                 "submitting a pull request or by talking to shauna"
                 ".\n".format(channel))

# Returns a grammatically correct string of the channel_greeters.
def greeter_string(conjunction, greeters):
    greeterstring = ""
    if len(greeters) > 2:
        for name in greeters[:-1]:
            greeterstring += "{}, ".format(name)
        greeterstring += "{0} {1}".format(conjunction, greeters[-1])
    elif len(greeters) == 2:
        greeterstring = "{0} {1} {2}".format(greeters[0], conjunction,
                                        greeters[1])
    else:
        greeterstring = greeters[0]
    return greeterstring

# Changes the wait time from the channel.
def wait_time_change(actor, ircmsg, ircsock):
    for admin in channel_greeters:
        if actor == admin:
            finder = re.search(r'\d\d*', re.search(r'--wait-time \d\d*', ircmsg)
                            .group())
            ircsock.send("PRIVMSG {0} :{1} the wait time is changing to {2} "
                         "seconds.\n".format(channel, actor, finder.group()))
            return int(finder.group())
    ircsock.send("PRIVMSG {0} :{1} you are not authorized to make that "
                 "change. Please contact one of the channel greeters, like {2}, for "
                 "assistance.\n".format(channel, actor, greeter_string("or", channel_greeters)))

# Responds to server Pings.
def pong(ircsock):
    ircsock.send("PONG :pingis\n") 


##########################
### The main function. ###
##########################

def main():
    ircsock = irc_start() 
    join_irc(ircsock)
    WelcomeBot = Bot()
    while 1:  # Loop forever
        ready_to_read, b, c = select.select([ircsock],[],[], 1)  # ignore b&c, doesn't allow keywords
        if ready_to_read:
            ircmsg = msg_handler(ircsock)
            process_newcomers(WelcomeBot, [i for i in WelcomeBot.newcomers if i.around_for() > WelcomeBot.wait_time],ircsock)
            ircmsg, actor = parse_messages(ircmsg)  # parse the next msg in the queue
            if ircmsg is not None: # If we were able to parse it
                message_response(WelcomeBot, ircmsg, actor, ircsock)  # Respond to the parsed message

if __name__ == "__main__": # This line tells the interpreter to only execute main() if the program is being run, not imported.
    sys.exit(main())

