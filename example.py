# -*- coding: utf-8 -*-
import srsbot
import string
import time
import re

bot = srsbot.SrsBot()
bot.verbose = 1 #See every line, switch to 0 to turn it off
bot.connect("irc.rizon.net", 6667) #Server, port
connectTime = time.time()

bot.register("ExampleBot", "examplebot", "Example T. Bot") #Nick, username, real name

channel = "#srsbot"
bot.join(channel)

while bot.connected:
	messages = bot.recvMessages() #Wait until messages are recieved and put them into the messages array
	
	for line in messages:
		word=string.split(line)
		
		if(word[1] == "353"):
			bot.privmsg(channel, "EXAMPLEBOT IS IN THE HIZZOUSE") #Send a private message to the channel
		
		if(re.search("hey examplebot", line, re.IGNORECASE)): #use a regular expression to search the message
			bot.privmsg(channel, "hey")
	
	if(time.time() - connectTime >= 120): #connected two minutes ago
		bot.privmsg(channel, "g2g. keep it fresh")
		bot.part(channel)
		bot.disconnect()