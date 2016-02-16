#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pysshrp.
#
# pysshrp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pysshrp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pysshrp.  If not, see <http://www.gnu.org/licenses/>.

import os, paramiko, SocketServer, time

import pysshrp.common
from pysshrp.clientthread import ClientThread
from pysshrp.sftpinterface import SFTPInterface

class RequestHandler(SocketServer.BaseRequestHandler):
	def __init__(self, request, client_address, server):
		# Change user and group (only when runned as root)
		if (os.getgid() == 0) and pysshrp.common.config.userId:
			os.setgid(pysshrp.common.config.userId)
		if (os.getuid() == 0) and pysshrp.common.config.groupId:
			os.setuid(pysshrp.common.config.groupId)

		SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)

	def setup(self):
		pysshrp.common.logger.info('New client thread started')
		self.clientthread = ClientThread()

		return SocketServer.BaseRequestHandler.setup(self)

	def handle(self):
		transport = paramiko.Transport(self.request)
		transport.add_server_key(pysshrp.common.config.keyData)
		transport.set_subsystem_handler('sftp', paramiko.SFTPServer, SFTPInterface)

		transport.start_server(server=self.clientthread)

		while transport.is_active() and pysshrp.common.running:
			time.sleep(1)

	def finish(self):
		if self.clientthread.client:
			self.clientthread.client.close()
		pysshrp.common.logger.info('Client thread ended')

		return SocketServer.BaseRequestHandler.finish(self)

class ServerThread(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	pass
