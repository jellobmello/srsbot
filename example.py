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
import time
import re

bot = srsbot.SrsBot()
bot.verbose = 1 #See every line, switch to 0 to turn it off
bot.connect("irc.rizon.net", 6667) #Server, port
connectTime = time.time()

nickname="ExampleBot"
bot.register(nickname, "examplebot", "Example T. Bot") #Nick, username, real name

channel = "#srsbot"
bot.join(channel)

while bot.connected:
	
	for line in bot.rawMessages(): #Iterate through received messages
		word=line.split()
		
		if(re.search("^:"+nickname+"!", line) and word[1]=="JOIN"): #Use a regular expression to see if you've joined the channel
			bot.privmsg(channel, "EXAMPLEBOT IS IN THE HIZZOUSE") #Send a private message to the channel
		
		if(re.search("hey examplebot", line, re.IGNORECASE)):
			bot.privmsg(channel, "hey")
		
		if(re.search("what it do, my dawg\?", line, re.IGNORECASE)):
			bot.privmsg(channel, "nothin much, man")
			bot.privmsg(channel, "nothin much")
		
		if(re.search("cool beans", line, re.IGNORECASE)):
			bot.privmsg(channel, "so cool they fresh, nawmeen?")
		
	if(time.time() - connectTime >= 30): #Disconnect after 30 seconds
		bot.privmsg(channel, "g2g. keep it fresh")
		bot.part(channel)
		bot.disconnect()
