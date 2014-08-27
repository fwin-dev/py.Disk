from __future__ import print_function

from _FuncDescriptors import ArgDescForPaths, PathFuncsAbstract

from Lang.Struct import OrderedDict
from abc import ABCMeta, abstractmethod
import os, shutil

# all subclasses of File should implement as many file object methods as possible
class File(object):
	__metaclass__ = ABCMeta
	def __init__(self, mode):
		self.mode = mode
		self.isDestructed = False
	
	def __str__(self, message=None, extraPairDict={}):
		return self.__repr__(message=message, extraPairDict=extraPairDict)
	def __repr__(self, valueLabel=None, value=None, extraPairDict={}, message=None):
		if valueLabel == None:
			valuePairs = OrderedDict()
			valuePairs["getPath"] = "'" + str(self.getPath()) + "'"
			valuePairs["mode"] = self.mode
			valuePairs["isWritable"] = self.isWritable()
			valuePairs["isClosed"] = self.isClosed()
			valuePairs["isDestructed"] = self.isDestructed
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
		if not isinstance(self.path, basestring):
			raise Exception("Incorrect type: " + str(type(self.path)) + ", instance passed='" + repr(self.path) + "'")
		if self.path == "":
			raise Exception("Invalid path: '' (empty string)")
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
		return self.join(right)
	def __radd__(self, left):
		return left.join(self)
	
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
	def _buildFunc(self, funcName, funcDescriptor):
		pass
	def __getattr__(self, name):
		return self._getattr(name)
	def _getattr(self, name):
		# had to add an extra layer of indirection here (extra getattr method) because of __getattr__ with super(...) limitation
		# http://stackoverflow.com/questions/12047847/super-object-not-calling-getattr
		funcDescriptor = PathFuncsAbstract.getDescriptorForFunc(name)
		if funcDescriptor == None:
			raise AttributeError(name)
		return self._buildFunc(name, funcDescriptor)
	
	@classmethod
	def _getClassTypes(cls, classType=None):
		if classType == None:
			classType = cls
		if issubclass(classType, FilePath):
			index = cls._allFilePathTypes.index(cls)
		elif issubclass(classType, FolderPath):
			index = cls._allFolderPathTypes.index(cls)
		fileObjectClass = cls._allFileObjectTypes[index]
		filePathClass = cls._allFilePathTypes[index]
		folderPathClass = cls._allFolderPathTypes[index]
		return fileObjectClass, filePathClass, folderPathClass
	
	@classmethod
	def _argsConvert_input(cls, funcName, funcDescriptor, args):
		if funcName == "utime":
			if len(args) == 3:
				args = [args[0], (args[1], args[2])]
			elif len(args) != 2:
				raise Exception()
		
		allArgDesc = funcDescriptor.getArgTypes(funcName)
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
			elif isinstance(args[i], basestring):
				returnArgs.insert(i, args[i])
			else:
				raise Exception("Could not convert argument " + str(i) + ", args=" + str(args))
		
		if funcName == "commonprefix" and len(returnArgs) > 1:
			returnArgs = [returnArgs]
		return returnArgs
	
	def _argsConvert_output(self, funcName, funcDescriptor, rawReturnValue, inputArgs):
		if funcName in funcDescriptor.RETURN_FILE:
			return self._makeFilePath(rawReturnValue)
		elif funcName in funcDescriptor.RETURN_FOLDER:
			return self._makeFolderPath(rawReturnValue)
		elif funcName in funcDescriptor.RETURN_SAME_AS_INPUT_TYPE:
			return self._argsConvert_output_sameAsInputType(inputArgs[0], rawReturnValue)
		elif funcName in funcDescriptor.RETURN_OTHER:
			return rawReturnValue
		elif funcName in funcDescriptor.RETURN_SPECIAL:
			return self._argsConvert_output_special(funcName, funcDescriptor, rawReturnValue, inputArgs)
		else:
			raise Exception("Unknown return type for function - can't convert to a PathAbstract type")
	
	def _argsConvert_output_sameAsInputType(self, inputArg, rawReturnValue):
		fileObjectClass, filePathClass, folderPathClass = self._getClassTypes()
		if isinstance(inputArg, filePathClass):
			return self._makeFilePath(rawReturnValue)
		elif isinstance(inputArg, folderPathClass):
			return self._makeFolderPath(rawReturnValue)
		else:
			raise Exception("Return value from os or os.path function can't be converted to a PathAbstract type because input argument type of function could not be determined")
	
	def _argsConvert_output_special(self, funcName, funcDescriptor, rawReturnValue, inputArgs):
		if funcName in ("join", "joinFile", "joinFolder"):
			return self._argsConvert_output_special_join(funcName, inputArgs, rawReturnValue)
		elif funcName == "splitext":
			fileObjectClass, filePathClass, folderPathClass = self._getClassTypes()
			assert isinstance(inputArgs[0], filePathClass)
			return (self._makeFilePath(rawReturnValue[0]), rawReturnValue[1])
		elif funcName == "split":
			dirname = self._makeFolderPath(rawReturnValue[0])
			basename = self._argsConvert_output_sameAsInputType(inputArgs[0], rawReturnValue[1])
			return (dirname, basename)
		else:
			raise NotImplementedError("Function not yet implemented")
	
	def _argsConvert_output_special_join(self, funcName, inputArgs, rawReturnValue):
		if isinstance(inputArgs[-1], FolderPath):
			assert funcName in ("join", "joinFolder")
			self._argsConvert_output_special_join_validation(inputArgs, "FolderPath")
			return self._makeFolderPath(rawReturnValue)
		elif isinstance(inputArgs[-1], FilePath):
			assert funcName in ("join", "joinFile")
			self._argsConvert_output_special_join_validation(inputArgs, "FilePath")
			for arg in inputArgs[0:-1]:
				if isinstance(arg, FilePath):
					raise Exception("Tried to join a FilePath on the left with a FilePath on the right")
			return self._makeFilePath(rawReturnValue)
		elif isinstance(inputArgs[-1], basestring):
			if funcName == "join":
				raise Exception("Could not determine output type of join call. Specifically use a FilePath or FolderPath instance as the last argument in the join call instead, or use the joinFile or joinFolder methods.")
			elif funcName == "joinFile":
				self._argsConvert_output_special_join_validation(inputArgs, "FilePath")
				return self._makeFilePath(rawReturnValue)
			elif funcName == "joinFolder":
				self._argsConvert_output_special_join_validation(inputArgs, "FolderPath")
				return self._makeFolderPath(rawReturnValue)
		else:
			raise Exception("Type not supported")
	
	def _argsConvert_output_special_join_validation(self, inputArgs, rightTypeStr):
		for arg in inputArgs[0:-1]:
			if isinstance(arg, FilePath):
				raise Exception("Tried to join a FilePath on the left with a " + rightTypeStr + " on the right")
	
	def splitAll(self):
		"""Splits a path into a list of components, with each component being either a filename or foldername. The only
		exception to this is the first component, which may be a drive letter or forward slash, signifying the root folder."""
		allParts_str = str(self).split(os.sep)
		if allParts_str[0] == "":
			allParts_str[0] = os.sep	# defines root folder
		if allParts_str[-1] == "":
			del allParts_str[-1]		# extra slash at the end
		allParts_pathInstance = []
		for part in allParts_str[:-1]:
			allParts_pathInstance.append(self._makeFolderPath(part))
		if isinstance(self, FilePath):
			allParts_pathInstance.append(self._makeFilePath(allParts_str[-1]))
		elif isinstance(self, FolderPath):
			allParts_pathInstance.append(self._makeFolderPath(allParts_str[-1]))
		else:
			raise Exception("Type not supported")
		return allParts_pathInstance

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
			shutil.copyfileobj(sourceFileObj, destFileObj, 1024*128)
		
		destFileObj.close()
#		print(self.__repr__("size right after copy/move:" + str(destFilePath.getsize())))
		if shouldCopyDates:
			self.copyDates(destFileObj.getPath())
		else:
			if not wasClosed and hasattr(destFileObj, "reopen"):
				destFileObj.reopen()
	
	def exists(self):
		return super(FilePath, self)._getattr("exists")() and self.isfile()
	def copyDates(self, destFilePath):
		destFilePath.utime(self.getatime(), self.getmtime())
	
	def copy(self, destPath, shouldCopyDates):
		if isinstance(destPath, FolderPath):
			destPath = destPath.joinFile(str(self.basename()))
		destFileObj = self._preCopy_getFileObj(destPath, shouldCopyDates)
		self._storeData(destFileObj, shouldCopyDates, destPath)
		assert self.getsize() == destPath.getsize()
	
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
	
	def mkdirs(self, *args, **kwargs):
		"""@see makedirs()"""
		return self.makedirs(*args, **kwargs)
	def makedirs(self, *args, **kwargs):
		return self.dirname().makedirs(*args, **kwargs)
	
	def isBinary(self):
		"""
		http://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python
		"""
		textchars = "".join(map(chr, [7,8,9,10,12,13,27] + range(0x20, 0x100)))
		with self.asFile("rb") as file_:
			isBinary = bool(file_.read(1024).translate(None, textchars))
		return isBinary


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
	def exists(self):
		return super(FolderPath, self)._getattr("exists")() and self.isdir()
	def create(self):
		"""Create directory if not exists"""
		if not self.exists():
			return self.mkdirs()
	def remove(self, isRecursive=False):
		"""Remove folder and contents if it exists."""
		if self.exists():
			if not isRecursive:
				return self.rmdir()
			else:
				return self.rmtree()
	def rmdirs(self, *args, **kwargs):
		if self.exists():
			return self.rmtree(*args, **kwargs)
	
	def mkdir(self, *args, **kwargs):
		if not self.exists():
			return super(FolderPath, self)._getattr("mkdir")(*args, **kwargs)
		return None
	def makedir(self, *args, **kwargs):
		"""@see mkdir(...)"""
		return self.mkdir(*args, **kwargs)
	def mkdirs(self, *args, **kwargs):
		"""@see makedirs(...)"""
		return self.makedirs(*args, **kwargs)
	def makedirs(self, *args, **kwargs):
		if not self.exists():
			return super(FolderPath, self)._getattr("makedirs")(*args, **kwargs)
		return None
	
	def walk(self, isRecursive, wantFiles, wantFolders, followSymlinks=True, nameGlob="*", topDown=True):
		"""@see WalkerAbstract.walk"""
		return self._walkerClass.walk(self, isRecursive, wantFiles, wantFolders, followSymlinks, nameGlob, topDown)
