#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-03-24
# @Author  : Robin (sintrb@gmail.com)
# @Version : 1.0

from PyDNSServer import DNSQueryHandler, DNSServer

import re

filters = [
	('baidu.com', 'allow'),
	('360.com', 'deny'),
	('qq.com', '192.168.0.100'),
	('.*', 'deny'),
]

class FilterHandler(DNSQueryHandler):
	def when_query(self, hostname, dns, rawdata, sock):
		# ip = self.queryip(hostname)
		for p, v in filters:
			if p == hostname or re.match(p, hostname):
				if v == 'deny':
					break
				elif v == 'allow':
					ip = self.queryip(hostname)
				else:
					ip = v
				print '%s %s %s'%(self.client_address[0], hostname, ip)
				return ip
		
if __name__ == "__main__":
	import sys

	filters = [] # clear

	# config with dns.cfg
	with open('dns.cfg') as f:
		for l in f:
			l = l.strip()
			if l.startswith('#') or not l:
				continue
			try:
				rs = re.findall('(\S+)\s+(\S+)',l)
				p = rs[0][0]
				m = rs[0][1]
				print '%s-->%s'%(p,m)
				filters.append((p,m))
			except:
				print 'err line: %s'%l
	host, port = '0.0.0.0', len(sys.argv) >= 2 and int(sys.argv[1]) or 53
	serv = DNSServer((host, port), DNSQueryHandlerClass=FilterHandler)
	print 'DNS Server running at %s:%s'%(host, port)
	serv.serve_forever()
