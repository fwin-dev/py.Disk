from __future__ import print_function
from Lang.FuncTools import Abstraction

from Lang.Struct import OrderedDict
from abc import ABCMeta, abstractmethod
import os, os.path, shutil

class ArgDescForPaths(Abstraction.ArgDesc):
	OTHER = 4
	FILE = 5
	FOLDER = 6

class PathFuncsAbstract(Abstraction.Descriptor):
	def isLocal(self, name):
		assert name not in self.REMOTE_UNSUPPORTED
		assert name in self.LOCAL + self.REMOTE
		return name in self.LOCAL
	def getArgTypes(self, name):
		if name == "walk":
			return [[ArgDescForPaths.SINGLE, ArgDescForPaths.FOLDER], [ArgDescForPaths.MULTI, ArgDescForPaths.OTHER]]
		
		if name in self.SINGLE_PATH_ARG:
			types = [[ArgDescForPaths.SINGLE]]
		elif name in self.MULTI_PATH_ARG:
			types = [[ArgDescForPaths.MULTI]]
		else:
			raise AttributeError
		
		if name in self.INPUTARGS_FILE_FOLDER:
			types[0].append(ArgDescForPaths.FILE)
			types[0].append(ArgDescForPaths.FOLDER)
		elif name in self.INPUTARGS_FILE:
			types[0].append(ArgDescForPaths.FILE)
		elif name in self.INPUTARGS_FOLDER:
			types[0].append(ArgDescForPaths.FOLDER)
		else:
			raise AttributeError
		
		return types


class OSPathFuncs(PathFuncsAbstract):
	def __init__(self):
		self.SINGLE_PATH_ARG = ("abspath", "basename", "dirname", "exists", "lexists", "expanduser", "expandvars", "getatime", "getctime", "getmtime", "getsize", "isabs", "isfile", "isdir", "islink", "ismount", "normcase", "normpath", "realpath", "split", "splitdrive", "splitext", "splitunc")
		self.MULTI_PATH_ARG = ("commonprefix", "join", "joinFile", "joinFolder", "relpath", "samefile")
		self.SPECIAL_PATH_ARG = tuple("walk")
		self.ALL_FUNCS = self.SPECIAL_PATH_ARG + self.SINGLE_PATH_ARG + self.MULTI_PATH_ARG
		
		# these will return the same result on any linux machine, so therefore can be run locally
		self.LOCAL = ("basename", "dirname", "isabs", "joinFile", "joinFolder", "normcase", "normpath", "split", "splitdrive", "splitext", "splitunc")
		# these are machine dependent and must be run remotely
		self.REMOTE = ("join", "abspath", "exists", "lexists", "expanduser", "expandvars", "getatime", "getmtime", "getctime", "getsize", "isfile", "isdir", "islink", "ismount", "realpath", "relpath", "samefile")
		self.REMOTE_UNSUPPORTED = ("walk")
		
		self.INPUTARGS_FILE = tuple()
		self.INPUTARGS_FOLDER = tuple("walk")
		self.INPUTARGS_FILE_FOLDER = tuple(filter(lambda x: x not in self.INPUTARGS_FILE + self.INPUTARGS_FOLDER, self.ALL_FUNCS))
		
		self.RETURN_FILE = tuple()
		self.RETURN_FOLDER = ("commonprefix", "dirname")
		self.RETURN_SAME_AS_INPUT_TYPE = ("abspath", "basename", "expanduser", "expandvars", "normcase", "normpath", "realpath", "relpath")
		self.RETURN_SPECIAL = ("join", "joinFile", "joinFolder", "split", "splitdrive", "splitext", "splitunc", "walk")
		self.RETURN_OTHER = tuple(filter(lambda x: x not in self.RETURN_FILE + self.RETURN_FOLDER + self.RETURN_SAME_AS_INPUT_TYPE + self.RETURN_SPECIAL, self.ALL_FUNCS))
	
	@classmethod
	def getBuiltinFunction(cls, funcName, asStr=False):
		if funcName in ("joinFile", "joinFolder"):
			funcName = "join"
		if not asStr:
			return getattr(os.path, funcName)
		else:
			assert hasattr(os.path, funcName)
			return "os.path." + funcName
OSPathFuncs = OSPathFuncs()


class OSFuncs(PathFuncsAbstract):
	def __init__(self):
		# other functions not listed here are not supported
		self.SINGLE_PATH_ARG = ("access", "chflags", "lchflags", "chmod", "lchmod", "chown", "lchown", "listdir", "lstat", "mkfifo",
								"mknod", "mkdir", "makedirs", "pathconf", "readlink", "remove", "removedirs", "rmdir", "stat",
								"statvfs", "tempnam", "unlink", "utime", "walk")
		self.MULTI_PATH_ARG = ("link", "symlink", "rename", "renames")
		self.SPECIAL_PATH_ARG = tuple("utime")
		self.ALL_FUNCS = self.SPECIAL_PATH_ARG + self.SINGLE_PATH_ARG + self.MULTI_PATH_ARG
		
		self.LOCAL = tuple()
		self.REMOTE = self.ALL_FUNCS
		# these are context sensitive and can't be run remotely because a new process is spawned every time
		self.REMOTE_UNSUPPORTED = ("chdir", "chroot")
		
		self.INPUTARGS_FILE = ("mknod", "pathconf", "remove", "unlink", "utime")
		self.INPUTARGS_FOLDER = ("listdir", "mkdir", "makedirs", "removedirs", "rmdir", "tempnam", "walk")
		self.INPUTARGS_FILE_FOLDER = tuple(filter(lambda x: x not in self.INPUTARGS_FILE + self.INPUTARGS_FOLDER, self.ALL_FUNCS))
		
		self.RETURN_FILE = tuple()
		self.RETURN_FOLDER = ("tempnam", "tmpnam")
		self.RETURN_SAME_AS_INPUT_TYPE = tuple("readlink")
		self.RETURN_SPECIAL = ("listdir", "walk")
		self.RETURN_OTHER = tuple(filter(lambda x: x not in self.RETURN_FILE + self.RETURN_FOLDER + self.RETURN_SAME_AS_INPUT_TYPE + self.RETURN_SPECIAL, self.ALL_FUNCS))
	
	@classmethod
	def getBuiltinFunction(cls, funcName, asStr=False):
		if not asStr:
			return getattr(os, funcName)
		else:
			assert hasattr(os, funcName)
			return "os." + funcName
OSFuncs = OSFuncs()


# all subclasses of File should implement as many file object methods as possible
class File(object):
	__metaclass__ = ABCMeta
	def __init__(self, mode):
		self.mode = mode
		self.isDestructed = False
	
	def __str__(self, message=None, extraPairDict=None):
		return self.__repr__(message=message, extraPairDict=extraPairDict)
	def __repr__(self, valueLabel=None, value=None, extraPairDict=None, message=None):
		if valueLabel == None:
			valuePairs = OrderedDict()
			valuePairs["getPath"] = "'" + self.getPath() + "'"
			valuePairs["mode"] = self.mode
			valuePairs["isWritable"] = self.isWritable()
			valuePairs["isClosed"] = self.isClosed()
			valuePairs["isDestructed"] = self.isDestructed
			if extraPairDict != None:
				valuePairs.update(extraPairDict)
		else:
			valuePairs = {valueLabel: value}
		str_ = ", ".join([name + "=" + str(value) for name, value in valuePairs.iteritems()])
		
		if message != None:
			str_ += message
		return str_
	
	def __enter__(self):
		self._createdOnOpen = False		# currently unused
		if not self.getPath().exists():
			self._createdOnOpen = True
#		print(repr(self))
		if self.isClosed():
			self.reopen()
		return self
	
	def __exit__(self, exc=None, value=None, tb=None):
		self.close()
	
	@abstractmethod
	def _getPath(self):		# should return subclass of FilePath
		pass
	def getPath(self):
		# this could potentially create undesired effects, such as setting the file modification date before flushing, since flushing will reset the modification time to the current time
#		if not self.isWritable():
#			raise Exception("Must close file before attempting to perform os.path or os equivalent operations")
		return self._getPath()
	
	def isWritable(self, ignoreClosedState=False):
		return (ignoreClosedState or not self.isClosed()) and \
			(self.mode.startswith("w") or self.mode.startswith("a") or self.mode.startswith("r+"))
	@abstractmethod
	def isClosed(self):
		pass
	
	def destruct(self):
		if not self.isClosed():
			self.close()
		self.isDestructed = True
	def reopen(self, mode=None):
		assert self.isClosed()
		if mode != None:
			self.mode = mode
		self._reopen()
	@abstractmethod
	def _reopen(self):
		pass


class PathAbstract(object):
	__metaclass__ = ABCMeta
	
	_allFileObjectTypes = []
	_allFilePathTypes = []
	_allFolderPathTypes = []
	@classmethod
	def _registerType(cls, fileObjectClass, filePathClass, folderPathClass):
		cls._allFileObjectTypes.append(fileObjectClass)
		cls._allFilePathTypes.append(filePathClass)
		cls._allFolderPathTypes.append(folderPathClass)
	
	def __init__(self, path):
		self.path = path
		assert isinstance(self.path, str) or isinstance(self.path, unicode)
	@abstractmethod
	def _makeFilePath(self, newPath):
		pass
	@abstractmethod
	def _makeFolderPath(self, newPath):
		pass
	def asStr(self):
		return self.path
	def __str__(self):
		return self.asStr()
	def __repr__(self, message=None):
		return self.path + (": " + message if message != None else "")
	
	def __add__(self, right):
		return self._addMaker(self.path + self._addMaker_getPath(right))
	def __radd__(self, left):
		return self._addMaker(self._addMaker_getPath(left) + self.path)
	
	def _addMaker_getPath(self, path):
		if isinstance(path, str) or isinstance(path, unicode):
			return path
		elif isinstance(path, PathAbstract):
			return path.path
		else:
			raise Exception("Cannot concatenate " + repr(path) + " to " + self)
	
	def _addMaker(self, newPath):
		if isinstance(self, FilePath):
			return self._makeFilePath(newPath)
		elif isinstance(self, FolderPath):
			return self._makeFolderPath(newPath)
	
	def __eq__(self, other):
		if not self.__class__ == other.__class__:
			return False
		if self.path == other.path or (self.exists() and other.exists() and self.samefile(other)):
			return True
		return False
	__ne__ = lambda self, other: not self.__eq__(other)
	def __hash__(self):
		return hash((self.__class__, self.path))
	
	@abstractmethod
	def _buildFunc(self, funcName, argParser):
		pass
	def __getattr__(self, name):
		if name in OSPathFuncs.ALL_FUNCS:
			argParser = OSPathFuncs
		elif name in OSFuncs.ALL_FUNCS:
			argParser = OSFuncs
		else:
			raise AttributeError
		return self._buildFunc(name, argParser)
	
	@classmethod
	def _getClassTypes(cls):
		if issubclass(cls, FilePath):
			index = cls._allFilePathTypes.index(cls)
		elif issubclass(cls, FolderPath):
			index = cls._allFolderPathTypes.index(cls)
		fileObjectClass = cls._allFileObjectTypes[index]
		filePathClass = cls._allFilePathTypes[index]
		folderPathClass = cls._allFolderPathTypes[index]
		return fileObjectClass, filePathClass, folderPathClass
	
	@classmethod
	def _argsConvert_input(cls, funcName, argParser, args):
		if funcName == "utime":
			if len(args) == 3:
				args = [args[0], (args[1], args[2])]
			elif len(args) != 2:
				raise Exception()
		
		allArgDesc = argParser.getArgTypes(funcName)
		fileObjectClass, filePathClass, folderPathClass = cls._getClassTypes()
		returnArgs = []
		
		for i in range(0, max([len(args),len(allArgDesc)])):
			if i > len(allArgDesc)-1:
				if ArgDescForPaths.MULTI in allArgDesc[-1]:
					argDesc = allArgDesc[len(allArgDesc)-1]
				else:
					argDesc = [ArgDescForPaths.OTHER]
			else:
				argDesc = allArgDesc[i]
			
			if ArgDescForPaths.OTHER in argDesc:
				returnArgs.insert(i, args[i])
			elif (ArgDescForPaths.FILE in argDesc and isinstance(args[i], filePathClass)) \
					or (ArgDescForPaths.FOLDER in argDesc and isinstance(args[i], folderPathClass)):
				returnArgs.insert(i, str(args[i]))
			elif ArgDescForPaths.FILE in argDesc and isinstance(args[i], fileObjectClass):
				returnArgs.insert(i, str(args[i]._getPath()))
			elif isinstance(args[i], str) or isinstance(args[i], unicode):
				returnArgs.insert(i, args[i])
			else:
				raise Exception("Could not convert argument " + str(i) + ", args=" + str(args))
		
		if funcName == "commonprefix" and len(returnArgs) > 1:
			returnArgs = [returnArgs]
		return returnArgs
	
	def _argsConvert_output(self, funcName, argParser, rawReturnValue, inputArgs):
		if funcName in argParser.RETURN_FILE:
			return self._makeFilePath(rawReturnValue)
		elif funcName in argParser.RETURN_FOLDER:
			return self._makeFolderPath(rawReturnValue)
		elif funcName in argParser.RETURN_SAME_AS_INPUT_TYPE:
			fileObjectClass, filePathClass, folderPathClass = self._getClassTypes()
			if isinstance(inputArgs[0], filePathClass):
				return self._makeFilePath(rawReturnValue)
			elif isinstance(inputArgs[0], folderPathClass):
				return self._makeFolderPath(rawReturnValue)
			else:
				raise Exception("Return value from os or os.path function can't be converted to a PathAbstract type because input argument type of function could not be determined")
		elif funcName in argParser.RETURN_OTHER:
			return rawReturnValue
		elif funcName in argParser.RETURN_SPECIAL:
			return self._argsConvert_output_special(funcName, argParser, rawReturnValue, inputArgs)
		else:
			raise Exception("Unknown return type for function - can't convert to a PathAbstract type")
	
	def _argsConvert_output_special(self, funcName, argParser, rawReturnValue, inputArgs):
		if funcName in ("join", "joinFile", "joinFolder"):
			if isinstance(inputArgs[-1], FolderPath):
				assert funcName in ("join", "joinFolder")
				return self._makeFolderPath(rawReturnValue)
			elif isinstance(inputArgs[-1], FilePath):
				assert funcName in ("join", "joinFile")
				return self._makeFilePath(rawReturnValue)
			elif isinstance(inputArgs[-1], str) or isinstance(inputArgs[-1], unicode):
				if funcName == "join":
					pathObj = self._makeFolderPath(rawReturnValue)
					if pathObj.isdir():
						return pathObj
					pathObj = self._makeFilePath(rawReturnValue)
					if pathObj.isfile():
						return pathObj
					raise Exception("Could not determine output type of join call. Specifically use FilePath or FolderPath as last argument in join call instead, or use the joinFile or joinFolder methods.")
				elif funcName == "joinFile":
					return self._makeFilePath(rawReturnValue)
				elif funcName == "joinFolder":
					return self._makeFolderPath(rawReturnValue)
			else:
				raise Exception("Type not supported")
		elif funcName == "splitext":
			fileObjectClass, filePathClass, folderPathClass = self._getClassTypes()
			assert isinstance(inputArgs[0], filePathClass)
			return (self._makeFilePath(rawReturnValue[0]), rawReturnValue[1])
		else:
			raise NotImplementedError("Function not yet implemented")


class FilePath(PathAbstract):
	def __init__(self, path):
		super(FilePath, self).__init__(path)
	@abstractmethod
	def asFile(self, mode="rb"):
		pass
	def create(self):
		# creates a 0 byte file
		if self.exists():
			return
		with self.asFile("wb"):
			pass
	
	def _storeData(self, destFileObj, shouldCopyDates, destFilePath):
		wasClosed = destFileObj.isClosed()
		if wasClosed:	destFileObj.reopen()
		else:			destFileObj.seek(0)
		
		temp = self.asFile("rb")
		temp.destruct()
		
		with self.asFile("rb") as sourceFileObj:
			shutil.copyfileobj(sourceFileObj, destFileObj, 1024*100)
		
		destFileObj.close()
#		print(self.__repr__("size right after copy/move:" + str(destFilePath.getsize())))
		if shouldCopyDates:
			self.copyDates(destFileObj.getPath())
		else:
			if not wasClosed and hasattr(destFileObj, "reopen"):
				destFileObj.reopen()
	
	def copyDates(self, destFilePath):
		destFilePath.utime(self.getatime(), self.getmtime())
	
	def copy(self, destFilePath, shouldCopyDates):
		if destFilePath.isdir():
			destFilePath = destFilePath.joinFile(str(self.basename()))
		destFileObj = self._preCopy_getFileObj(destFilePath, shouldCopyDates)
		self._storeData(destFileObj, shouldCopyDates, destFilePath)
	
	def _preCopy_getFileObj(self, destFilePath, shouldCopyDates):
		destFilePath.create()
		return destFilePath.asFile("w+b")
	
	def move(self, destFilePath):
		self.copy(destFilePath, True)
		self.remove()
	def rename(self, destFileName):
		newFilePath = self.dirname().joinFile(destFileName)
		self.move(newFilePath)
		return newFilePath


class FolderPath(PathAbstract):
	"""Abstract concept of a folder path."""
	def __init__(self, path, walkerClass):
		"""
		@param walkerClass	WalkerAbstract:	@see WalkerAbstract
		"""
		PathAbstract.__init__(self, path)
		self._walkerClass = walkerClass
	def copy(self, destFolderPath, shouldCopyDates=False):
		destFolderPath.create()
		for srcSubfolderPath in self.walk(isRecursive=False, wantFiles=False, wantFolders=True):
			srcSubfolderPath.copy(destFolderPath.joinFolder(str(srcSubfolderPath.basename())))
		for srcFilePath in self.walk(isRecursive=False, wantFiles=True, wantFolders=False):
			srcFilePath.copy(destFolderPath, shouldCopyDates)
	def create(self):
		"""Create directory if not exists"""
		if not self.exists():
			return self.mkdirs()
	@abstractmethod
	def rmtree(self):
		pass
	def remove(self, isRecursive=False):
		"""Remove folder and contents if it exists."""
		if self.exists():
			if not isRecursive:
				return self.rmdir()
			else:
				return self.rmtree()
	def mkdirs(self, *args, **kwargs):
		"""@see makedirs()"""
		return self.makedirs(*args, **kwargs)
	def walk(self, isRecursive, wantFiles, wantFolders, followSymlinks=True, nameGlob="*", topDown=True):
		"""@see WalkerAbstract.walk"""
		return self._walkerClass.walk(self, isRecursive, wantFiles, wantFolders, followSymlinks, nameGlob, topDown)

