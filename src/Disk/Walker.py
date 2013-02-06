from Lang import abstractmethod

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
		assert rootFolder.exists()
		rootFolder = rootFolder.abspath()
		results = []
		
		if not hasattr(nameGlob, "__iter__"):
			nameGlob = [nameGlob]
		
		for currentRoot, currentFolders, currentFiles in walkerClass._getOSwalkResults(rootFolder, topDown, followSymlinks):
			if not isRecursive and currentRoot != str(rootFolder):
				break
			if wantFolders:
				for currentFolder in currentFolders:
					if wantFiles or any([fnmatchcase(currentFolder, singleNameGlob) for singleNameGlob in nameGlob]):
						results.append(rootFolder._makeFolderPath(os.path.join(currentRoot, currentFolder)))
			if wantFiles:
				for currentFile in currentFiles:
					if any([fnmatchcase(currentFile, singleNameGlob) for singleNameGlob in nameGlob]):
						results.append(rootFolder._makeFilePath(os.path.join(currentRoot, currentFile)))
		return results

walk = WalkerAbstract.walk
