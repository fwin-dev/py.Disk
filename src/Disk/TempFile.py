from Local import BaseFile, FilePath

import os, tempfile

class NamedSecureTempFile(BaseFile):
	"""
	This is basically a combination python's built-in tempfile.NamedTemporaryFile and tempfile.mkstemp
	@see NamedTemporaryFile
	@see tempfile.mkstemp
	"""
	def __init__(self, mode="wb", suffix="", prefix="py_tmp", dir=None, delete=True):
		super(NamedSecureTempFile, self).__init__(mode)
		self.delete = delete
		self.suffix = suffix
		self.prefix = prefix
		self.dir = dir
		
		fd, self.name = tempfile.mkstemp(self.suffix, self.prefix, self.dir)
		fileLikeObj = os.fdopen(fd, self.mode)
		fileLikeObj.close()
	
	def destruct(self):
		"""Call when this file is no longer needed. If `delete` (set in constructor) is True, the file will be deleted."""
		BaseFile.destruct(self)
		if self.delete:
			os.remove(self.name)

	def _getPath(self):
		return FilePath(self.name)
