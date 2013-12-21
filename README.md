# What is this

oh-irc-bot (potential name: Nightlightbot) is a bot for welcoming people into the #openhatch irc channel 
when no one is paying attention.  The goals are to:

1) alert community members when someone knew enters the room and says hello (either by using their nick
in a response, or by sending a private message)
2) helping a person to feel welcome even when there's no one around, and providing more information about
staying in touch

# Deets

## Response conditions

Proposed

1) someone joins, says hi/hey/hello immediately, and no one responds for 60 seconds
2) someone says hi/hey/hello with no nicks after it, and no one responds for 60 seconds
3) someone joins, says nothing, and no one responds for a while but they're still there?

## Responses

May 

Include "maintainers" nicks so they get pinged?
Suggest waiting til the morning, or emailing.

## Implementation ideas

Keep last line said in chat (remember that ircmsg will prob include joins and parts and nick changes.

# How to help

Find me (shauna) on the #openhatch IRC.  Alternatively you can fork this project, make changes, and send
them back if you want.  If you need help using github, see [here](https://openhatch.org/wiki/Git_Basics).

I will come back and improve this documentation later.

# Credit

This bot was adapted from code found here: http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python
