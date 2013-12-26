import time
from abc import ABCMeta, abstractproperty

class FilePathAbstract:
	__metaclass__ = ABCMeta
	
	@abstractproperty
	def srcFilePath(self):
		"""Must not already exist. This file path will be used to copy data from, in order to test `destFilePath`."""
		pass
	@abstractproperty
	def destFilePath(self):
		"""Must not already exist. This will be the primary class (`Disk.AbstractFilePath` instance) to be tested."""
		pass
	
	def setUp(self):
		super(FilePathAbstract, self).setUp()
		if self.srcFilePath.exists():
			self.srcFilePath.remove()
		self._writeSrcFile()
		if self.destFilePath.exists():
			self.destFilePath.remove()
	def _writeSrcFile(self):
		with self.srcFilePath.asFile("w") as srcFile:
			srcFile.write("abcdef\nghijkl\n")
		print(self.srcFilePath.getmtime())
		assert self.srcFilePath.exists() and self.srcFilePath.getsize() > 0
		if self.srcFilePath.getmtime() != int(self.srcFilePath.getmtime()):
			print("WARNING: Your OS does not support fractional time precision on files")
	def tearDown(self):
		super(FilePathAbstract, self).tearDown()
		if self.destFilePath.exists():
			self.destFilePath.remove()
			self.assertTrue(not self.destFilePath.exists(), "Failed to remove destination file")
		if self.srcFilePath.exists():
			self.srcFilePath.remove()
			self.assertTrue(not self.srcFilePath.exists(), "Failed to remove source file")
	
	def test_toStr(self):
		self.assertEqual(str(self.srcFilePath), "/tmp/py0001.txt")
	
	def test_add(self):
		with self.assertRaises(Exception):
			print(self.srcFilePath + self.destFilePath)
	
	def test_splitAll(self):
		paths = ("bar.txt", "/foo/bar.txt")
		paths = [self.srcFilePath._makeFilePath(path) for path in paths]
		correctSplits = ([self.srcFilePath._makeFilePath("bar.txt")],
						 [self.srcFilePath._makeFolderPath("/"), self.srcFilePath._makeFolderPath("foo"), self.srcFilePath._makeFilePath("bar.txt")]
						)
		for path, correctSplit in zip(paths, correctSplits):
			pathParts = path.splitAll()
			self.assertEqual(pathParts, correctSplit)
	
	def test_copy_withModifiedDate(self):
		assert self.srcFilePath.exists() and self.srcFilePath.getsize() > 0
		self.srcFilePath.copy(self.destFilePath, shouldCopyDates=True)
		self.assertTrue(self.srcFilePath.exists() and self.srcFilePath.getsize() > 0, "Source file was modified on a copy operation!!")
		self.assertEqual(self.srcFilePath.getsize(), self.destFilePath.getsize(), "Source file contents were not entirely copied to the destination file")
		self.assertEqual(self.srcFilePath.getmtime(), self.destFilePath.getmtime(), "Source file 'last modified' timestamp was not copied correctly to the destination file, or filesystems do not support the same precision")
	
	def test_copy_noModifiedDate(self):
		assert self.srcFilePath.exists() and self.srcFilePath.getsize() > 0
		time.sleep(1)	# make sure not to create destFile too quickly, in order to differentiate timestamps
		self.srcFilePath.copy(self.destFilePath, shouldCopyDates=False)
		self.assertTrue(self.srcFilePath.exists() and self.srcFilePath.getsize() > 0, "Source file was modified on a copy operation!!")
		self.assertEqual(self.srcFilePath.getsize(), self.destFilePath.getsize(), "Source file contents were not entirely copied to the destination file")
		self.assertNotEqual(self.srcFilePath.getmtime(), self.destFilePath.getmtime(), "Source file 'last modified' timestamp was not copied correctly to the destination file, or filesystems do not support the same precision")
	
	def test_move(self):
		assert self.srcFilePath.exists() and self.srcFilePath.getsize() > 0
		self.srcFilePath.move(self.destFilePath)
		self.assertTrue(not self.srcFilePath.exists(), "Failed to remove source file")
		self.assertTrue(self.destFilePath.getsize() > 0, "Destination file contents were not entirely moved from the source file")
