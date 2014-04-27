#########################################################################
############## The abundant notes are there for the newbs. ##############
#########################################################################

# Import some necessary libraries.
import socket 
import time
import csv
import string
import Queue
import random
from threading import Thread
from re import search

# Some basic variables used to configure the bot.
server = "irc.freenode.net" 
channel = "#openhatch" 
botnick = "WelcomeBot"
channel_admins = "shauna, paulproteus, and marktraceur"
waitTime = 60  # amount of time after joining before bot replies to someone


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


# Creates separate thread for reading messages from the server.
def msg_handler():
    while True:
        ircmsg = ircsock.recv(2048)  # receive data from the server
        ircmsg = ircmsg.strip('\n\r')  # removing any unnecessary linebreaks
        q.put(ircmsg)  # put in queue for main loop to read
        print(ircmsg)


# Responds to server Pings.
def pong():
    ircsock.send("PONG :pingis\n")  


# This function responds to a user that inputs "Hello Mybot".
def hello(actor, greeting, chan=channel):
    ircsock.send("PRIVMSG {0} :{1} {2}\n".format(chan, greeting, actor))


# This function explains what the bot is when queried.
def help(actor, chan=channel):
    ircsock.send("PRIVMSG {} :I'm a bot!  I'm from here <https://github"
                 ".com/shaunagm/oh-irc-bot>.  You can change my behavior by "
                 "submitting a pull request or by talking to shauna.\n"
                 .format(chan))


# This welcomes the "person" passed to it.
def welcome(newcomer):
    ircsock.send("PRIVMSG {0} :Welcome {1}!  The channel is pretty quiet "
                 "right now, so I though I'd say hello, and ping some people "
                 "(like {2}) that you're here.  If no one responds for a "
                 "while, try emailing us at hello@openhatch.org or just try "
                 "coming back later.  FYI, you're now on my list of known "
                 "nicknames, so I won't bother you "
                 "again.\n".format(channel, newcomer, channel_admins))


# On startup, makes array of nicks from nicks.csv.
# New info will be written to the array AND the txt file.
def make_nick_array():
    nick_array = []
    with open('nicks.csv', 'rb') as csvfile:
        nicks_data = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in nicks_data:
            nick_array.append(row)
    return nick_array


# Adds NewComer to list of known nicks.
def add_person(person):
    person = person.replace("_", "")
    nickArray.append([person])
    with open('nicks.csv', 'a') as csvfile:
        nickwriter = csv.writer(csvfile, delimiter=',', quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)
        nickwriter.writerow([person])


def get_welcome_regex(string_array):
    #make regex case-insenstive
    pattern = r'(?i)'
    for s in string_array:
        pattern += r'(?:[ :]'+s+r'(?:[ \.!\?,\)]|$))|'
    #delete trailing '|'
    pattern = pattern[:-1]
    return pattern


#################### Startup ####################
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667))  # Here we connect to server using port 6667.
ircsock.send("USER {0} {0} {0} :This is http://openhatch.org/'s greeter bot"
             ".\n".format(botnick))  # bot authentication
ircsock.send("NICK {}\n".format(botnick))  # Assign the nick to the bot.
join_channel(channel)

# Starts a separate thread to get messages from server
q = Queue.LifoQueue()
# Calls getIRC(), defined above, in a separate thread.
t = Thread(target=msg_handler)
t.daemon = True
t.start()

nickArray = make_nick_array()

# This is the array of NewComer objects that people who join are added to.
newList = []
hello_array = [r'hello', r'hi', r'hey', r'yo', r'sup']
help_array = [r'help', r'info', r'faq', r'explain yourself']
hello_pattern = get_welcome_regex(hello_array)
help_pattern = get_welcome_regex(help_array)

# Loop forever
while 1:

    for i in newList:
        if i.status == 0 and i.around_for() > waitTime:
            welcome(i.nick)
            i.update_status()
            add_person(i.nick)
            newList.remove(i)

    if q.empty() == 0:
        ircmsg = q.get()
        actor = ircmsg.split(":")[1].split("!")[0]

        ##### Welcome functions #####
        # If someone has spoken into the channel...
        if ircmsg.find("PRIVMSG " + channel) != -1:
            for i in newList:
                if actor != i.nick:  # and is not the new NewComer
                    i.update_status()  # set the status to 1
                    add_person(i.nick)
                    newList.remove(i)
                ## Else: Do we want to do something extra if the person who
                # joined the chat says something with no response?

        # If someone joins #channel...
        if ircmsg.find("JOIN " + channel) != -1:
            if actor != botnick:  # and it is not the bot
                if [actor.replace("_", "")] not in nickArray:
                    if actor not in (i.nick for i in newList):
                        newList.append(NewComer(actor))

        # If someone parts or quits the #channel...
        if ircmsg.find("PART " + channel) != -1 or ircmsg.find("QUIT") != -1:
            for i in newList:  # and that person is on the newlist
                if actor == i.nick:
                    newList.remove(i)   # remove them from the list

        ##### Unwelcome functions #####
        # If someone talks to (or refers to) the bot.
        if ircmsg.find(botnick) != -1 and ircmsg.find("PRIVMSG") != -1:
            chan = channel
            matchHello = search(hello_pattern, ircmsg)
            matchHelp = search(help_pattern, ircmsg)
            if ircmsg.find("PRIVMSG " + botnick) != -1:
                chan = actor
            if matchHello:
                hello(actor, random.choice(hello_array), chan)
            if matchHelp:
                help(actor, chan)

        # If the server pings us then we've got to respond!
        if ircmsg.find("PING :") != -1:
            pong()
