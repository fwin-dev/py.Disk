import _base
from Walker import WalkerAbstract
import OS

import os, shutil

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

class PathAbstract:
	"""
	Abstract concept of a file or folder path.
	
	This is a mixin without using super() because super can't call different superclass constructors with different arguments.
	"""
	def _makeFilePath(self, newPath):
		return FilePath(newPath)
	def _makeFolderPath(self, newPath):
		return FolderPath(newPath)
	def _buildFunc(self, funcName, argParser):
		"""Hook for argument and return value conversion."""
		return _buildFunc(funcName, argParser, self)

class FolderPath(PathAbstract, _base.FolderPath):
	"""A locally accessible folder path."""
	def __init__(self, path):
		_base.FolderPath.__init__(self, path, LocalFolderWalker)
	def rmtree(self):
		"""@see shutil.rmtree"""
		return shutil.rmtree(str(self))

class FilePath(PathAbstract, _base.FilePath):
	"""A locally accessible file path."""
	def __init__(self, path):
		_base.FilePath.__init__(self, path)
	def asFile(self, mode):
		"""
		@param mode		str:	@see File
		@return File
		"""
		return File(self.asStr(), mode)
	
	def move(self, destFilePath):
		"""
		Moves a file to destFilePath.
		
		Performs a local move operation if the source file path and destination are both local.
		"""
		if isinstance(destFilePath, self.__class__):	# shortcut for when file is on same drive - don't do copy then delete
			OS.runCMD("mv %s %s", (self, destFilePath))
		else:
			return _base.FilePath.move(self, destFilePath)


def _buildFunc(funcName, argParser, pathInstance):
	func = argParser.getBuiltinFunction(funcName, False)
	def _run(*args):
		args = [pathInstance] + list(args)
		result = func(*(pathInstance._argsConvert_input(funcName, argParser, args)))
		return pathInstance._argsConvert_output(funcName, argParser, result, args)
	return _run

_base.PathAbstract._registerType(File, FilePath, FolderPath)

class LocalFolderWalker(WalkerAbstract):
	"""Implementation of WalkerAbstract for folders on the local system."""
	def __init__(self):
		super(LocalFolderWalker, self).__init__()
	@classmethod
	def _getOSwalkResults(cls, folder, topDown, followSymlinks):
		return os.walk(str(folder), topdown=topDown, followlinks=followSymlinks)

WalkerAbstract._registerType(LocalFolderWalker, FolderPath)
