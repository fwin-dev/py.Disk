import _base
from Net import SSH

from Walker import WalkerAbstract

class SSHpathAbstract:
	def __init__(self, connection):
		self.connection = connection
		assert isinstance(self.connection, SSH.Connection)
	def _makeFilePath(self, newPath):
		return FilePath(self.connection, newPath)
	def _makeFolderPath(self, newPath):
		return FolderPath(self.connection, newPath)
	def _buildFunc(self, funcName, argParser):
		return _buildFunc(funcName, argParser, self)

class FolderPath(SSHpathAbstract, _base.FolderPath):
	"""Path of a folder on a remote machine."""
	def __init__(self, connection, remotePath):
		_base.FolderPath.__init__(self, remotePath, SSHFolderWalker)
		SSHpathAbstract.__init__(self, connection)
	@classmethod
	def _argsConvert_input(cls, funcName, argParser, args, toString):
		args = super(FolderPath, cls)._argsConvert_input(funcName, argParser, args)
		if toString:
			args = _argsConvert_toString(funcName, argParser, args, cls)
		return args
	def rmtree(self):
		return self.connection.runPyCode_singleLine("shutil.rmtree(" + SSH.escapePath(self) + ")", ["shutil"])

class FilePath(SSHpathAbstract, _base.FilePath):
	"""Path of a file on a remote machine."""
	def __init__(self, connection, remotePath):
		SSHpathAbstract.__init__(self, connection)
		_base.FilePath.__init__(self, remotePath)
	def asFile(self, mode):
		from SSH import File
		return File(self.connection, self.asStr(), mode)
	def copy(self, destFilePath, shouldCopyDates):
		"""
		@param destFilePath		FilePath:	Any FilePath instance
		@param shouldCopyDates	bool:		If `True`, last modified time and last accessed time for the destination file will be the same as the source file.
		"""
		if isinstance(destFilePath, self.__class__) and destFilePath.connection == self.connection:
			if not shouldCopyDates:
				self.connection.runShellCMD("cp " + SSH.escapePath(self.path) + " " + SSH.escapePath(destFilePath.path))
			else:
				self.connection.runShellCMD("rsync -t " + SSH.escapePath(self.path) + " " + SSH.escapePath(destFilePath.path))
		else:
			return _base.FilePath.copy(self, destFilePath, shouldCopyDates)
	def move(self, destFilePath):
		if isinstance(destFilePath, self.__class__) and destFilePath.connection == self.connection:
			self.connection.runShellCMD("mv " + SSH.escapePath(self.path) + " " + SSH.escapePath(destFilePath.path))
		else:
			return _base.FilePath.move(self, destFilePath)
			
	@classmethod
	def _argsConvert_input(cls, funcName, argParser, args, toString):
		args = super(FilePath, cls)._argsConvert_input(funcName, argParser, args)
		if toString:
			args = _argsConvert_toString(funcName, argParser, args, cls)
		return args

def _buildFunc(funcName, argParser, pathInstance):
	"""
	@return function:	Returns a run function which, when called, will run the function specified by funcName either on
						the remote machine or the local machine (for speed improvement, instead of going across the network.
	"""
	isLocalFunc = argParser.isLocal(funcName)
	func = argParser.getBuiltinFunction(funcName, not isLocalFunc)
	
	def _run(*args):
		args = [pathInstance] + list(args)
		result = __run(func, pathInstance._argsConvert_input(funcName, argParser, args, not isLocalFunc))
		return pathInstance._argsConvert_output(funcName, argParser, result, args)
	
	if isLocalFunc:
		def __run(func, args):
			return func(*args)
	else:
		def __run(func, args):
			return pathInstance.connection.runPyCode_singleLine(func + "(" + ", ".join(args) + ")", ["os","os.path"])
	return _run


def _argsConvert_toString(funcName, argParser, args, pathClass):
	for i in range(0, len(args)):
		if isinstance(args[i], str) or isinstance(args[i], unicode):
			args[i] = "'" + args[i].replace("'", "\\'") + "'"
		else:
			args[i] = str(args[i])
	return args


class SSHFolderWalker(WalkerAbstract):
	def __init__(self):
		super(SSHFolderWalker, self).__init__(FolderPath)
	@classmethod
	def _getOSwalkResults(cls, folder, topDown, followSymlinks):
		cmd = "[i for i in os.walk(" + SSH.escapePath(folder) + ", topdown=" + str(topDown) + ", followlinks=" + str(followSymlinks) + ")]"
		return folder.connection.runPyCode_singleLine(cmd, "os")

