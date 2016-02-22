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

import errno, os, paramiko

class SFTPInterface(paramiko.SFTPServerInterface):
	def __init__(self, server, *largs, **kwargs):
		super(paramiko.SFTPServerInterface, self).__init__(*largs, **kwargs)

		self.client = paramiko.SFTPClient.from_transport(server.client)
		self.root_path = server.root_path if ('root_path' in server.__dict__) else ''

	def _parsePath(self, path):
		result = os.path.normpath(self.root_path + '/' + path)
		if not result.startswith(self.root_path):
			raise IOError(errno.EACCES)
		return result

	def list_folder(self, path):
		try:
			return self.client.listdir_attr(self._parsePath(path))
		except IOError as e:
			return paramiko.SFTPServer.convert_errno(e.errno)

	def stat(self, path):
		try:
			return self.client.stat(self._parsePath(path))
		except IOError as e:
			return paramiko.SFTPServer.convert_errno(e.errno)

	def lstat(self, path):
		try:
			return self.client.lstat(self._parsePath(path))
		except IOError as e:
			return paramiko.SFTPServer.convert_errno(e.errno)

	def open(self, path, flags, attr):
		if (flags & os.O_CREAT) and (attr is not None):
			attr._flags &= ~attr.FLAG_PERMISSIONS
			paramiko.SFTPServer.set_file_attr(self._parsePath(path), attr)
		if flags & os.O_WRONLY:
			if flags & os.O_APPEND:
				fstr = 'ab'
			else:
				fstr = 'wb'
		elif flags & os.O_RDWR:
			if flags & os.O_APPEND:
				fstr = 'a+b'
			else:
				fstr = 'r+b'
		else:
			# O_RDONLY (== 0)
			fstr = 'rb'

		try:
			f = self.client.open(self._parsePath(path), fstr)
		except IOError as e:
			return paramiko.SFTPServer.convert_errno(e.errno)

		fobj = paramiko.SFTPHandle(flags)
		fobj.filename = self._parsePath(path)
		fobj.readfile = f
		fobj.writefile = f
		fobj.client = self.client
		return fobj
		# TODO: verify (socket.error when stopping file upload/download)

	def remove(self, path):
		try:
			self.client.remove(self._parsePath(path))
		except IOError as e:
			return paramiko.SFTPServer.convert_errno(e.errno)
		return paramiko.SFTP_OK

	def rename(self, oldpath, newpath):
		try:
			self.client.rename(self._parsePath(oldpath), self._parsePath(newpath))
		except IOError as e:
			return paramiko.SFTPServer.convert_errno(e.errno)
		return paramiko.SFTP_OK

	def mkdir(self, path, attr):
		try:
			if attr.st_mode is None:
				self.client.mkdir(self._parsePath(path))
			else:
				self.client.mkdir(self._parsePath(path), attr.st_mode)
		except IOError as e:
			return paramiko.SFTPServer.convert_errno(e.errno)
		return paramiko.SFTP_OK

	def rmdir(self, path):
		try:
			self.client.rmdir(self._parsePath(path))
		except IOError as e:
			return paramiko.SFTPServer.convert_errno(e.errno)
		return paramiko.SFTP_OK

	def chattr(self, path, attr):
		try:
			if attr._flags & attr.FLAG_PERMISSIONS:
				self.client.chmod(self._parsePath(path), attr.st_mode)
			if attr._flags & attr.FLAG_UIDGID:
				self.client.chown(self._parsePath(path), attr.st_uid, attr.st_gid)
			if attr._flags & attr.FLAG_AMTIME:
				self.client.utime(self._parsePath(path), (attr.st_atime, attr.st_mtime))
			if attr._flags & attr.FLAG_SIZE:
				with self.client.open(self._parsePath(path), 'w+') as f:
					f.truncate(attr.st_size)
		except IOError as e:
			return paramiko.SFTPServer.convert_errno(e.errno)
		return paramiko.SFTP_OK

	def symlink(self, target_path, path):
		# TODO
		return paramiko.SFTP_OP_UNSUPPORTED

	def readlink(self, path):
		# TODO
		return paramiko.SFTP_OP_UNSUPPORTED
