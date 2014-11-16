## What is this?

oh-irc-bot (or "WelcomeBot", its IRC nick) is a bot for welcoming people into the #openhatch irc channel
when no one is paying attention.  The goals are to:

1. alert community members when someone new enters the room and says hello (either by using their nick
in a response, or by sending a private message)
2. help a person to feel welcome even when there's no one around, and providing more information about
staying in touch

## Basic Structure

<code>bot.py</code> is the project's main file.  It uses the socket module to communicate and gathers a list of known IRC nicknames, stored in <code>nicks.csv</code>.  Its basic functions include:

1. If someone enters the channel, the bot checks to see if they are a known nick.  If not, it adds them to a list of people to greet.  If no one else has spoken into the channel after a period of time, 60 seconds by default, it greets them.  If someone else (not the new nick) speaks into the channel within the set wait time, or if the nick is known, the bot remains silent.  The bots response text includes the nicks of channel maintainers/frequent contributors so that they are pinged.  Channel maintainers can change the wait time of the bot by using the following command in the irc channel: *Botname* --wait-time *new wait time in seconds*.
2. If someone says hello to the bot, the bot says hello back.
3. If someone asks the bot for information (via key phrases like "help", "faq", etc) the bot explains what it is and links to this repository.

The repository also contains <code>test_bot.py</code>, which is a set of automated tests for the bot.  To learn more about these, see __Testing__ below.  <code>test_nicks.csv</code>, which is the set of nicks used for the automated tests.

There are also some miscellaneous files that you can ignore for now.  We'll clean them up eventually. :)

## Setting up
Currently, the bot is only compatible up to Python 2.7.

To run the bot:

1.  Download the repository.  If you need help using github, see [here](https://openhatch.org/wiki/Git_Basics).
2.  Edit bot.py to change the nickname to something besides "WelcomeBot" and the channel to "openhatch-bots".
2.  Open up a command line and type <code>python bot.py</code>.  
3.  Although all IRC messages should be printed to your command line, for development purposes, it will probably be useful to be on IRC separately using your normal nick.

If you run into setup difficulties, ping shauna on freenode (via the #openhatch channel is preferred) and/or leave an issue in this repository's issue tracker.

In order to keep the bot continuously running, we put it on a server using the following command:

<code>nohup python bot.py &</code>

[Nohup](http://en.wikipedia.org/wiki/Nohup) keeps it from terminating when we close the terminal and <code>&</code> keeps it from printing the IRC messages to the terminal.

## Testing

We use [Python unittest](https://docs.python.org/2/library/unittest.html) to test the bot, and [Coverage](http://nedbatchelder.com/code/coverage/) to look at the test coverage.  

When running tests, use this command:

<code>python -m unittest test_bot</code>

The output should tell you how many tests you ran and if any of them are failures.

When creating tests, you can use the following series of commands to see whether your test is testing the code you want it to test:

<code>
./bin/coverage run test_bot.py
</code>

_Note_: You will likely need to install coverage.  The above command assumes you have installed it to a virtual environment.  If you haven't, the command to use is: <code>coverage run test_bot.py</code>

## How to help

The [issue tracker](https://github.com/shaunagm/oh-irc-bot/issues?state=open) lists improvements we want to make.  I strongly encourage you to contact me and say hello before you get started (I am shauna on the #openhatch IRC).  Please feel free to submit pull requests to address these issues.  If you're not familiar with how to do this using github, see [here](https://openhatch.org/wiki/Git_Basics).  You can also always ask me for help or  clarification.  

## Credit

This bot was adapted from code found [here](http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python).

Also [this](http://docs.python.org/2/library/queue.html) has been very helpful.
