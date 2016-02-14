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

import paramiko, SocketServer, time

import pysshrp.common
from pysshrp.clientthread import ClientThread
from pysshrp.sftpinterface import SFTPInterface

class RequestHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		pysshrp.common.logger.info('New client thread started')
		transport = paramiko.Transport(self.request)
		transport.add_server_key(pysshrp.common.config.key)
		transport.set_subsystem_handler('sftp', paramiko.SFTPServer, SFTPInterface)

		transport.start_server(server=ClientThread())

		channel = transport.accept()
		while transport.is_active() and pysshrp.common.running:
			time.sleep(1)

class ServerThread(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	pass
