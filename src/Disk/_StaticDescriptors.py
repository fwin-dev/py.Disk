from Lang.FuncTools.Abstraction import abstractmethod

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
	def getBuiltinFunction(cls, funcName, asStr=False):
		pass
