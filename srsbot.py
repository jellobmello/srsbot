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

class SrsBot:
	readBuffer=""
	tempMessages=[]
	messages=[]
	channels=[]
	notifications=[]
	connected=0
	registered=0
	verbose=0
	
	def connect(self, server, port, timeout=240, reconnect=0):
		self.server = server
		self.port = port
		self.timeout = timeout
		
		self.socket=socket.socket()
		self.socket.settimeout(timeout) #timeout after four minutes
		
		print "Connecting...",
		try:
			self.socket.connect((self.server, self.port))
		except socket.gaierror as error:
			print "Connection failed. %s." % error
			if(reconnect==0): #Check to see if this is an attempt by reconnect() so we don't end up recursing
				self.reconnect()
		except socket.herror as error:
			print "Connection failed. %s." % error
			if(reconnect==0):
				self.reconnect()
		except socket.error as error:
			print "Connection failed. %s." % error
			if(reconnect==0):
				self.reconnect()
		except socket.timeout:
			print "Connection failed. Timed out."
			if(reconnect==0):
				self.reconnect()
		else:
			self.connected = 1
			print "Connected."

	def disconnect(self, quitMessage="SrsBot Beta 7"):
		print "Disconnecting."
		self.sendMessage("QUIT :%s \r\n" % quitMessage)
		self.socket.close()
		self.connected = 0
	
	def reconnect(self, maxattempts=100, interval=10):
		self.socket.close()
		print "Reconnecting."
		attempts = 1
		connectionAttemptTime = 0
		while (attempts < maxattempts):
			if(time.time() - connectionAttemptTime > interval): #Don't wanna blow through all the reconnects in one go
				print "(%s of %s)" % (attempts, maxattempts)
				self.connect(self.server, self.port, reconnect=1)
				connectionAttemptTime = time.time()
				attempts = attempts+1
			if(self.connected == 1):
				if (self.registered):
					self.register(self.nickname, self.username, self.realname)
				if (self.channels):
					for line in self.channels:
						self.sendMessage("JOIN %s" % line)
				break
	
	def register(self, nickname, username, realname): #Registers with the server
		self.nickname = nickname
		self.username = username
		self.realname = realname
		self.registered = 1
		
		print "Logging in."
		self.sendMessage("NICK %s" % self.nickname)
		self.sendMessage("USER %s %s %s :%s" % (self.username, "srsbot", self.server, self.realname))
	
	def nick(self, nickname): #Changes nickname
		self.nickname = nickname
		
		print "Changing nickname to %s." % nickname
		self.sendMessage("NICK %s" % self.nickname)
	
	def join(self, channel):
		print "Joining %s" % channel
		self.sendMessage("JOIN %s" % channel)
		self.channels.append(channel)
	
	def part(self, channel):
		print "Leaving %s" % channel
		self.sendMessage("PART %s" % channel)
		self.channels.remove(channel)
	
	def recvMessages(self): #Waits until messages are recieved and get an array of messages
		try:
			self.readBuffer=self.readBuffer+self.socket.recv(1024) #get messages from the socket
		except socket.timeout as error:
			print "Timed out (%s)." % self.timeout
			self.connected = 0
			self.reconnect()
			return self.messages
		except socket.error as error:
			print str(error)
			self.connected = 0
			self.reconnect()
			return self.messages
		
		temp=string.split(self.readBuffer, "\r\n") #create an array of messages
		self.readBuffer=temp.pop() #If all messages are completed with \r\n, this removes the blank index. If the last message is incomplete, this moves it to readBuffer to be completed on the next socket.recv()
		
		for line in temp:
			self.tempMessages.append(string.rstrip(line)) #clean up whitespace
		
		self.messages=self.tempMessages
		self.tempMessages=[]
		
		for line in self.messages: #Eventually I shouldn't have to do this once some sort of listening function is created
			message=string.split(line, ":")
			word=string.split(line)
			if(word[1]=="433"):
				self.nick(self.nickname+"_")
			if(word[0]=="PING"):
				self.sendMessage("PONG "+word[1])
			
			self.printVerbose(self.timestamp()+" |<- "+line)
		
		return self.messages
	
	def message(self, message): #Sends a raw message to the server terminated with a newline
		try:
			bytesSent = self.socket.send(message+"\r\n") #send message over the socket
		except socket.timeout as error:
			print "Timed out (%s)." % self.timeout
			self.connected = 0
			self.reconnect()
		except socket.error as error:
			print str(error)
			self.connected = 0
			self.reconnect()
			return self.messages
		else:
			self.printVerbose(self.timestamp()+" ->| "+message)
			return bytesSent
	
	def sendMessage(self, message): #Deprecated form of message TODO: remove in rc1
		self.message(message)
	
	def privmsg(self,recipient, message): #Sends a PRIVMSG
		self.sendMessage("PRIVMSG %s :%s" % (recipient, message))
	
	def sendPrivmsg(self, recipient, message): #Deprecated form of privmsg TODO: remove in rc1
		self.privmsg(recipient, message)
	
	def printVerbose(self, message): #Prints a message if the self.verbose variable has been turned on
		if self.verbose==1: print message
	
	def timestamp(self):
		now = time.localtime(time.time())
		year, month, day, hour, minute, second, weekday, yearday, daylight = now
		timestamp = "%02d:%02d:%02d" % (hour, minute, second)
		return timestamp
