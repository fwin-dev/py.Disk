from Local._File import File

import os, tempfile

class NamedSecureTempFile(File):
	"""
	This is basically a combination of python's built-in tempfile.NamedTemporaryFile and tempfile.mkstemp
	@see NamedTemporaryFile
	@see tempfile.mkstemp
	"""
	def __init__(self, mode="wb", suffix="", prefix="py_tmp", dir=None, delete=True):
		self.delete = delete
		self.suffix = suffix
		self.prefix = prefix
		self.dir = dir
		
		fd, path = tempfile.mkstemp(self.suffix, self.prefix, self.dir)
		fileLikeObj = os.fdopen(fd, mode)
		fileLikeObj.close()
		super(NamedSecureTempFile, self).__init__(path, mode)
	
	def destruct(self):
		"""Call when this file is no longer needed. If `delete` (set in constructor) is True, the file will be deleted."""
		super(NamedSecureTempFile, self).destruct()
		if self.delete:
			os.remove(self._path)
