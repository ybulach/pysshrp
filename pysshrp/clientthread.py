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

import logging, paramiko, re

import copy, pysshrp.common

class ClientThread(paramiko.ServerInterface):
	logger = logging.getLogger('pysshrpd.client')

	def __init__(self):
		self.client = None
		self.upstream = None
		self.root_path = ''
		self.shellchannel = None
		self.shellthread = None

	def get_allowed_auths(self, username):
		return 'password,publickey'

	def _findUpstream(self, username):
		upstream = None
		regex_extracts = None

		# Find the best upstream match for the given username
		for server in pysshrp.common.config.servers:
			# Regex (less accurate)
			if server.user.startswith('^'):
				regex_extracts = re.search(server.user, username)
				if regex_extracts:
					# Keep searching for something more accurate
					upstream = copy.deepcopy(server)

			# String (more accurate)
			elif server.user == username:
				# Nothing can be more accurate
				regex_extracts = None
				upstream = copy.deepcopy(server)
				break

		# No match
		if not upstream:
			self.logger.critical('%s:%d: no upstream found for username "%s"' % (self.client_address + (username,)))
			return None

		# Get upstream configuration
		if regex_extracts:
			upstream.upstream_host = regex_extracts.expand(upstream.upstream_host)
			upstream.upstream_user = regex_extracts.expand(upstream.upstream_user)
		else:
			upstream.upstream_host = upstream.upstream_host
			upstream.upstream_user = upstream.upstream_user

		upstream.upstream_port = upstream.upstream_port
		self.root_path = upstream.upstream_root_path

		if not upstream.upstream_user:
			upstream.upstream_user = username

		return upstream

	def _connectToUpstream(self, upstream, password=False, publickey=False):
		try:
			upstream_password = upstream.upstream_password if password else None
			upstream_key = upstream.upstream_key if publickey else None

			self.client = paramiko.SSHClient()
			self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
			self.client.connect(upstream.upstream_host, port=upstream.upstream_port, username=upstream.upstream_user, password=upstream_password, pkey=upstream_key)
			self.shellchannel = self.client.get_transport().open_session()

			self.logger.info('%s:%d: connected to upstream %s@%s:%d' % (self.client_address + (upstream.upstream_user, upstream.upstream_host, upstream.upstream_port)))
			self.upstream = upstream
			return paramiko.AUTH_SUCCESSFUL
		except paramiko.SSHException:
			self.logger.critical('%s:%d: connection failed to upstream %s@%s:%d' % (self.client_address + (upstream.upstream_user, upstream.upstream_host, upstream.upstream_port)))
			self.upstream = None
			return paramiko.AUTH_FAILED

	def check_auth_password(self, username, password):
		self.logger.info('%s:%d: trying password authentication for "%s"' % (self.client_address + (username,)))

		# Check the username
		upstream = self._findUpstream(username)
		if not upstream:
			return paramiko.AUTH_FAILED

		# Local authentication
		if upstream.password and not (upstream.password == password):
			self.logger.critical('%s:%d: local authentication of "%s" failed' % (self.client_address + (username,)))
			return paramiko.AUTH_FAILED

		# Connect to the upstream
		if not upstream.upstream_password:
			upstream.upstream_password = password
		return self._connectToUpstream(upstream, password=True)

	def check_auth_publickey(self, username, key):
		self.logger.info('%s:%d: trying publickey authentication for "%s"' % (self.client_address + (username,)))

		# Check the username
		upstream = self._findUpstream(username)
		if not upstream:
			return paramiko.AUTH_FAILED

		# Look for the client key in upstream's authorized_keys file
		if not upstream.upstream_key:
			self.logger.warning('%s:%d: publickey authentication is disabled for "%s"' % (self.client_address + (username,)))
			return paramiko.AUTH_FAILED

		authenticated = False
		if self._connectToUpstream(upstream, publickey=True) == paramiko.AUTH_SUCCESSFUL:
			try:
				sftp = self.client.open_sftp()
				with sftp.file('.ssh/authorized_keys', 'r') as file:
					for line in file.readlines():
						line = line.split(' ')
						if (len(line) >= 2) and (line[0] == key.get_name()) and (line[1] == key.get_base64()):
							authenticated = True
							break
				sftp.close()
			except Exception:
				pass

			# Close all connections
			self.upstream = None
			self.shellchannel.close()
			self.client.close()

		if not authenticated:
			self.logger.critical('%s:%d: authentication of "%s" with publickey failed' % (self.client_address + (username,)))
			self.upstream = None
			return paramiko.AUTH_FAILED

		# Connect to the upstream
		return self._connectToUpstream(upstream, publickey=True)

	def check_channel_request(self, kind, chanid):
		if kind == 'session':
			return paramiko.OPEN_SUCCEEDED
		return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

	def check_channel_exec_request(self, channel, command):
		if not self.upstream or not self.upstream.allow_ssh:
			return False

		try:
			self.shellchannel.exec_command(command)

			self.shellthread = pysshrp.SSHInterface(channel, self.shellchannel)
			self.shellthread.start()
			self.logger.info('%s:%d: new exec requested' % self.client_address)
			return True
		except paramiko.SSHException:
			self.logger.critical('%s:%d: exec request failed' % self.client_address)
			return False

	def check_channel_shell_request(self, channel):
		if not self.upstream or not self.upstream.allow_ssh:
			return False

		try:
			self.shellchannel.invoke_shell()

			self.shellthread = pysshrp.SSHInterface(channel, self.shellchannel)
			self.shellthread.start()
			self.logger.info('%s:%d: new shell requested' % self.client_address)
			return True
		except paramiko.SSHException:
			self.logger.critical('%s:%d: shell request failed' % self.client_address)
			return False

	def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
		if not self.upstream or not self.upstream.allow_ssh:
			return False

		try:
			self.shellchannel.get_pty(term, width, height, pixelwidth, pixelheight)
			self.logger.info('%s:%d: new pty requested' % self.client_address)
			return True
		except paramiko.SSHException:
			self.logger.critical('%s:%d: pty request failed' % self.client_address)
			return False

	def check_channel_subsystem_request(self, channel, name):
		if not self.upstream or not self.upstream.allow_sftp:
			return False

		try:
			super(ClientThread, self).check_channel_subsystem_request(channel, name)
			self.logger.info('%s:%d: new subsystem "%s" requested' % (self.client_address + (name,)))
			return True
		except paramiko.SSHException:
			self.logger.critical('%s:%d: subsystem "%s" request failed' % (self.client_address + (name,)))
			return False

	def check_channel_window_change_request(self, channel, width, height, pixelwidth, pixelheight):
		if not self.upstream or not self.upstream.allow_ssh:
			return False

		try:
			self.shellchannel.resize_pty(width, height, pixelwidth, pixelheight)
			self.logger.info('%s:%d: pty resized' % self.client_address)
			return True
		except paramiko.SSHException:
			self.logger.critical('%s:%d: pty resizing failed' % self.client_address)
			return False
