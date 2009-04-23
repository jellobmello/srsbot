# -*- coding: utf-8 -*-
'''Copyright 2009, Jello B. Mello

This file is part of SrsBot.

SrsBot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SrsBot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with SrsBot.  If not, see <http://www.gnu.org/licenses/>.'''

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
	
	for line in bot.messages(): #Iterate through received messages
		word=string.split(line)
		
		if(word[1] == "353"):
			bot.privmsg(channel, "EXAMPLEBOT IS IN THE HIZZOUSE") #Send a private message to the channel
		
		if(re.search("hey examplebot", line, re.IGNORECASE)): #use a regular expression to search the message
			bot.privmsg(channel, "hey")
	
	if(time.time() - connectTime >= 120): #connected two minutes ago
		bot.privmsg(channel, "g2g. keep it fresh")
		bot.part(channel)
		bot.disconnect()