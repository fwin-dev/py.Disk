from Lang.FuncTools.Abstraction import abstractmethod

import os.path
from fnmatch import fnmatchcase

class WalkerAbstract:
	"""Gets a list of files and/or folders in a folder."""
	allWalkers = {}
	def __init__(self, folderClass):
		self.allWalkers[folderClass] = self.__class__
	
	@classmethod
	@abstractmethod
	def _getOSwalkResults(cls, folder, topDown, followSymlinks):
		pass
	
	@classmethod
	def _registerType(cls, walkerType, folderPathType):
		cls.allWalkers[folderPathType] = walkerType
	
	@classmethod
	def _checkReadAccess(cls, folder):
		try:
			if not folder.access(os.R_OK):
				raise Exception("Permission denied while reading folder: '" + str(folder) + "'")
		except NotImplementedError:		# some Disk library implementations can't handle os.access method (py.Disk.FTP)
			pass
	
	@classmethod
	def walk(cls, rootFolder, isRecursive, wantFiles, wantFolders, followSymlinks=False, nameGlob="*", topDown=True):
		"""
		Gets a list of files and/or folders in a folder.
		
		@wantFiles		bool:	If True, files in the root folder will be included in the results.
		@wantFolders	bool:	If True, subfolders in the root folder will be included in the results.
		@followSymlinks	bool:	If True, symlinks are followed to where their pointers point.
		@nameGlob		bool:	Same as a path glob in bash
		@topDown		bool:	If True, returns results scanning rootFolder from top to bottom.
		"""
		walkerClass = cls.allWalkers[rootFolder.__class__]
		if not rootFolder.exists():
			raise Exception("Folder to walk does not exist: '" + str(rootFolder) + "'")
		cls._checkReadAccess(rootFolder)
		rootFolder = rootFolder.abspath()
		results = []
		
		if not hasattr(nameGlob, "__iter__"):
			nameGlob = [nameGlob]
		
		foundRoot = False
		for currentRoot, currentFolders, currentFiles in walkerClass._getOSwalkResults(rootFolder, topDown, followSymlinks):
			if not isRecursive:
				if foundRoot:
					break
				if currentRoot == str(rootFolder):
					foundRoot = True
				else:
					continue
			
			if wantFolders:
				for currentFolder in currentFolders:
					if nameGlob == "*" or any([fnmatchcase(currentFolder, singleNameGlob) for singleNameGlob in nameGlob]):
						currentFolder = rootFolder._makeFolderPath(os.path.join(currentRoot, currentFolder))
						if isRecursive:
							cls._checkReadAccess(currentFolder)
						results.append(currentFolder)
			if wantFiles:
				for currentFile in currentFiles:
					if nameGlob == "*" or any([fnmatchcase(currentFile, singleNameGlob) for singleNameGlob in nameGlob]):
						results.append(rootFolder._makeFilePath(os.path.join(currentRoot, currentFile)))
		return results

walk = WalkerAbstract.walk
