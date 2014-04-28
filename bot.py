#########################################################################
################# Abundant notes are appreciated here! ##################
#########################################################################

# Import some necessary libraries.
import socket 
import time
import csv
import Queue
import random
from threading import Thread
from re import search

# Some basic variables used to configure the bot.
server = "irc.freenode.net" 
channel = "#openhatch"
botnick = 'WelcomeBot'
channel_admins = ('shauna', 'paulproteus', 'marktraceur')
wait_time = 60  # amount of time after joining before bot replies to someone
change_wait = botnick + " --wait-time "


#################### Classes ####################
# Newcomer class that is created when someone joins the room.
class NewComer(object):

        def __init__(self, nick):
            self.nick = nick
            self.born = time.time()
            self.status = 0

        def update_status(self):
            self.status = 1

        def around_for(self):
            return int(time.time() - self.born)


#################### Functions! ####################
# Joins specified channel.
def join_channel(chan):
    ircsock.send("JOIN {} \n".format(chan))


# Reads the messages from the server and adds them to the Queue and prints
# them to the console. This function will be run in a thread, see below.
def msg_handler():
    while True:
        new_msg = ircsock.recv(2048)  # receive data from the server
        new_msg = new_msg.strip('\n\r')  # removing any unnecessary linebreaks
        q.put(new_msg)  # put in queue for main loop to read
        print(new_msg)


# Responds to server Pings.
def pong():
    ircsock.send("PONG :pingis\n")  


# This function responds to a user that inputs "Hello Mybot".
def bot_hello(greeting):
    ircsock.send("PRIVMSG {0} :{1} {2}\n".format(channel, greeting, actor))


# This function explains what the bot is when queried.
def bot_help():
    ircsock.send("PRIVMSG {} :I'm a bot!  I'm from here <https://github"
                 ".com/shaunagm/oh-irc-bot>.  You can change my behavior by "
                 "submitting a pull request or by talking to 'fill in "
                 "the blank'.\n".format(channel))


# This welcomes the "person" passed to it.
def welcome(newcomer):
    ircsock.send("PRIVMSG {0} :Welcome {1}!  The channel is pretty quiet "
                 "right now, so I though I'd say hello, and ping some people "
                 "(like {2}) that you're here.  If no one responds for a "
                 "while, try emailing us at hello@openhatch.org or just try "
                 "coming back later.  FYI, you're now on my list of known "
                 "nicknames, so I won't bother you again."
                 "\n".format(channel, newcomer, channel_admins))


# Adds the current NewComer's nick to nicks.csv and known_nicks.
def add_known_nick(new_known_nick):
    new_known_nick = new_known_nick.replace("_", "")
    known_nicks.append([new_known_nick])
    with open('nicks.csv', 'a') as csvfile:
        nickwriter = csv.writer(csvfile, delimiter=',', quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)
        nickwriter.writerow([new_known_nick])


# "I NEED NOTES!!!!", said the function.
def get_welcome_regex(string_array):
    #make regex case-insenstive
    pattern = r'(?i)'
    for s in string_array:
        pattern += r'(?:[ :]'+s+r'(?:[ \.!\?,\)]|$))|'
    #delete trailing '|'
    pattern = pattern[:-1]
    return pattern


# This function is used to change the wait time from the channel.
# It confirms that the attempt is allowed and then returns the requested value.
# If the attempt is not allowed, a message is sent to help
def wait_time_change():
    for admin in channel_admins:
        if actor == admin:
            finder = search(r'\d\d*', search(r'--wait-time \d\d*', ircmsg)
                            .group())
            ircsock.send("PRIVMSG {0} :{1} the wait time is changing to {2} "
                         "seconds.\n".format(channel, actor, finder.group()))
            return finder.group()
    ircsock.send("PRIVMSG {0} :{1} you are not authorized to make that "
                 "change. Please contact one of the channel admins {2} for "
                 "assistance.\n".format(channel, actor, channel_admins))


#################### Startup ####################
# Creates a socket that will be used to send and receive messages,
# then connects the socket to an IRC server and joins the channel.
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667))  # Here we connect to server using port 6667.
ircsock.send("USER {0} {0} {0} :This is http://openhatch.org/'s greeter bot"
             ".\n".format(botnick))  # bot authentication
ircsock.send("NICK {}\n".format(botnick))  # Assign the nick to the bot.
join_channel(channel)

# Creates a list of known nicks from nicks.csv.
# The list is checked to ensure that people are only greeted once.
# NewComers will be added to the list and the csv.
known_nicks = []
with open('nicks.csv', 'rb') as csv_file:
    csv_file_data = csv.reader(csv_file, delimiter=',', quotechar='|')
    for row in csv_file_data:
        known_nicks.append(row)

# Creates a Queue that will hold the incoming messages.
q = Queue.Queue()
# Creates a separate thread that will listen on the server and add any
# messages to the Queue. The thread is created to run target which equals
# the msg_handler function from above.
t = Thread(target=msg_handler)
t.daemon = True
t.start()

# This is the array of NewComer objects that people who join are added to.
newcomers = []

hello_list = [r'hello', r'hi', r'hey', r'yo', r'sup']
help_list = [r'help', r'info', r'faq', r'explain yourself']
hello_pattern = get_welcome_regex(hello_list)
help_pattern = get_welcome_regex(help_list)


#################### The Workhorse ####################
# This is the main loop that monitors the channel and sends and receives the
# messages, either in the below code or by calling a function. This is the
# brain of this code.
while 1:  # loop forever

    for i in newcomers:
        if i.status == 0 and i.around_for() > wait_time:
            welcome(i.nick)
            i.update_status()
            add_known_nick(i.nick)
            newcomers.remove(i)

    # If the queue is not empty...
    if q.empty() == 0:
        # get the next msg in the queue
        ircmsg = q.get()
        # and get the nick of the msg sender
        actor = ircmsg.split(":")[1].split("!")[0]

        ##### Welcome functions #####
        # If someone has spoken into the channel...
        if ircmsg.find("PRIVMSG " + channel) != -1:
            for i in newcomers:
                if actor != i.nick:  # and is not the new NewComer
                    i.update_status()  # set the status to 1
                    add_known_nick(i.nick)
                    newcomers.remove(i)
                ## Else: Do we want to do something extra if the person who
                # joined the chat says something with no response?

        # If someone joins #channel...
        if ircmsg.find("JOIN " + channel) != -1:
            if actor != botnick:  # and it is not the bot
                if [actor.replace("_", "")] not in known_nicks:
                    if actor not in (i.nick for i in newcomers):
                        newcomers.append(NewComer(actor))

        # If someone parts or quits the #channel...
        if ircmsg.find("PART " + channel) != -1 or ircmsg.find("QUIT") != -1:
            for i in newcomers:  # and that person is on the newlist
                if actor == i.nick:
                    newcomers.remove(i)   # remove them from the list

        ##### Unwelcome functions #####
        # If someone talks to (or refers to) the bot.
        if ircmsg.find(botnick) != -1 and ircmsg.find("PRIVMSG") != -1:
            matchHello = search(hello_pattern, ircmsg)
            matchHelp = search(help_pattern, ircmsg)
            if matchHello:
                bot_hello(random.choice(hello_list))
            if matchHelp:
                bot_help()

        # If someone tries to change the wait time...
        if ircmsg.find(change_wait) != -1:
            wait_time = wait_time_change()  # call this to check and change it

        # If the server pings us then we've got to respond!
        if ircmsg.find("PING :") != -1:
            pong()
