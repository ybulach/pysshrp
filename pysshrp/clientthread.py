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

import paramiko, re

import pysshrp.common

class ClientThread(paramiko.ServerInterface):
	def __init__(self):
		self.client = None
		self.root_path = ''
		self.shellchannel = None
		self.shellthread = None

	def get_allowed_auths(self, username):
		return 'password'

	def _findUpstream(self, username):
		for server in pysshrp.common.config.servers:
			# Regex
			if server.user.startswith('^'):
				regex_extracts = re.search(server.user, username)
				if regex_extracts:
					return (regex_extracts, server)
			# String
			elif server.user == username:
				return (None, server)

		return (None, None)

	def check_auth_password(self, username, password):
		regex_extracts = None
		found = False

		# Check the username
		regex_extracts, server = self._findUpstream(username)

		if not server:
			return paramiko.AUTH_FAILED

		# Get upstream configuration
		if regex_extracts:
			upstream_host = regex_extracts.expand(server.upstream_host)
			upstream_user = regex_extracts.expand(server.upstream_user)
		else:
			upstream_host = server.upstream_host
			upstream_user = server.upstream_user

		upstream_port = server.upstream_port
		self.root_path = server.upstream_root_path

		if not upstream_user:
			upstream_user = username

		# Connect to the upstream
		try:
			pysshrp.common.logger.info('New upstream connection to %s@%s:%d' % (upstream_user, upstream_host, upstream_port))

			self.client = paramiko.Transport((upstream_host, upstream_port))
			self.client.start_client()
			self.client.auth_password(upstream_user, password)
			self.shellchannel = self.client.open_session()

			return paramiko.AUTH_SUCCESSFUL
		except paramiko.SSHException:
			return paramiko.AUTH_FAILED

	def check_auth_publickey(self, username, key):
		return paramiko.AUTH_FAILED

	def check_channel_request(self, kind, chanid):
		if kind == 'session':
			return paramiko.OPEN_SUCCEEDED
		return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

	def check_channel_exec_request(self, channel, command):
		return False

	def check_channel_shell_request(self, channel):
		try:
			self.shellchannel.invoke_shell()

			self.shellthread = pysshrp.SSHInterface(channel, self.shellchannel)
			self.shellthread.start()
			return True
		except paramiko.SSHException:
			return False

	def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
		try:
			self.shellchannel.get_pty(term, width, height, pixelwidth, pixelheight)
			return True
		except paramiko.SSHException:
			return False
