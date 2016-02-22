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

import select, threading

class SSHInterface(threading.Thread):
	def __init__(self, serverchan, clientchan, *largs, **kwargs):
		super(SSHInterface, self).__init__(*largs, **kwargs)

		self.serverchan = serverchan
		self.clientchan = clientchan

	def run(self):
		try:
			while self.serverchan.get_transport().is_active() and self.clientchan.get_transport().is_active():
				r, w, e = select.select([self.serverchan, self.clientchan], [], [])
				if self.serverchan in r:
					try:
						x = self.serverchan.recv(1024)
						if len(x) == 0:
							break
						self.clientchan.send(x)
					except socket.timeout:
						pass
				if self.clientchan in r:
					try:
						x = self.clientchan.recv(1024)
						if len(x) == 0:
							break
						self.serverchan.send(x)
					except socket.timeout:
						pass
		finally:
			if self.serverchan:
				self.serverchan.close()
			if self.clientchan:
				self.clientchan.close()
