from Disk import _base
import Net.SSH
from Disk.TempFile import NamedSecureTempFile
from _Paths import FilePath
from Lang.Struct import OrderedDict

import os.path

class File(_base.File):
	"""Represents a file on a remote machine."""
	def __init__(self, connection, remotePath, mode="rb"):
		super(File, self).__init__(mode)
		self.connection = connection
		assert isinstance(self.connection, Net.SSH.Connection)
		self.remotePath = remotePath
		if isinstance(self.remotePath, FilePath):
			self.remotePath = str(self.remotePath)
		self._file = None
	def __repr__(self, valueLabel=None, value=None, extraPairDict=None, message=None):
		extraPairDict = OrderedDict(extraPairDict)
		if self.isWritable():
			extraPairDict["needsFlush"] = self._needsFlush
		return super(File, self).__repr__(valueLabel=valueLabel, value=value, extraPairDict=extraPairDict, message=message)
	
	def _reopen(self):
		assert self.getPath().dirname().exists()
		if self.mode not in ["w", "wb"]:	# need to know file contents since we're reading
			if not self.getPath().exists():
				self.connection.runShellCMD("touch " + Net.SSH.escapePath(self.remotePath))
			self._file = NamedSecureTempFile("wb")
			with self._file:
				self.connection.download(self.remotePath, self._file)	# download supports file like objects with a "write" method
			self._file.reopen(self.mode)
		else:
#			print(self.__str__("opening"))
			self._file = NamedSecureTempFile(self.mode)
			self._file.__enter__()
		if self.isWritable(ignoreClosedState=True):
			self._needsFlush = True
#			print(self.__str__("made temp file and opened"))
#			print(repr(self))
	
	def _getPath(self):
		return FilePath(self.connection, self.remotePath)
	
	def __getattr__(self, name):
		if name not in ["read", "write", "seek", "tell", "mode", "closed"]:
			raise AttributeError
		if name == "write":
#			print("writing to temp file")
			self._needsFlush = True
		if self._file == None:
			if name == "close":
				return lambda: None
			elif name == "closed":
				return lambda: True
			else:
				raise AttributeError("Attempt to call method " + str(name) + " before file was opened")
		if hasattr(self._file, name):
			return getattr(self._file, name)
		raise AttributeError
	
	def flush(self):
		"""Uploads the file if changed."""
		self._file.flush()
#		print(repr(self))
		if not self.isWritable() or not self._needsFlush:
			return
		self.connection.upload(self._file.name, os.path.dirname(self.remotePath))
		remoteTempFilePath = os.path.join(os.path.dirname(self.remotePath), os.path.basename(self._file.name))
		self.connection.runShellCMD("mv " + Net.SSH.escapePath(remoteTempFilePath) + " " + Net.SSH.escapePath(self.remotePath))
		assert self._file.getPath().stat().st_size == self.getPath().stat().st_size
		self._needsFlush = False
	
	def isClosed(self):
		return self.closed()
	def close(self):
		self.flush()
		self._file.destruct()

