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
	def _buildFunc(self, funcName, funcDescriptor):
		"""Hook for argument and return value conversion."""
		return _buildFunc(funcName, funcDescriptor, self)
	
	def move(self, destPath):
		"""
		Moves a file or folder to destPath.
		
		Performs a local move operation if the source file path and destination are both on the same drive.
		"""
		if isinstance(destPath, self.__class__):
			shutil.move(str(self), str(destPath))
		else:
			return _base.FilePath.move(self, destPath)

def _buildFunc(funcName, funcDescriptor, pathInstance):
	func = funcDescriptor.getBuiltinFunction(funcName, False)
	def _run(*args):
		args = [pathInstance] + list(args)
		result = func(*(pathInstance._argsConvert_input(funcName, funcDescriptor, args)))
		return pathInstance._argsConvert_output(funcName, funcDescriptor, result, args)
	return _run


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
