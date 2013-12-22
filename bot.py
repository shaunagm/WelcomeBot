# Import some necessary libraries.
import socket 
import time

# Some basic variables used to configure the bot        
server = "irc.freenode.net" # Server
channel = "#openscienceframework" # Channel
botnick = "ShaunaBot" # Your bots nick

# Connecting to the channel, defining basic functions

def ping(): # Responds to server Pings.
  ircsock.send("PONG :pingis\n")  

def joinchan(chan): # This function is used to join channels.
  ircsock.send("JOIN "+ chan +"\n")

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667)) # Here we connect to the server using the port 6667
ircsock.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :This bot is a result of a tutoral covered on http://shellium.org/wiki.\n") # user authentication
ircsock.send("NICK "+ botnick +"\n") # here we actually assign the nick to the bot

joinchan(channel) # Join the channel using the functions we previously defined

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
        print "timecheck: " + str(self.nick) + " has been around for " + str(time.time() - self.born)
        return time.time() - self.born

## bot-specific functions

def hello(speaker): # This function responds to a user that inputs "Hello Mybot"
  ircsock.send("PRIVMSG "+ channel +" :Hello! "+ speaker + "\n")

def welcome(speaker):
  ircsock.send("PRIVMSG "+ channel +" :Welcome "+ speaker + "!\n")

newList = []

while 1: 

  ircmsg = ircsock.recv(2048) # receive data from the server   <-------- this needs to be fixed!  Threading?  Buffer file?
  ircmsg = ircmsg.strip('\n\r') # removing any unnecessary linebreaks.
  print(ircmsg) # Here we print what's coming from the server

  speaker = ircmsg.split(":")[1].split("!")[0]

  if ircmsg.find(":Hello "+ botnick) != -1: # Response to 'Hello botnick'
    hello(speaker)

  if ircmsg.find("PING :") != -1: # if the server pings us then we've got to respond!
    ping()

  if ircmsg.find("JOIN "+ channel) != -1:  # If someone joins #channel
    newList.append(newcomer(speaker))		# Create a newcomer object and append to list.

  print newList

  for i in newList:
     print i.aroundFor()
     print i.status
     if i.aroundFor() > 3 and i.status == 0:
	print welcome(i.nick)
        i.changeStatus(1)
