#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-06-30
# @Author  : Robin (sintrb@gmail.com)
# @Link    : https://github.com/sintrb/PyDNSServer
# @Version : 1.0

import SocketServer
import struct
import re
import datetime
import socket as socketlib

class DNSQuery:
	'''
	DNS Query Object
	'''
	def __init__(self, data):
		i = 1
		self.name = ''
		while True:
			d = ord(data[i])
			if d == 0:
				break;
			if d < 32:
				self.name = self.name + '.'
			else:
				self.name = self.name + chr(d)
			i = i + 1
		self.querybytes = data[0:i + 1]
		(self.type, self.classify) = struct.unpack('>HH', data[i + 1:i + 5])
		self.len = i + 5
	def getbytes(self):
		return self.querybytes + struct.pack('>HH', self.type, self.classify)


class DNSAnswer:
	'''
	DNS Answer RRS
	this class is also can be use as Authority RRS or Additional RRS
	'''
	def __init__(self, ip):
		self.name = 49164
		self.type = 1
		self.classify = 1
		self.timetolive = 190
		self.datalength = 4
		self.ip = ip
	def getbytes(self):
		res = struct.pack('>HHHLH', self.name, self.type, self.classify, self.timetolive, self.datalength)
		s = self.ip.split('.')
		res = res + struct.pack('BBBB', int(s[0]), int(s[1]), int(s[2]), int(s[3]))
		return res


class DNSFrame:
	'''
	DNS frame,
	Must initialized by a DNS query frame data
	'''
	def __init__(self, data):
		self.id, self.flags, self.quests, self.answers, self.author, self.addition = struct.unpack('>HHHHHH', data[0:12])
		self.query = DNSQuery(data[12:])
	def getname(self):
		return self.query.name
	def setip(self, ip):
		self.answer = DNSAnswer(ip)
		self.answers = 1
		self.flags = 33152
	def getbytes(self):
		res = struct.pack('>HHHHHH', self.id, self.flags, self.quests, self.answers, self.author, self.addition)
		res = res + self.query.getbytes()
		if self.answers != 0:
			res = res + self.answer.getbytes()
		return res

class DNSQueryHandler(SocketServer.BaseRequestHandler):
	'''
	A UDPHandler to handle DNS query
	'''
	def queryip(self, hostname):
		'''
		Get a host ip from DNS Server(config in system network)
		'''
		try:
			return socketlib.getaddrinfo(hostname,0)[0][4][0]
		except:
			return None
	def when_query(self, hostname, dns, rawdata, sock):
		'''
		When query host ip it will called,
		return a IPV4 address to response DNS query,
		such as '172.16.0.200'
		'''
		# ip = self.queryip(hostname)
		ip = '172.16.0.100'
		print '%s %s %s'%(self.client_address[0], hostname, ip)
		return ip
	def handle(self):
		'''
		To handle a UDP data request(DNS query is by UDP)
		'''
		data = self.request[0].strip()
		dns = DNSFrame(data)
		sock = self.request[1]
		if(dns.query.type==1):
			# If this is query a A record, then response it
			ip = self.when_query(dns.getname(), dns, data, sock)
			if ip:
				dns.setip(ip)
			sock.sendto(dns.getbytes(), self.client_address)

		else:
			# else, ignore it, because can't handle it
			sock.sendto(data, self.client_address)


class DNSServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
	'''
	DNS Server,
	It only support A record query
	'''
	def __init__(self, server_address=('0.0.0.0', 53), DNSQueryHandlerClass=DNSQueryHandler):
		'''
		Init a DNS Server,
		DNSQueryHandlerClass must be a subclass of DNSQueryHandler
		'''
		SocketServer.UDPServer.__init__(self, server_address, DNSQueryHandlerClass)

# Now, test it
if __name__ == "__main__":
	import sys
	host, port = '0.0.0.0', len(sys.argv) == 2 and int(sys.argv[1]) or 53
	serv = DNSServer((host, port), )
	print 'DNS Server running at %s:%s'%(host, port)
	serv.serve_forever()

# Now, U can use "nslookup" command to test it
# Such as "nslookup - 127.0.0.1" or "nslookup www.aa.com 127.0.0.1"

