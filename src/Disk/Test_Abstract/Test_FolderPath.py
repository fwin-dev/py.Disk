import Disk._base

from abc import ABCMeta, abstractproperty

class FolderPathAbstract:
	__metaclass__ = ABCMeta
	
	@abstractproperty
	def srcFolderPath(self):
		"""
		This file path will be used to copy data from, in order to test `destFilePath`.
		
		Must not already exist. 
		"""
		pass
	@abstractproperty
	def destFolderPath(self):
		"""
		This will be the primary class (`Disk.AbstractFolderPath` subclass instance) to be tested.
		
		Must not already exist.
		"""
		pass
	@abstractproperty
	def relFilePath(self):
		"""A relative FilePath instance, only for testing interaction of the FolderPath instance with a FilePath instance."""
		pass
	@abstractproperty
	def relFolderPath(self):
		"""A relative FolderPath instance, only for testing interaction of the FolderPath instance with a FilePath instance."""
		pass
	
	def _createFolderPaths(self):
		if not self.srcFolderPath.exists():
			self.srcFolderPath.mkdirs()
		if not self.destFolderPath:
			self.destFolderPath.mkdirs()
	def setUp(self):
		super(FolderPathAbstract, self).setUp()
		assert not self.srcFolderPath.exists()
		assert not self.destFolderPath.exists()
		assert not self.srcFolderPath.joinFile(self.relFilePath).exists()
		assert not self.destFolderPath.joinFile(self.relFilePath).exists()
		self._createFolderPaths()
	def tearDown(self):
		super(FolderPathAbstract, self).tearDown()
		if self.srcFolderPath.exists():
			self.srcFolderPath.remove()
		if self.destFolderPath.exists():
			self.destFolderPath.remove()
	
	def test_join_folderWithRelFile(self):
		fullPath_usingJoin = self.srcFolderPath.join(self.relFilePath)
		self.assertIsInstance(fullPath_usingJoin, Disk._base.FilePath)
		self.assertIsInstance(self.srcFolderPath + self.relFilePath, Disk._base.FilePath)
		self.assertEqual(fullPath_usingJoin, self.srcFolderPath + self.relFilePath)
	
	def test_join_folderWithRelFolder(self):
		fullPath_usingJoin = self.srcFolderPath.join(self.relFolderPath)
		self.assertIsInstance(fullPath_usingJoin, Disk._base.FolderPath)
		self.assertIsInstance(self.srcFolderPath + self.relFolderPath, Disk._base.FolderPath)
		self.assertEqual(fullPath_usingJoin, self.srcFolderPath + self.relFolderPath)
	
	def test_splitAll(self):
		paths = ("/foo/bar", "foo/bar", "foo")
		paths = [self.srcFolderPath._makeFolderPath(path) for path in paths]
		correctSplits = ([self.srcFolderPath._makeFolderPath("/"), self.srcFolderPath._makeFolderPath("foo"), self.srcFolderPath._makeFolderPath("bar")],
						 [self.srcFolderPath._makeFolderPath("foo"), self.srcFolderPath._makeFolderPath("bar")],
						 [self.srcFolderPath._makeFolderPath("foo")]
						)
		for path, correctSplit in zip(paths, correctSplits):
			pathParts = path.splitAll()
			self.assertEqual(pathParts, correctSplit)
	
# 	def test_join_folderWithFullFolder(self):
# 		# This should be an invalid operation, but there's no good way to check if a path is relative or absolute
# 		with self.assertRaises(Exception):
# 			fullPath_usingJoin = self.srcFolderPath.join(self.destFolderPath)
# 			print(type(fullPath_usingJoin))
# 		
# 		with self.assertRaises(Exception):
# 			fullPath_usingJoin = self.srcFolderPath + self.destFolderPath
# 			print(type(fullPath_usingJoin))
# 	
# 	def test_join_folderWithFullFile(self):
# 		# This should be an invalid operation, but there's no good way to check if a path is relative or absolute
# 		with self.assertRaises(Exception):
# 			fullPath_usingJoin = self.srcFolderPath.join(self.destFolderPath)
# 			print(type(fullPath_usingJoin))
# 		
# 		with self.assertRaises(Exception):
# 			fullPath_usingJoin = self.srcFolderPath + self.destFolderPath
# 			print(type(fullPath_usingJoin))

