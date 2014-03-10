# Import some necessary libraries.
import socket 
import time
import csv
import string
import Queue
import random
import re
import itertools
from threading import Thread

# Some basic variables used to configure the bot        
server = "irc.freenode.net" 
channel = "#openhatch" 
botnick = "WelcomeBot" 
waitTime = 60        # Amount of time after joining before bot replies to someone

# Classes
class newcomer(object):  # Newcomer class created when someone joins the room

        def __init__(self, nick):
            self.nick = nick
            self.born = time.time()
            self.status = 0

        def updateStatus(self):
            self.status = 1

        def aroundFor(self):
            return int(time.time() - self.born)

# Functions!
def joinchan(chan): 	# Joins channels
    ircsock.send("JOIN " + chan + "\n")

def getIRC():           # Creates separate thread for reading messages from the server
    while True:
        ircmsg = ircsock.recv(2048) # receive data from the server   
        ircmsg = ircmsg.strip('\n\r') # removing any unnecessary linebreaks.
        q.put(ircmsg) # Put in queue for main loop to read
        print(ircmsg) 

def ping(): # Responds to server Pings.
    ircsock.send("PONG :pingis\n")  

def hello(actor, greeting, chan=channel): # This function responds to a user that inputs "Hello Mybot"
    ircsock.send("PRIVMSG " + chan + " :" + greeting + " " + actor + "\n")

def help(actor, chan=channel): # This function explains what the bot is when queried.
    ircsock.send("PRIVMSG " + chan + " :I'm a bot!  I'm from here: https://github.com/shaunagm/oh-irc-bot. You can change my behavior by submitting a pull request or by talking to shauna. \n")

def welcome(newcomer):  # This welcomes a specific person.
    ircsock.send("PRIVMSG " + channel + " :Welcome " + newcomer + "!  The channel's pretty quiet right now, so I thought I'd say hello, and ping some people (like shauna, paulproteus, marktraceur) that you're here.  If no one responds for a while, try emailing us at hello@openhatch.org or just coming back later.  FYI, you're now on my list of known nicknames, so I won't bother you again.\n")

def makeNickArray():  # On startup, makes array of nicks from Nicks.txt.  New info will be written to both array and txt file.
    nickArray = []
    with open('nicks.csv', 'rb') as csvfile:
        nicksData = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in nicksData:
             nickArray.append(row)
    return nickArray

def addPerson(person):  # Adds newcomer to list of known nicks
    person = person.replace("_","")
    nickArray.append([person])
    with open('nicks.csv', 'a') as csvfile:
        nickwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        nickwriter.writerow([person])

# Startup
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send("USER " + botnick + " " + botnick + " " + botnick + " :This is http://openhatch.org/'s greeter bot.\n") # user authentication
ircsock.send("NICK " + botnick + "\n") # here we actually assign the nick to the bot
joinchan(channel)

# Starts a separate thread to get messages from server
q = Queue.LifoQueue()
t = Thread(target=getIRC)   # calls getIRC() (defined above) in a separate thread
t.daemon = True
t.start()

nickArray = makeNickArray()

newList = []  # This is the array of newcomer objects that people who join the room are added to.
helloArray = ['hello','hi','hey','yo ','sup']
helpArray = ['help','info','faq','explain yourself']

while 1:  # Loop forever

    for i in newList:
        if i.status == 0 and i.aroundFor() > waitTime:
            welcome(i.nick)
            i.updateStatus()
            addPerson(i.nick)
            newList.remove(i)

    if q.empty() == 0:
        ircmsg = q.get()
        actor = ircmsg.split(":")[1].split("!")[0]

        # Welcome functions
        if ircmsg.find("PRIVMSG " + channel) != -1: # If someone has spoken into the channel
            for i in newList:
                if actor != i.nick: # Don't turn off response if the person speaking is the person who joined.
                    i.updateStatus()	# Sets status to 1
                    addPerson(i.nick)
                    newList.remove(i)
                ## Else: Do we want to do something extra if the person who joined the chat says something with no response?

        if ircmsg.find("JOIN " + channel) != -1:  # If someone joins #channel
            if actor != botnick:  # Remove the case where the bot gets a message that the bot has joined.
                if [actor.replace("_","")] not in nickArray:
                    if actor not in (i.nick for i in newList):
                        newList.append(newcomer(actor))

        if ircmsg.find("PART " + channel) != -1 or ircmsg.find("QUIT") != -1:  # If someone parts or quits the #channel
            for i in newList:  # And that person is on the newlist (has entered channel within last 60 seconds)
                if actor == i.nick:
                    newList.remove(i)   # Remove them from the list


        # Unwelcome functions
        # Reply if someone addresses the bot in a message

        # extract only message content (exclude prefix containing meta data)
        m = re.match(":[^:]+PRIVMSG[^:]+:(.*)", ircmsg)
        try: # tokenize message into words
            ircmsg_clean = m.group(1)
            ircmsg_words = re.split("[\s\.,;!?]+", ircmsg_clean)
        except AttributeError:  # message couldn't be extracted
            ircmsg_words = None

        # test if message could be extracted and contains name of bot and any of the key words (hello or help arrays)
        if ircmsg_words and botnick in ircmsg_words: # if a message contains bot's name
            chan = channel
            
            ircmsg_words = map(lambda x: x.lower(), ircmsg_words) # lowercase message
            ircmsg_words = map(lambda word: ''.join(letter[0] for letter in itertools.groupby(word)), ircmsg_words) # collapse series of consecutive equal letters into one (e.g. "heeelp" -> "help")
            ircmsg_words = ['hello' if word == 'helo' else word for word in ircmsg_words] # fix 'hello' word if it was affected by collapsing above
            
            if any(x in ircmsg_words for x in helloArray): # if message contains a "hello" word
                hello(actor,random.choice(helloArray), chan)
            if any(y in ircmsg_words for y in helpArray): # if message contains a "help" word
                help(actor, chan)

        if ircmsg.find("PING :") != -1: # if the server pings us then we've got to respond!
            ping()

