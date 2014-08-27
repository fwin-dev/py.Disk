from Disk import _base
from _Paths import FilePath

class BaseFile(_base.File):
	"""Abstract concept of a file object."""
	def __init__(self, mode):
		"""
		@param mode		str:	Same as mode passed to the python built-in open() function.
		"""
		super(BaseFile, self).__init__(mode)
		self._file = None
	
	def __enter__(self):
		return super(BaseFile, self).__enter__()
	def __exit__(self, *args, **kwargs):
		return super(BaseFile, self).__exit__(*args, **kwargs)
	
	def _reopen(self):
#		print("baseFile: opening for " + self.mode + ": " + str(self.getPath()))
		self._file = open(str(self.getPath()), self.mode)
	
	def open(self):
		"""Opens or re-opens the file with the mode specified in the constructor."""
		return self._reopen()
	
	def close(self):
		if self._file == None:
#			print("baseFile: tried to close but not open: " + str(self.getPath()))
			return
		self._file.close()
#		print("baseFile: closed: " + str(self.getPath()))
		self._file = None
	def closed(self):
		return self._file == None
	def isClosed(self):
		return self.closed()
	
	def __getattr__(self, name):
		if self._file == None:
			raise AttributeError("Attempt to access method " + str(name) + " before file was opened")
		if hasattr(self._file, name):
			return getattr(self._file, name)
		raise AttributeError

class File(BaseFile):
	"""Implementation of BaseFile using a FilePath instance to store the path."""
	def __init__(self, path, mode):
		if isinstance(path, FilePath):
			path = str(path)
		self._path = path
		self.mode = mode
		super(File, self).__init__(mode)
	def _getPath(self):
		return FilePath(self._path)

