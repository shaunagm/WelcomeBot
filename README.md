# What is this

oh-irc-bot (potential name: Nightlightbot) is a bot for welcoming people into the #openhatch irc channel 
when no one is paying attention.  The goals are to:

1. alert community members when someone knew enters the room and says hello (either by using their nick
in a response, or by sending a private message)
2. helping a person to feel welcome even when there's no one around, and providing more information about
staying in touch

# Deets

## Response conditions

Proposed

1. someone joins; says hi/hey/hello; no one responds for X seconds; bot RESPONDS [YES]
2. someone joins; says nothing for Y seconds; no one responds for X seconds; bot checks list of known nicks:
    - if unknown RESPONDS
    - if known PMs maintainers
3. someone says hi/hey/hello with no nicks in channel after it; no one responds for X seconds; bot RESPONDS ?

## Responses

May 

* Include "maintainers" nicks so they get pinged?
* Suggest waiting til the morning, or emailing.

## Implementation ideas

May want to keep a list of known nicks so channel regulars aren't constantly getting bugged by the bot.

# How to help

Find me (shauna) on the #openhatch IRC.  Alternatively you can fork this project, make changes, and send
them back if you want.  If you need help using github, see [here](https://openhatch.org/wiki/Git_Basics).

I will come back and improve this documentation later.

# Credit

This bot was adapted from code found [here](http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python).

Also [this](http://docs.python.org/2/library/queue.html) has been very helpful.
