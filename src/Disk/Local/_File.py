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
	def __exit__(self, *args):
		super(BaseFile, self).__exit__(*args)
	
	def _reopen(self):
		self._file = open(str(self.getPath()), self.mode)
	
	def _getPath(self):
		return FilePath(self._file.name)
	
	def open(self):
		"""Opens or re-opens the file with the mode specified in the constructor."""
		return self._reopen()
	
	def __getattr__(self, name):
		if self._file == None:
			if name == "close":
				return lambda: None
			elif name == "closed":
				return True
			else:
				raise AttributeError("Attempt to call method " + str(name) + " before file was opened")
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

