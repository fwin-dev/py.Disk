from Disk.Test_Abstract import Test_FilePath, Test_FolderPath
import Disk.Local

import unittest

class Test_LocalFile_to_LocalFile(Test_FilePath.FilePathAbstract, unittest.TestCase):
	srcFilePath = Disk.Local.FilePath("/tmp/py0001.txt")
	destFilePath = Disk.Local.FilePath("/tmp/py0002.txt")

class Test_LocalFolder(Test_FolderPath.FolderPathAbstract, unittest.TestCase):
	srcFolderPath = Disk.Local.FolderPath("/tmp/py_test1/foo1")
	destFolderPath = Disk.Local.FolderPath("/tmp/py_test2/foo2")
	relFilePath = Disk.Local.FilePath("py0003.txt")
	relFolderPath = Disk.Local.FolderPath("folder")
	
	def test_rmtree(self):
		self.srcFolderPath.rmtree()
		self.assertTrue(not self.srcFolderPath.exists(), "Could not remove folder tree")
		self._createFolderPaths()
