# Import some necessary libraries.
import socket 
import time
import Queue
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

joinchan(channel) # Join the channel using the functions we previously defined

# Creates separate thread for reading messages from the server
def getIRC():
  while True:
    ircmsg = ircsock.recv(2048) # receive data from the server   <-------- this needs to be fixed!  Threading?  Buffer file?
    ircmsg = ircmsg.strip('\n\r') # removing any unnecessary linebreaks.
    q.put(ircmsg)
    print(ircmsg) # Here we print what's coming from the server

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
        print "newcomer object named " + self.nick + " created"

    def changeStatus(self,status):
        self.status = status
        print "status of newcomer object changed to " + str(self.status)

    def aroundFor(self):
#        print "timecheck: " + str(self.nick) + " has been around for " + str(time.time() - self.born)
        return time.time() - self.born


# Functions
def ping(): # Responds to server Pings.
  ircsock.send("PONG :pingis\n")  

def hello(speaker): # This function responds to a user that inputs "Hello Mybot"
  ircsock.send("PRIVMSG "+ channel +" :Hello! "+ speaker + "\n")

def welcome(speaker):
  ircsock.send("PRIVMSG "+ channel +" :Welcome "+ speaker + "!\n")


#### Main function

newList = []

while 1: 

  if q.empty() == 0:
    ircmsg = q.get()
    speaker = ircmsg.split(":")[1].split("!")[0]

    if ircmsg.find(":Hello "+ botnick) != -1: # Response to 'Hello botnick'
      hello(speaker)

    if ircmsg.find("PING :") != -1: # if the server pings us then we've got to respond!
      ping()

    if ircmsg.find("JOIN "+ channel) != -1:  # If someone joins #channel
      newList.append(newcomer(speaker))		# Create a newcomer object and append to list.

  for i in newList:
     if i.aroundFor() > 3 and i.status == 0:
	print welcome(i.nick)
        i.changeStatus(1)
