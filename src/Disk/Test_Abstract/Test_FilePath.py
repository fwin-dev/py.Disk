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
		print("writing file")
		self._writeSrcFile()
		assert not self.destFilePath.exists()
	def _writeSrcFile(self):
		assert not self.srcFilePath.exists()
		with self.srcFilePath.asFile("w") as srcFile:
			srcFile.write("abcdef\nghijkl\n")
		assert self.srcFilePath.exists() and self.srcFilePath.getsize() > 0
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
	
	def test_copy_withModifiedDate(self):
		assert self.srcFilePath.exists() and self.srcFilePath.getsize() > 0
		self.srcFilePath.copy(self.destFilePath, shouldCopyDates=True)
		self.assertTrue(self.srcFilePath.exists() and self.srcFilePath.getsize() > 0, "Source file was modified on a copy operation!!")
		self.assertEqual(self.srcFilePath.getsize(), self.destFilePath.getsize(), "Source file contents were not entirely copied to the destination file")
		
		# python 3.3 adds support for nanosecond precision, but < 3.3 only guarantees second precision
		self.assertEqual(int(self.srcFilePath.getmtime()), int(self.destFilePath.getmtime()), "Source file 'last modified' timestamp was not copied correctly to the destination file")
	
	def test_copy_noModifiedDate(self):
		assert self.srcFilePath.exists() and self.srcFilePath.getsize() > 0
		time.sleep(1)	# make sure not to create destFile too quickly, in order to differentiate timestamps
		self.srcFilePath.copy(self.destFilePath, shouldCopyDates=False)
		self.assertTrue(self.srcFilePath.exists() and self.srcFilePath.getsize() > 0, "Source file was modified on a copy operation!!")
		self.assertEqual(self.srcFilePath.getsize(), self.destFilePath.getsize(), "Source file contents were not entirely copied to the destination file")
		
		# python 3.3 adds support for nanosecond precision, but < 3.3 only guarantees second precision
		self.assertNotEqual(int(self.srcFilePath.getmtime()), int(self.destFilePath.getmtime()), "Source file 'last modified' timestamp was not copied correctly to the destination file")
	
	def test_move(self):
		assert self.srcFilePath.exists() and self.srcFilePath.getsize() > 0
		self.srcFilePath.move(self.destFilePath)
		self.assertTrue(not self.srcFilePath.exists(), "Failed to remove source file")
		self.assertTrue(self.destFilePath.getsize() > 0, "Destination file contents were not entirely moved from the source file")

