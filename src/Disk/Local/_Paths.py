from Disk import _base
import OS

import shutil

class PathAbstract(object):
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
		from _Walker import LocalFolderWalker
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
		from _File import File
		return File(self.asStr(), mode)
	
	def move(self, destFilePath):
		"""
		Moves a file to destFilePath.
		
		Performs a local move operation if the source file path and destination are both local.
		"""
		if isinstance(destFilePath, self.__class__):	# shortcut for when file is on same drive - don't do copy then delete
			shutil.move(str(self), str(destFilePath))
		else:
			return _base.FilePath.move(self, destFilePath)


def _buildFunc(funcName, argParser, pathInstance):
	func = argParser.getBuiltinFunction(funcName, False)
	def _run(*args):
		args = [pathInstance] + list(args)
		result = func(*(pathInstance._argsConvert_input(funcName, argParser, args)))
		return pathInstance._argsConvert_output(funcName, argParser, result, args)
	return _run

