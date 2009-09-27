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
import sys
import socket
import string
import time
import re

class message:
	'''A message.
	This class exposes the following properties:
		message.body
		message.sender
		message.senderHost
		message.recipient
		message.type
		message.raw
	'''
	
	def __init__(self, body="", sender="", senderHost="", recipient="", type="", raw=""):
		self.body = body
		self.sender = sender
		self.senderHost = senderHost
		self.recipient = recipient
		self.type = type
		self.raw = raw
	
	def __str__(self):
		return self.raw

class SrsBot:
	def __init__(self):
		self.readBuffer=""
		self.tempMessages=[]
		self.messageList=[]
		self.formattedMessages=[]
		self.channels=[]
		self.joinQueue=[]
		self.connected=0
		self.registered=0
		self.verbose=0
	
	def connect(self, server, port, timeout=240, reconnect=0):
		self.server = server
		self.port = port
		self.timeout = timeout
		
		self.sock=socket.socket()
		self.sock.settimeout(timeout) #timeout after four minutes
		
		self.printVerbose("Connecting...")
		try:
			self.sock.connect((self.server, self.port))
		except socket.gaierror:
			if(reconnect==0): #Check to see if this is an attempt by reconnect() so we don't end up recursing
				self.reconnect()
		except socket.herror:
			if(reconnect==0):
				self.reconnect()
		except socket.error:
			if(reconnect==0):
				self.reconnect()
		except socket.timeout:
			self.printVerbose("Connection failed. Timed out.")
			if(reconnect==0):
				self.reconnect()
		else:
			self.connected = 1
			self.printVerbose("Connected.")

	def disconnect(self, quitMessage="SrsBot RC 1"):
		self.printVerbose("Disconnecting.")
		self.message("QUIT :%s \r\n" % quitMessage)
		self.sock.close()
		self.connected = 0
	
	def reconnect(self, maxattempts=100, interval=10):
		self.sock.close()
		self.printVerbose("Reconnecting.")
		attempts = 1
		connectionAttemptTime = 0
		while (attempts < maxattempts):
			if(time.time() - connectionAttemptTime > interval): #Don't wanna blow through all the reconnects in one go
				self.printVerbose("(%s of %s)" % (attempts, maxattempts))
				self.connect(self.server, self.port, reconnect=1)
				connectionAttemptTime = time.time()
				attempts = attempts+1
			if(self.connected == 1):
				if (self.registered):
					self.register(self.nickname, self.username, self.realname)
				if (self.channels):
					for line in self.channels:
						self.message("JOIN %s" % line)
				break
	
	def register(self, nickname, username, realname): #Registers with the server
		self.nickname = nickname
		self.username = username
		self.realname = realname
		
		self.printVerbose("Logging in.")
		self.message("NICK %s" % self.nickname)
		self.message("USER %s %s %s :%s" % (self.username, socket.gethostname(), self.server, self.realname))
	
	def nick(self, nickname): #Changes nickname
		self.nickname = nickname
		
		self.printVerbose("Changing nickname to %s." % nickname)
		self.message("NICK %s" % self.nickname)
	
	def join(self, channel):
		self.printVerbose("Joining %s" % channel)
		self.joinQueue.append(channel)
	
	def part(self, channel):
		self.printVerbose("Leaving %s" % channel)
		self.message("PART %s" % channel)
		self.channels.remove(channel)
	
	def messages(self): #High-level method that returns a list of message objects
		self.formattedMessages=[] #Clean it up so the messages from last time aren't still there
		
		for rawMessage in self.rawMessages():
			try:
				body=rawMessage.split(":", 2)[2]
			except IndexError:
				body="" #Some message
			
			senderHost=rawMessage.split()[1]
			sender=rawMessage.split(":")[1].split("!")[0]
			msgtype=rawMessage.split()[1]
			
			if(msgtype=="PRIVMSG"):
				recipient=rawMessage.split()[2]
			else:
				recipient=""
			
			self.formattedMessages.append(message(body=body, sender=sender, senderHost=senderHost, recipient=recipient, type=msgtype, raw=message))
		
		return self.formattedMessages
	
	def rawMessages(self): #Waits until messages are recieved then returns a list of messages
		try:
			self.readBuffer=self.readBuffer+self.sock.recv(1024) #Get messages from the socket
		except socket.timeout:
			self.printVerbose("Timed out (%s)." % self.timeout)
			self.connected = 0
			self.reconnect()
			return self.messageList
		except socket.error:
			self.connected = 0
			self.reconnect()
			return self.messageList
		
		tempMessages=self.readBuffer.split("\r\n") #Create a list of messages

		#If all messages are completed with \r\n, this removes the blank item. If the last message is incomplete, this moves back it to readBuffer to be completed on the next socket.recv(). tempMessages is necessary for self.messageList to always contain complete messages.
		self.readBuffer=tempMessages.pop()
		
		self.messageList=tempMessages
		
		for line in self.messageList:
			self.printVerbose(self.timestamp()+" |<- "+line)
			
			message=string.split(line, ":")
			word=string.split(line)
			
			if(word[1]=="001"):
				self.registered=1
			
			if(self.registered):
				for channel in self.joinQueue: #join all the channels in the join queue
					self.message("JOIN "+channel)
					self.channels.append(channel)
					self.joinQueue.remove(channel)
			
			if(word[1]=="433"):
				self.nick(self.nickname+"_")
				
			if(word[0]=="PING"):
				self.message("PONG "+word[1])
		
		return self.messageList
	
	def message(self, message): #Sends a raw message to the server terminated with a newline
		try:
			bytesSent = self.sock.send(message+"\r\n") #send message over the socket
		except socket.timeout:
			self.printVerbose("Timed out (%s)." % self.timeout)
			self.connected = 0
			self.reconnect()
		except socket.error:
			self.connected = 0
			self.reconnect()
			return self.messageList
		else:
			self.printVerbose(self.timestamp()+" ->| "+message)
			return bytesSent
	
	def privmsg(self,recipient, message): #Sends a PRIVMSG
		self.message("PRIVMSG %s :%s" % (recipient, message))
	
	def printVerbose(self, message): #Prints a message if the self.verbose variable has been turned on
		if self.verbose==1: print message
	
	def timestamp(self):
		now = time.localtime(time.time())
		year, month, day, hour, minute, second, weekday, yearday, daylight = now
		timestamp = "%02d:%02d:%02d" % (hour, minute, second)
		return timestamp
