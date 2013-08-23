from abc import ABCMeta, abstractproperty

class WalkerAbstract:
	__metaclass__ = ABCMeta
	
	@abstractproperty
	def folderPath(self):
		"""Must not already exist"""
		pass
	
	def setUp(self):
		super(WalkerAbstract, self).setUp()
		assert not self.folderPath.exists()
		self.folderPath.mkdir()
	def tearDown(self):
		super(WalkerAbstract, self).tearDown()
		self.folderPath.remove(isRecursive=True)
	
	def _createTempFiles(self, folderPath, prefix=""):
		folderPath.create()
		filesMade = []
		for i in range(0, 4):
			filePath = folderPath.joinFile(prefix + str(i) + ".txt")
			filePath.create()
			filesMade.append(filePath)
		return filesMade
	
	def test_folderNotExists(self):
		folder = self.folderPath.joinFolder("sub_folder")
		self.assertRaises(Exception, folder.walk, wantFiles=True, wantFolders=True, isRecursive=False)
	
	def test_walk_folder_noRecurse_wantFiles(self):
		self._test_walk_folder_noRecurse_wantFiles(topDown=False)
	def test_walk_folder_noRecurse_wantFiles_topDown(self):
		self._test_walk_folder_noRecurse_wantFiles(topDown=True)
	def _test_walk_folder_noRecurse_wantFiles(self, **walkParams):
		parentFolder = self.folderPath
		subFolder = parentFolder.joinFolder("sub_folder")
		parentFilesMade = self._createTempFiles(parentFolder)
		subFolderFilesMade = self._createTempFiles(subFolder, "sub")
		results = [i for i in parentFolder.walk(wantFiles=True, wantFolders=False, isRecursive=False, **walkParams)]
		self.assert_(set(parentFilesMade) == set(results), str(parentFilesMade) + "\n" + str(results))
		parentFolder.remove(isRecursive=True)
	
	def test_walk_folder_recurse_wantFiles(self):
		self._test_walk_folder_recurse_wantFiles(topDown=False)
	def test_walk_folder_recurse_wantFiles_topDown(self):
		self._test_walk_folder_recurse_wantFiles(topDown=True)
	def _test_walk_folder_recurse_wantFiles(self, **walkParams):
		parentFolder = self.folderPath
		subFolder = parentFolder.joinFolder("sub_folder")
		filesMade = self._createTempFiles(parentFolder)
		filesMade += self._createTempFiles(subFolder, "sub")
		results = [i for i in parentFolder.walk(wantFiles=True, wantFolders=False, isRecursive=True, **walkParams)]
		self.assert_(set(filesMade) == set(results), str(filesMade) + "\n" + str(results))
		parentFolder.remove(isRecursive=True)
	
	def test_walk_folder_noRecurse_wantFolders(self):
		self._test_walk_folder_noRecurse_wantFolders(topDown=False)
	def test_walk_folder_noRecurse_wantFolders_topDown(self):
		self._test_walk_folder_noRecurse_wantFolders(topDown=True)
	def _test_walk_folder_noRecurse_wantFolders(self, **walkParams):
		parentFolder = self.folderPath
		subFolder = parentFolder.joinFolder("sub_folder")
		self._createTempFiles(parentFolder)
		self._createTempFiles(subFolder, "sub")
		results = [i for i in parentFolder.walk(wantFiles=False, wantFolders=True, isRecursive=False, **walkParams)]
		self.assert_(set([subFolder]) == set(results), str(subFolder) + "\n" + str(results))
	
	def test_walk_folder_recurse_wantFolders(self):
		self._test_walk_folder_noRecurse_wantFiles(topDown=False)
	def test_walk_folder_recurse_wantFolders_topDown(self):
		self._test_walk_folder_noRecurse_wantFiles(topDown=True)
	def _test_walk_folder_recurse_wantFolders(self, **walkParams):
		parentFolder = self.folderPath
		subFolder = parentFolder.joinFolder("sub_folder")
		subSubFolder = subFolder.joinFolder("sub_sub_folder")
		self._createTempFiles(parentFolder)
		self._createTempFiles(subFolder, "sub")
		self._createTempFiles(subSubFolder, "subsub")
		results = [i for i in parentFolder.walk(wantFiles=False, wantFolders=True, isRecursive=True, **walkParams)]
		self.assert_(set([subFolder, subSubFolder]) == set(results), str([subFolder, subSubFolder]) + "\n" + str(results))
