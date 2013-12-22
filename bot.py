# Import some necessary libraries.
import socket 
import time
import Queue
import random
from threading import Thread

# Some basic variables used to configure the bot        
server = "irc.freenode.net" # Server
channel = "#openscienceframework" # Channel
botnick = "ShaunaBot" # Your bots nick

# Connects to server and joins channel
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This bot is a result of a tutoral covered on http://shellium.org/wiki.\n") # user authentication
ircsock.send("NICK "+ botnick +"\n") # here we actually assign the nick to the bot

def joinchan(chan): # This function is used to join channels.
  ircsock.send("JOIN "+ chan +"\n")

joinchan(channel)

# Creates separate thread for reading messages from the server
def getIRC():
  while True:
    ircmsg = ircsock.recv(2048) # receive data from the server   
    ircmsg = ircmsg.strip('\n\r') # removing any unnecessary linebreaks.
    q.put(ircmsg) # Put in queue for main loop to read
    print(ircmsg) 

q = Queue.LifoQueue()
t = Thread(target=getIRC)
t.daemon = True
t.start()

# Classes
class newcomer(object):  # Newcomer class created when someone joins the room

    def __init__(self, nick):
        self.nick = nick
        self.born = time.time()
	self.status = 0

    def changeStatus(self,status):
        self.status = status	# Right now there's just status 0 (not replied to) and 1 (replied to)

    def aroundFor(self):
        return time.time() - self.born


# Functions
def ping(): # Responds to server Pings.
  ircsock.send("PONG :pingis\n")  

def hello(speaker,greeting): # This function responds to a user that inputs "Hello Mybot"
  ircsock.send("PRIVMSG " + channel +" :" + greeting + " " + speaker + "\n")

def help(speaker): # This function explains what the bot is when queried.
  ircsock.send("PRIVMSG " + channel +" :I'm a bot!  I'm from here: https://github.com/shaunagm/oh-irc-bot. You can change my behavior by submitting a pull request or by talking to shauna. \n")

def welcome(newcomer):  # This welcomes a specific person.
  ircsock.send("PRIVMSG "+ channel +" :Welcome "+ newcomer + "!\n")
  ircsock.send("PRIVMSG "+ channel +" :(pssst shauna there's someone here)\n")


#### Main function

newList = []

while 1: 

  for i in newList:
     if i.aroundFor() > 5 and i.status == 0:
	print welcome(i.nick)
        i.changeStatus(2)

  if q.empty() == 0:
    ircmsg = q.get()
    speaker = ircmsg.split(":")[1].split("!")[0]

    if ircmsg.find("PRIVMSG "+ channel) != -1: # If someone has spoken into the channel
      for i in newList:
        if speaker != i.nick: # Don't turn off response if the person speaking is the person who joined.
          i.changeStatus(1)  # set status to "someone has spoken in channel" for all waiting newcomers

    if ircmsg.find(botnick) != -1 and ircmsg.find("PRIVMSG #") != -1: # If someone talks to (or refers to) the bot
	helloArray = ['Hello','hello','Hi','hi','Hey','hey','Yo','yo ','Sup','sup']
        helpArray = ['Help','help','Info','info','faq','FAQ','explain yourself','EXPLAIN YOURSELF']
        if any(x in ircmsg for x in helloArray):
	  hello(speaker,random.choice(helloArray))
        if any(y in ircmsg for y in helpArray):
          help(speaker)

    if ircmsg.find("PING :") != -1: # if the server pings us then we've got to respond!
      ping()

    if ircmsg.find("JOIN "+ channel) != -1:  # If someone joins #channel
      if speaker != botnick:  # Probably a cleaner way to do this
        newList.append(newcomer(speaker))		# Create a newcomer object and append to list.

