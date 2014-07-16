from Lang.FuncTools.Abstraction import abstractmethod

import os.path
import os

class FuncDesc:
	LOCAL = 2
	REMOTE = 3

class ArgDesc:
	SINGLE = 0
	MULTI = 1

class Descriptor(object):
	@classmethod
	@abstractmethod
	def isLocal(cls, funcName):
		pass
	@classmethod
	@abstractmethod
	def getArgTypes(cls, funcName):
		pass
	@classmethod
	@abstractmethod
	def getBuiltinFuncReference(cls, funcName, asStr=False):
		pass

class ArgDescForPaths(ArgDesc):
	OTHER = 4
	FILE = 5
	FOLDER = 6

class PathFuncsAbstract(Descriptor):
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
	
	@classmethod
	def getBuiltinFuncReference(cls, module, moduleName, funcName, asStr=False):
		"""
		@return tuple: Index 0 is either the module itself if asStr=False or the module name (with package name) as a string if asStr=True. Similarly, index 1 is the function itself if asStr=False or the function name if asStr=True.
		"""
		if not asStr:
			return module, getattr(module, funcName)
		else:
			assert hasattr(module, funcName)
			return moduleName, funcName


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
	def getBuiltinFuncReference(cls, funcName, asStr=False):
		if funcName in ("joinFile", "joinFolder"):
			funcName = "join"
		return super(OSPathFuncs, cls).getBuiltinFuncReference(os.path, "os.path", funcName=funcName, asStr=asStr)
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
	def getBuiltinFuncReference(cls, funcName, asStr=False):
		return super(OSFuncs, cls).getBuiltinFuncReference(os, "os", funcName=funcName, asStr=asStr)
OSFuncs = OSFuncs()
